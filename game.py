import asyncio
import random
from typing import Sequence

from cards import Ambassador, Assassin, Captain, CardList, Contessa, Duke
from player import Player
from utils import Action, EmptyDeckError, IllegalActionError, CounterAction
import logging

logger = logging.getLogger(__name__)


class Deck:
    def __init__(self):
        """Create a new 15 cards deck."""
        cards = [Duke(i) for i in range(3)]
        cards += [Assassin(i) for i in range(3)]
        cards += [Ambassador(i) for i in range(3)]
        cards += [Captain(i) for i in range(3)]
        cards += [Contessa(i) for i in range(3)]
        self.cards = CardList(cards)

    @property
    def cards(self):
        raise IllegalActionError("Can't look at the Deck's cards.")

    @cards.setter
    def cards(self, cards):
        self._cards = cards

    def shuffle(self):
        random.shuffle(self._cards)

    def draw_card(self, shuffle: bool = False):
        if len(self) == 0:
            raise EmptyDeckError

        if shuffle:
            self.shuffle()
        return self._cards.pop()

    def return_cards(self, cards: CardList):
        self._cards += cards

    def __len__(self):
        return len(self._cards)


class Game:
    def __init__(self, players: Sequence[Player]):
        self.players = players
        self.deck = Deck()
        self.discard_pile = CardList()

    async def __call__(self):
        self.deck.shuffle()

        for player in self.players:
            player.coins = 2
            player.cards = CardList([self.deck.draw_card(), self.deck.draw_card()])

        while True:
            await self.turn()

    async def turn(self):
        for player in self.players:
            while True:
                action, target = await player.proactive_action()
                try:
                    self.check_legal_action(action, player, target)
                except IllegalActionError as err:
                    logger.info(err)
                    logger.info(
                        f"Player {player} played the illegal action {action}. Re-playing"
                    )
                    continue
                finally:
                    break

                self.do_action(action, player, target)

    # TODO this is hacky!
    def get_first_caller(self, calls: Sequence[bool]) -> Player:
        for idx, call in enumerate(calls):
            if call:
                return self.players[idx]

    @staticmethod
    def finalize_call(caller: Player, called: Player, action: Action):
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
        calls = await asyncio.gather(
            *[player.maybe_call(source, action) for player in self.players]
        )
        if any(calls):
            caller = get_first_caller(calls)
            self.finalize_call(caller=caller, called=source, action=action)

        else:
            if action == Action.INCOME:
                source.income()

            elif action == Action.FOREIGNAID:
                counter_actions = await asyncio.gather(
                    *[
                        player.counter_action(Action.FOREIGNAID, source)
                        for player in self.players
                    ]
                )
                if any(counter_actions):
                    claimed_duke = self.get_first_caller(counter_actions)
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
                target.lose_influence()

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
                    if len(target.cards) == 0:
                        self.remove_player(target)

            elif action == Action.EXCHANGE:
                source.exchange(self.deck)

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

    def check_legal_action(self, action: Action, player: Player, target: Player):
        if action == Action.COUP and player.coins < 7:
            raise IllegalActionError("Can't execute Coup: not enough coins.")
        elif action == Action.ASSASS and player.coins < 3:
            raise IllegalActionError("Can't execute Assassination: not enough coins.")
        elif action == Action.EXCHANGE and len(self.deck) < 2:
            raise IllegalActionError("Can't execute Exchange: deck is empty.")
        elif action == Action.STEAL and target.coins < 2:
            raise IllegalActionError(f"Can't steal from {target}. Not enough coins.")
        elif player.coins > 10 and Action != Action.COUP:
            raise IllegalActionError(f"{player} Must perform COUP!")

        # TODO add assertions that target is None if it should be.


"""TODO:
- block stealing - must state using what card
- implement finalize_call()
- implement get_first_caller() using async
- make all counterable actions use the same method for solving calls
"""
