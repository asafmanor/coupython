from __future__ import annotations

import asyncio
import logging
import sys
from typing import Sequence

from cards import CardList
from deck import Deck
from player import Player
from random_player import RandomPlayer
from action import Action, CounterAction, IllegalActionError, check_legal_action

logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)


class CheatingError(Exception):
    pass


class Game:
    def __init__(self, players: Sequence[Player]):
        logger.info(f"Game is set up with {players}")
        self.players = players
        self.deck = Deck()
        self.discard_pile = CardList()

    async def __call__(self):
        logger.info("Game starting.")
        self.deck.shuffle()

        for player in self.players:
            player.coins = 2
            player.cards = CardList([self.deck.draw_card(), self.deck.draw_card()])

        while True:
            await self.turn()

    async def turn(self):
        for player in self.players:
            action_is_illegal = True
            while action_is_illegal:
                action, target = await player.proactive_action(self.players)
                try:
                    check_legal_action(action, player, target, self.deck)
                except IllegalActionError as err:
                    logger.debug(err)
                    logger.debug(
                        f"Player {player} played the illegal action {action}. Re-playing."
                    )
                except StopIteration:
                    action_is_illegal = False

            await self.do_action(player, action, target)

    # TODO this is hacky!
    def get_first_caller(
        self, calls: Sequence[bool], callers: Sequence[Player]
    ) -> Player:
        for idx, call in enumerate(calls):
            if call:
                return callers[idx]

    def finalize_call(self, caller: Player, called: Player, action: Action):

        def solve(card_name: str):
            if called.has(card_name):
                called.replace(card_name, self.deck)
                caller.lose_influence(self.discard_pile)
            else:
                called.lose_influence(self.discard_pile)

        if action == Action.INCOME:
            raise RuntimeError("INCOME Action was called.")
        elif action == Action.FOREIGNAID:
            raise RuntimeError("FOREIGNAID Action was called.")
        elif action == Action.COUP:
            raise RuntimeError("COUP Action was called.")
        elif action == Action.TAX:
            solve("Duke")
        elif action == Action.ASSASS:
            solve("Assassin")
        elif action == Action.EXCHANGE:
            solve("Ambassador")
        elif action == Action.STEAL:
            solve("Captain")

        logger.info("There were calls... skipping...")

    def remove_player(self, removed: Player):
        for idx, player in enumerate(self.players):
            if player == removed:
                self.players.pop(idx)
                logger.info(f"Player {player} was removed from the game.")
                logger.debug(f"List of players: {self.players}")

        if len(self.players == 1):
            logger.info(f"Player {player} has won the game!")
            exit()

    async def do_action(self, source: Player, action: Action, target: Player):
        adversaries = [player for player in self.players if player != source]
        calls = await asyncio.gather(
            *[player.maybe_call(source, action) for player in adversaries]
        )
        if any(calls):
            caller = self.get_first_caller(calls, adversaries)
            self.finalize_call(caller=caller, called=source, action=action)

        else:
            if action == Action.INCOME:
                source.income()

            elif action == Action.FOREIGNAID:
                counter_actions = await asyncio.gather(
                    *[
                        player.counter_action(Action.FOREIGNAID, source)
                        for player in adversaries
                    ]
                )
                if any(counter_actions):
                    claimed_duke = self.get_first_caller(counter_actions, adversaries)
                    counter_call = await source.maybe_call(
                        claimed_duke, CounterAction.BLOCKFOREIGNAID
                    )
                    if counter_call:
                        self.finalize_call(
                            caller=source,
                            called=claimed_duke,
                            action=CounterAction.BLOCKFOREIGNAID,
                        )

                else:
                    source.foreign_aid()

            elif action == Action.COUP:
                source.coup()
                await target.target_coup(self.discard_pile)

                if len(target.cards) == 0:
                    self.remove_player(target)

            elif action == Action.TAX:
                source.tax()

            elif action == Action.ASSASS:
                ca = await target.target_assassinate(source, self.discard_pile)
                if ca:
                    counter_call = await source.maybe_call(
                        target, CounterAction.BLOCKASSASS
                    )
                    if counter_call:
                        self.finalize_call(
                            caller=source,
                            called=target,
                            action=CounterAction.BLOCKASSASS,
                        )

                else:
                    source.assassinate()
                    if (
                        len(target._cards) == 0
                    ):  # TODO, don't use target._cards, find a better way
                        self.remove_player(target)

            elif action == Action.EXCHANGE:
                await source.exchange(self.deck)

            elif action == Action.STEAL:
                ca = await target.target_steal(source)
                if ca:
                    counter_call = await source.maybe_call(
                        target, CounterAction.BLOCKSTEAL
                    )
                    if counter_call:
                        self.finalize_call(
                            caller=source,
                            called=target,
                            action=CounterAction.BLOCKSTEAL,
                        )

                else:
                    source.steal()


if __name__ == "__main__":
    players = [
        RandomPlayer("Acapella"),
        RandomPlayer("Boogy"),
        RandomPlayer("Classic"),
        RandomPlayer("Disco"),
    ]
    game = Game(players)
    asyncio.run(game())

"""TODO:
- block stealing - must state using what card
- implement finalize_call()
- implement get_first_caller() using async.wait()
- make all counterable actions use the same method for solving calls
- break Player.counter_action() into the different actions.
- break do_action() so unit-tests can run on it
"""
