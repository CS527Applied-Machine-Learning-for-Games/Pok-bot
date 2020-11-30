# -*- coding: utf-8 -*-
import numpy as np
import tensorflow as tf
import pandas as pd
import json
import random

from poke_env.player.env_player import Gen8EnvSinglePlayer
from poke_env.player.random_player import RandomPlayer

from poke_env.player_configuration import PlayerConfiguration
from poke_env.player.random_player import RandomPlayer
from poke_env.server_configuration import LocalhostServerConfiguration
​
from rl.agents.cem import CEMAgent
from rl.policy import LinearAnnealedPolicy, EpsGreedyQPolicy
from rl.memory import SequentialMemory, EpisodeParameterMemory
from tensorflow.keras.layers import Dense, Flatten, Activation
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam



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
            battle, fainted_value=2, hp_value=1, status_value= 10, victory_value=30
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

​
​
​
NB_TRAINING_STEPS = 30000
NB_EVALUATION_EPISODES = 100
​

TRAINING_OPPONENT = 'RandomPlayer'
FROZEN_RL_PRESENT = False
​
tf.random.set_seed(0)
np.random.seed(0)
​
​
# This is the function that will be used to train the agent
def agent_training(player, agent, nb_steps, filename):
    model = agent.fit(player, nb_steps=nb_steps)
    # save model history to csv
    save_file = f"{filename}_trainlog_{nb_steps}eps.csv"
    print("===============================================")
    print(f"Saving model history as {save_file}")
    print("===============================================")
    pd.DataFrame(model.history).to_csv(save_file)
    player.complete_current_battle()
​
​
def agent_evaluation(player, agent, nb_episodes, filename):
    # Reset battle statistics
    player.reset_battles()
    model = agent.test(player, nb_episodes=nb_episodes, visualize=False, verbose=False)
​
    # save model history to csv
    save_file = f"{filename}_testlog_{nb_episodes}eps.csv"
    print("===============================================")
    print(f"Saving model history as {save_file}")
    print("===============================================")
    pd.DataFrame(model.history).to_csv(save_file)

    print(
          "CEM Evaluation: %d victories out of %d episodes"
          % (player.n_won_battles, nb_episodes)
          )
​

if __name__ == "__main__":
    env_player = SimpleRLPlayer(
        player_configuration=PlayerConfiguration("CEM_RL_Player"),
        battle_format="gen8randombattle",
        server_configuration=LocalhostServerConfiguration,
    )
​
    random_opponent = RandomPlayer(
        player_configuration=PlayerConfiguration("RandomPlayer"),
        battle_format="gen8randombattle",
        server_configuration=LocalhostServerConfiguration,
    )
​
    maxdamage_opponent = MaxDamagePlayer(
        player_configuration=PlayerConfiguration("MaxDamagePlayer"),
        battle_format="gen8randombattle",
        server_configuration=LocalhostServerConfiguration,
    )

    n_action = len(env_player.action_space)
​
    memory = EpisodeParameterMemory(limit=10000, window_length=1)
    model = Sequential()
    model.add(Flatten(input_shape=(1, 10)))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(n_action))
    model.add(Activation('softmax'))
​

    agent = CEMAgent(model=model, nb_actions=n_action, memory=memory,
                   batch_size=50, nb_steps_warmup=1000, train_interval=50, elite_frac=0.05, noise_ampl=4)

​
    agent.compile()
​
    # Training
    env_player.play_against(
        env_algorithm=agent_training,
        opponent=random_opponent,
                            env_algorithm_kwargs={"agent": agent, "nb_steps": NB_TRAINING_STEPS, "filename": TRAINING_OPPONENT},
    )
    model.save("model_%d" % NB_TRAINING_STEPS)
​
    # Evaluation
    print("Results against random player:")
    env_player.play_against(
        env_algorithm=agent_evaluation,
        opponent=random_opponent,
        env_algorithm_kwargs={"agent": agent, "nb_episodes": NB_EVALUATION_EPISODES, "filename": f'({TRAINING_OPPONENT}_{NB_TRAINING_STEPS})RandomPlayer'},
    )
​
    print("\nResults against max player:")
    env_player.play_against(
        env_algorithm=agent_evaluation,
        opponent=maxdamage_opponent,
        env_algorithm_kwargs={"agent": agent, "nb_episodes": NB_EVALUATION_EPISODES, "filename": f'({TRAINING_OPPONENT}_{NB_TRAINING_STEPS})MaxPlayer'},
    )
