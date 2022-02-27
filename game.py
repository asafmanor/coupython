from __future__ import annotations

import logging
import random
import sys
from collections import defaultdict
from typing import Sequence

from action import Action, CounterAction, check_legal_action
from cards import CardList
from deck import Deck
from player import Player
from random_player import RandomPlayer
from state import ChainOfEvents, ObservableState, ChallangeAftermath

logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(name)-12s %(message)s",
)

random.seed(0)


class Game:
    def __init__(self, players: Sequence[Player]):

        logger.info(f"Game is set up with {players}")
        self.players = players
        self.deck = Deck()
        self.discard_pile = CardList()
        self.n = 0

    def state(self, chain_of_events: ChainOfEvents) -> ObservableState:
        return ObservableState(self.players, self.discard_pile, self.n, chain_of_events)

    def __call__(self) -> Player:
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
                return self.players[0]
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
            chain_of_events = ChainOfEvents()

            # Active player performing action
            adversaries = [
                x for x in self.players if active_player != x
            ]  # TODO: must be a better way to exclude
            action, target = active_player.do_action(
                adversaries, self.state(chain_of_events)
            )
            # TODO: legality of action should be asserted by the player?
            check_legal_action(action, active_player, target, self.deck)
            chain_of_events.record(player=active_player, action=action, target=target)

            challenges = [
                adv.do_challenge(active_player, action, self.state(chain_of_events))
                for adv in adversaries
            ]
            if any(challenges):
                challenger = self._get_single_random(challenges, adversaries)

                aftermath = self.solve_challenge(
                    challenger=challenger, challenged=active_player, action=action
                )
                chain_of_events.record(
                    player=challenger,
                    action=CounterAction.CHALLANGE,
                    target=active_player,
                    info=aftermath,
                )

            else:
                if action == Action.INCOME:
                    active_player.income()  # TODO: return reward

                elif action == Action.FOREIGNAID:
                    counter_actions = [
                        adv.counter_foreign_aid(
                            active_player, self.state(chain_of_events)
                        )[0]
                        for adv in adversaries
                    ]
                    if any(counter_actions):
                        player_claiming_to_have_duke = self._get_single_random(
                            counter_actions, adversaries
                        )
                        chain_of_events.record(
                            player=player_claiming_to_have_duke,
                            action=CounterAction.BLOCK_FOREIGNAID,
                            target=active_player,
                        )

                        counter_challenge = active_player.do_challenge(
                            player_claiming_to_have_duke,
                            CounterAction.BLOCK_FOREIGNAID,
                            self.state(chain_of_events),
                        )
                        if counter_challenge:
                            aftermath = self.solve_challenge(
                                challenger=active_player,
                                challenged=player_claiming_to_have_duke,
                                action=CounterAction.BLOCK_FOREIGNAID,
                            )
                            chain_of_events.record(
                                player=active_player,
                                action=CounterAction.CHALLANGE,
                                target=player_claiming_to_have_duke,
                                info=aftermath,
                            )

                    else:
                        active_player.foreign_aid()

                elif action == Action.COUP:
                    active_player.coup()
                    target.lose_influence(self.discard_pile)

                    if target.num_cards == 0:
                        self.remove_player(target)

                elif action == Action.TAX:
                    active_player.tax()

                elif action == Action.ASSASSINATION:
                    ca, _ = target.counter_assassinate(
                        active_player, self.discard_pile, self.state(chain_of_events)
                    )
                    if ca:
                        player_claiming_to_have_contessa = target
                        chain_of_events.record(
                            player=player_claiming_to_have_contessa,
                            action=CounterAction.BLOCK_ASSASSINATION,
                            target=active_player,
                        )

                        counter_challenge = active_player.do_challenge(
                            player_claiming_to_have_contessa,
                            CounterAction.BLOCK_ASSASSINATION,
                            self.state(chain_of_events),
                        )
                        if counter_challenge:
                            aftermath = self.solve_challenge(
                                challenger=active_player,
                                challenged=player_claiming_to_have_contessa,
                                action=CounterAction.BLOCK_ASSASSINATION,
                            )
                            chain_of_events.record(
                                player=active_player,
                                action=CounterAction.CHALLANGE,
                                target=player_claiming_to_have_contessa,
                                info=aftermath,
                            )

                    else:
                        active_player.assassinate()
                        if target.num_cards == 0:
                            self.remove_player(target)

                elif action == Action.EXCHANGE:
                    active_player.exchange(self.deck)

                elif action == Action.STEAL:
                    ca, with_card = target.counter_steal(
                        active_player, self.state(chain_of_events)
                    )
                    if ca:
                        player_claiming_to_have_captain_or_ambassador = target
                        chain_of_events.record(
                            player=player_claiming_to_have_captain_or_ambassador,
                            action=CounterAction.BLOCK_STEAL,
                            target=active_player,
                            info=with_card,
                        )

                        counter_challenge = active_player.do_challenge(
                            player_claiming_to_have_captain_or_ambassador,
                            CounterAction.BLOCK_STEAL,
                            self.state(chain_of_events),
                        )
                        if counter_challenge:
                            aftermath = self.solve_challenge(
                                challenger=active_player,
                                challenged=player_claiming_to_have_captain_or_ambassador,
                                action=CounterAction.BLOCK_STEAL,
                                with_card=with_card,
                            )
                            chain_of_events.record(
                                player=active_player,
                                action=CounterAction.CHALLANGE,
                                target=player_claiming_to_have_captain_or_ambassador,
                                info=aftermath,
                            )

                    else:
                        active_player.steal()

            chain_of_events()

    def _get_single_random(
        self, challenges: Sequence[bool], challengers: Sequence[Player]
    ) -> Player:
        ch_pl_tuples = [x for x in zip(challenges, challengers)]
        random.shuffle(ch_pl_tuples)
        for ch, pl in ch_pl_tuples:
            if ch:
                return pl

    def solve_challenge(
        self,
        challenger: Player,
        challenged: Player,
        action: Action,
        with_card: str = None,
    ) -> ChallangeAftermath:
        def solve(card_name: str):
            """Solve the challange by checking the challenged / challenger cards.

            Args:
                card_name (str): The card name to check.

            Returns:
                ChallangeAftermath: If the challanger won, i.e. the challenged does not have the card.
            """

            if challenged.has(card_name):
                logger.info(f"{challenged} has the card {card_name}!")
                challenged.replace(card_name, self.deck)
                challenger.lose_influence(self.discard_pile)
                if challenger.num_cards == 0:
                    self.remove_player(challenger)
                return ChallangeAftermath.LOST

            else:
                logger.info(f"{challenged} does not have the card {card_name}!")
                challenged.lose_influence(self.discard_pile)
                if challenged.num_cards == 0:
                    self.remove_player(challenged)
                return ChallangeAftermath.WON

        if action == Action.INCOME:
            raise RuntimeError("INCOME Action was challenged.")
        elif action == Action.FOREIGNAID:
            raise RuntimeError("FOREIGNAID Action was challenged.")
        elif action == Action.COUP:
            raise RuntimeError("COUP Action was challenged.")
        elif action == Action.TAX:
            return solve("Duke")
        elif action == Action.ASSASSINATION:
            return solve("Assassin")
        elif action == Action.EXCHANGE:
            return solve("Ambassador")
        elif action == Action.STEAL:
            return solve("Captain")
        elif action == CounterAction.BLOCK_STEAL:
            if with_card not in ("Captain", "Ambassador"):
                raise RuntimeError(
                    f"{challenged} tried to block stealing with {with_card}"
                )
            return solve(with_card)
        elif action == CounterAction.BLOCK_FOREIGNAID:
            return solve("Duke")
        elif action == CounterAction.BLOCK_ASSASSINATION:
            return solve("Contessa")
        else:
            raise RuntimeError(f"How do we solve a challange to {action}??")

    def remove_player(self, removed: Player):
        for idx, player in enumerate(self.players):
            if player == removed:
                self.players.pop(idx)
                logger.info(f"Player {player} was removed from the game.")
                logger.debug(f"List of players: {self.players}")


if __name__ == "__main__":
    winners = defaultdict(int)
    for _ in range(50):
        all_players = [
            RandomPlayer("Asaf"),
            RandomPlayer("Nitai"),
            RandomPlayer("Hossein"),
            RandomPlayer("Dror"),
            RandomPlayer("Matan"),
            RandomPlayer("Brandon"),
        ]
        players = all_players
        game = Game(players)
        winner = game()
        winners[winner.name] += 1

    print(winners)

"""
- Counter actions - everybody can challange!
- Unit tests after each turn:
    - Total number of cards in the game.
    - Total number of coins in the game.
"""
