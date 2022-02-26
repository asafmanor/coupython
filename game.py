from __future__ import annotations

import logging
import random
import sys
from typing import Dict, Sequence

import numpy as np

from action import Action, CounterAction, check_legal_action
from cards import CardList
from deck import Deck
from player import Player
from random_player import RandomPlayer

logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout, level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
)

random.seed(0)


class Game:
    def __init__(self, players: Sequence[Player]):

        logger.info(f"Game is set up with {players}")
        self.players = players
        self.deck = Deck()
        self.discard_pile = CardList()
        self.n = 0

    @property
    def state(self) -> Dict:
        # TODO: need to be a state per player.
        # + Add belief state
        # + Add "mode" vector: enum of `active`, `challanger` (all players except active one), `target`, `counter-target`
        return {
            "player_stats": [
                (player.num_cards, player.coins) for player in self.players
            ],  # TODO: change to matrix (P * [N, C])
            "discard_pile": self.discard_pile,  # TODO: change to mask (discarded / non-discarded)
            "turn": self.n,
        }

    def __call__(self):
        logger.info("Game starting.")
        for player in self.players:
            player.coins = 2
            player.cards = CardList([self.deck.draw_card(), self.deck.draw_card()])

        print(str(game))

        while True:
            self.n += 1
            self.turn()
            print(str(game))

            # Finalize game
            if len(self.players) == 1:
                logger.info(f"Player {self.players[0]} has won the game!")
                return
            elif len(self.players) < 1:
                raise RuntimeError(f"We have {len(self.players)} players left...")

    def __str__(self):
        out = "\n" + "=" * 70 + "\n"
        out += "=" * 25 + f"   Turn number {self.n:2d}   " + "=" * 25 + "\n"
        out += "=" * 70 + "\n"
        for player in self.players:
            out += f"{str(player):10} | {player.coins:02d} coins | {player._cards}\n"
        out += "=" * 70 + "\n"
        out += "=" * 70 + "\n" * 2

        return out

    def __repr__(self):
        return str(self)

    def turn(self):
        for active_player in self.players:
            adversaries = [x for x in self.players if active_player != x]  # TODO: must be a better way to exclude
            action, target = active_player.do_action(adversaries, self.state)
            check_legal_action(
                action, active_player, target, self.deck
            )  # TODO: legality of action should be asserted by the player?
            self._turn(active_player, action, target)

    def get_first_challenger(self, challenges: Sequence[bool], challengers: Sequence[Player]) -> Player:
        ch_pl_tuples = [x for x in zip(challenges, challengers)]
        random.shuffle(ch_pl_tuples)
        for ch, pl in ch_pl_tuples:
            if ch:
                return pl

    def solve_challenge(self, challenger: Player, challenged: Player, action: Action, with_card: str = None):
        def solve(card_name: str):
            if challenged.has(card_name):
                logger.info(f"{challenged} has the card {card_name}!")
                challenged.replace(card_name, self.deck)
                challenger.lose_influence(self.discard_pile)
                if challenger.num_cards == 0:
                    self.remove_player(challenger)
            else:
                logger.info(f"{challenged} does not have the card {card_name}!")
                challenged.lose_influence(self.discard_pile)
                if challenged.num_cards == 0:
                    self.remove_player(challenged)

        if action == Action.INCOME:
            raise RuntimeError("INCOME Action was challenged.")
        elif action == Action.FOREIGNAID:
            raise RuntimeError("FOREIGNAID Action was challenged.")
        elif action == Action.COUP:
            raise RuntimeError("COUP Action was challenged.")
        elif action == Action.TAX:
            solve("Duke")
        elif action == Action.ASSASSINATION:
            solve("Assassin")
        elif action == Action.EXCHANGE:
            solve("Ambassador")
        elif action == Action.STEAL:
            solve("Captain")
        elif action == CounterAction.BLOCK_STEAL:
            if with_card not in ("Captain", "Ambassador"):
                raise RuntimeError(f"{challenged} tried to block stealing with {with_card}")
            solve(with_card)
        elif action == CounterAction.BLOCK_FOREIGNAID:
            solve("Duke")
        elif action == CounterAction.BLOCK_ASSASSINATION:
            solve("Contessa")
        else:
            raise RuntimeError(f"How do we solve a challange to {action}??")

    def remove_player(self, removed: Player):
        for idx, player in enumerate(self.players):
            if player == removed:
                self.players.pop(idx)
                logger.info(f"Player {player} was removed from the game.")
                logger.debug(f"List of players: {self.players}")

    def _turn(self, active_player: Player, action: Action, target: Player):
        adversaries = [x for x in self.players if active_player != x]  # TODO: must be a better way to exclude
        challenges = [adv.do_challenge(active_player, action, self.state) for adv in adversaries]
        if any(challenges):
            challenger = self.get_first_challenger(challenges, adversaries)
            self.solve_challenge(challenger=challenger, challenged=active_player, action=action)

        else:
            if action == Action.INCOME:
                active_player.income()  # TODO: return reward

            elif action == Action.FOREIGNAID:
                counter_actions = [player.counter_foreign_aid(active_player)[0] for player in adversaries]
                if any(counter_actions):
                    # TODO: this is an abuse of "get_first_challenger" as this is not a challange but a counter action
                    player_claiming_to_have_duke = self.get_first_challenger(counter_actions, adversaries)
                    counter_challenge = active_player.do_challenge(
                        player_claiming_to_have_duke, CounterAction.BLOCK_FOREIGNAID, self.state
                    )
                    if counter_challenge:
                        self.solve_challenge(
                            challenger=active_player,
                            challenged=player_claiming_to_have_duke,
                            action=CounterAction.BLOCK_FOREIGNAID,
                        )

                else:
                    active_player.foreign_aid()

            elif action == Action.COUP:
                active_player.coup()
                target.target_coup(self.discard_pile)

                if target.num_cards == 0:
                    self.remove_player(target)

            elif action == Action.TAX:
                active_player.tax()

            elif action == Action.ASSASSINATION:
                ca, _ = target.counter_assassinate(active_player, self.discard_pile)
                if ca:
                    counter_challenge = active_player.do_challenge(
                        target, CounterAction.BLOCK_ASSASSINATION, self.state
                    )
                    if counter_challenge:
                        self.solve_challenge(
                            challenger=active_player, challenged=target, action=CounterAction.BLOCK_ASSASSINATION,
                        )

                else:
                    active_player.assassinate()
                    if target.num_cards == 0:
                        self.remove_player(target)

            elif action == Action.EXCHANGE:
                active_player.exchange(self.deck)

            elif action == Action.STEAL:
                ca, with_card = target.counter_steal(active_player)
                if ca:
                    counter_challenge = active_player.do_challenge(target, CounterAction.BLOCK_STEAL, self.state)
                    if counter_challenge:
                        self.solve_challenge(
                            challenger=active_player,
                            challenged=target,
                            action=CounterAction.BLOCK_STEAL,
                            with_card=with_card,
                        )

                else:
                    active_player.steal()


if __name__ == "__main__":
    for _ in range(50):
        all_players = [
            RandomPlayer("Asaf"),
            RandomPlayer("Nitai"),
            RandomPlayer("Hossein"),
            RandomPlayer("Dror"),
            RandomPlayer("Matan"),
            RandomPlayer("Brandon"),
        ]
        num_players = np.random.choice([3, 4, 5, 6])
        players = [x for x in np.random.choice(all_players, num_players, replace=False)]
        game = Game(players)
        game()

"""
- Counter actions - everybody can challange!
- Unit tests after each turn:
    - Total number of cards in the game.
    - Total number of coins in the game.
"""
