import numpy as np
import tensorflow as tf
import asyncio
from collections import namedtuple
from poke_env.player_configuration import PlayerConfiguration
from poke_env.server_configuration import ShowdownServerConfiguration
from poke_env.player.env_player import Gen8EnvSinglePlayer
from poke_env.player.random_player import RandomPlayer
from poke_env.player.player import Player
from rl.agents.dqn import DQNAgent
from rl.policy import LinearAnnealedPolicy, EpsGreedyQPolicy
from rl.memory import SequentialMemory
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam

ServerConfiguration = namedtuple(
    "ServerConfiguration", ["server_url", "authentication_url"]
)

# We define our RL player
# It needs a state embedder and a reward computer, hence these two methods
class SimpleRLPlayer(Gen8EnvSinglePlayer):
    def embed_battle(self, battle):
        # -1 indicates that the move does not have a base power
        # or is not available
        moves_base_power = -np.ones(4)
        moves_dmg_multiplier = np.ones(4)
        for i, move in enumerate(battle.available_moves):
            moves_base_power[i] = (
                move.base_power / 100
            )  # Simple rescaling to facilitate learning
            if move.type:
                moves_dmg_multiplier[i] = move.type.damage_multiplier(
                    battle.opponent_active_pokemon.type_1,
                    battle.opponent_active_pokemon.type_2,
                )

        # We count how many pokemons have not fainted in each team
        remaining_mon_team = (
            len([mon for mon in battle.team.values() if mon.fainted]) / 6
        )
        remaining_mon_opponent = (
            len([mon for mon in battle.opponent_team.values() if mon.fainted]) / 6
        )
        #print('Player: status',[mon for mon in battle.side_conditions])

        # We count how many pokemons side conditions in each team
        remaining_status_team = (
            len([mon for mon in battle.side_conditions]) / 6
        )
        remaining_status_opponent = (
            len([mon for mon in battle.opponent_side_conditions]) / 6
        )


        # Final vector with 10 components
        return np.concatenate(
            [
                moves_base_power,
                moves_dmg_multiplier,
                [remaining_mon_team, remaining_mon_opponent],
                [remaining_status_team, remaining_status_opponent],
            ]
        )

    def compute_reward(self, battle) -> float:
        return self.reward_computing_helper(
            battle, fainted_value=2, hp_value=1, status_value= 0.75, victory_value=30
        )



class MaxDamagePlayer(RandomPlayer):
    def choose_move(self, battle):
        # If the player can attack, it will
        if battle.available_moves:
            # Finds the best move among available ones
            best_move = max(battle.available_moves, key=lambda move: move.base_power)
            return self.create_order(best_move)

        # If no attack is available, a random switch will be made
        else:
            return self.choose_random_move(battle)


NB_TRAINING_STEPS = 30000
NB_EVALUATION_EPISODES = 100

tf.random.set_seed(0)
np.random.seed(0)

# This is the function that will be used to train the dqn
def dqn_training(player, dqn, nb_steps):
    dqn.fit(player, nb_steps=nb_steps)
    player.complete_current_battle()


def dqn_evaluation(player, dqn, nb_episodes):
    # Reset battle statistics
    player.reset_battles()
    dqn.test(player, nb_episodes=nb_episodes, visualize=False, verbose=False)

    print(
        "DQN Evaluation: %d victories out of %d episodes"
        % (player.n_won_battles, nb_episodes)
    )


async def main():
    env_player = SimpleRLPlayer(
    server_configuration= ServerConfiguration("localhost:8000",
    "https://play.pokemonshowdown.com/action.php?"),)

    #opponent = RandomPlayer(player_configuration=PlayerConfiguration("USCPokebot", "uscpokebot"),
    #server_configuration= ServerConfiguration("localhost:8000",
    #"https://play.pokemonshowdown.com/action.php?"),)
    #second_opponent = MaxDamagePlayer(battle_format="gen8randombattle")

    # Output dimension
    n_action = len(env_player.action_space)

    model = Sequential()
    model.add(Dense(128, activation="elu", input_shape=(1, 12)))

    # Our embedding have shape (1, 10), which affects our hidden layer
    # dimension and output dimension
    # Flattening resolve potential issues that would arise otherwise
    model.add(Flatten())
    model.add(Dense(128, activation="elu"))
    model.add(Dense(128, activation="elu"))
    model.add(Dense(64, activation="elu"))
    model.add(Dense(n_action, activation="linear"))

    memory = SequentialMemory(limit=10000, window_length=1)

    # Ssimple epsilon greedy
    policy = LinearAnnealedPolicy(
        EpsGreedyQPolicy(),
        attr="eps",
        value_max=1.0,
        value_min=0.05,
        value_test=0,
        nb_steps=10000,
    )
    loaded_model = tf.keras.models.load_model('model_30000')
    loaded_model.load_weights('weights_DQN_30000.h5')
    # Defining our DQN
    dqn = DQNAgent(
        model=loaded_model,
        nb_actions=len(env_player.action_space),
        policy=policy,
        memory=memory,
        nb_steps_warmup=1000,
        gamma=0.5,
        target_model_update=1,
        delta_clip=0.01,
        enable_double_dqn=True,
    )

    dqn.compile(Adam(lr=0.00025), metrics=["mae"])


    #model.load_weights('weights_DQN.h5')
    # Evaluation
    class EmbeddedRLPlayer(Player):
      def choose_move(self, battle):
        if np.random.rand() < 0.01:  # avoids infinite loops
            return self.choose_random_move(battle)
        embedding = SimpleRLPlayer.embed_battle(self, battle)
        action = dqn.forward(embedding)
        return SimpleRLPlayer._action_to_move(self, action, battle)
    #player_configuration=PlayerConfiguration("USCPokebot", "uscpokebot"),
    emb_player = EmbeddedRLPlayer(
    player_configuration=PlayerConfiguration("CSCI527Bot", "CSCI527Bot"),
    server_configuration= ServerConfiguration(
    "sim.smogon.com:8000", "https://play.pokemonshowdown.com/action.php?"
      ),)
    await emb_player.ladder(50)



if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
