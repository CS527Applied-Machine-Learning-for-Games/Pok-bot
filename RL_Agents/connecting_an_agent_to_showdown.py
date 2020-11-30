# -*- coding: utf-8 -*-
import asyncio
from collections import namedtuple
from poke_env.player.random_player import RandomPlayer
from poke_env.player_configuration import PlayerConfiguration
from poke_env.server_configuration import ShowdownServerConfiguration

ServerConfiguration = namedtuple(
    "ServerConfiguration", ["server_url", "authentication_url"]
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

async def main():
    # We create a random player
    player = MaxDamagePlayer(
        player_configuration=PlayerConfiguration("USCPokebot", "uscpokebot"),
        server_configuration= ServerConfiguration(
    "sim.smogon.com:8000", "https://play.pokemonshowdown.com/action.php?"
),
    )

    # Sending challenges to 'your_username'
    #await player.send_challenges("your_username", n_challenges=1)

    # Accepting one challenge from any user
    # await player.accept_challenges(None, 1)

    # Accepting three challenges from 'your_username'
    # await player.accept_challenges('your_username', 3)

    # Playing 5 games on the ladder
    await player.ladder(5)

    # Print the rating of the player and its opponent after each battle
    # for battle in player.battles.values():
    #     print(battle.rating, battle.opponent_rating)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
