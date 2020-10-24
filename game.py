import asyncio
import logging
import random
from typing import Callable

import numpy as np

from cards import Ambassador, Assassin, Captain, CardList, Contessa, Duke
from utils import (
    Action,
    CounterAction,
    EmptyDeckError,
    IllegalActionError,
    InsufficientFundsError,
    TargetAction,
)


class Deck:
    def __init__(self):
        """Create a new 15 cards deck."""
        cards = [Duke(i) for i in range(3)]
        cards += [Assassin(i) for i in range(3)]
        cards += [Ambassador(i) for i in range(3)]
        cards += [Captain(i) for i in range(3)]
        cards += [Contessa(i) for i in range(3)]
        self.cards = CardList(cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self, shuffle: bool = False):
        if len(self) == 0:
            raise EmptyDeckError

        if shuffle:
            self.shuffle()
        return self.cards.pop()

    def return_cards(self, *cards):
        self.cards += cards

    def __len__(self):
        return len(self.cards)


class Player:
    # TODO: implement > 10 cards check
    # methods beginning with target_ are called when you are the target of an action
    def __init__(self, name: str):
        self.name = name
        self.cards: list = None
        self.logger = logging.getLogger(name)

    @property
    def coins(self):
        return self._coins

    @coins.setter
    def coins(self, value):
        if value < 0:
            raise InsufficientFundsError
        self._coins = value

    def take_3(self):
        self.coins += 3

    def assassinate(self, target):
        if self.coins < 3:
            raise IllegalActionError("Can't execute Assasinate: not enough coins")
        self.coins -= 3
        # TODO target.target_assassinate() should be caleed from main loop

    async def exchange(self, deck: Deck):
        if len(deck) < 2:
            raise IllegalActionError("Can't execute Exchange: deck is empty")

        card_1 = deck.draw_card(shuffle=False)
        card_2 = deck.draw_card(shuffle=False)
        current_num_cards = len(self.cards)
        await self._finalize_exchange(self, [card_1, card_2])
        if current_num_cards == len(self.cards):
            raise RuntimeError(
                "Number of cards returned from _finalize_exchange "
                + f"is inequivalent to {current_num_cards}"
            )

    async def counter_action(self, action: Action, source):
        counter_action = await self._counter_action(action, source)
        if counter_action is not None:
            self.logger.info(f"Performed counter-action {counter_action}")

    async def target_assassinate(self, source):
        """Called when you the player is the target of an assassination."""
        counter_action = await self.counter_action(TargetAction.ASSA_AS_TARGET, source)
        if counter_action is None:
            self.lose_influence()

        return counter_action

    async def target_steal(self, source):
        """Called when you the player is the target of stealing."""
        counter_action = await self.counter_action(TargetAction.STEAL_AS_TARGET, source)
        if counter_action is None:
            self.coins -= 2

        return counter_action

    def steal(self, target):
        if target.coins < 2:
            raise IllegalActionError(
                f"Can't steal from {target.name}: s/he has insufficient funds."
            )

        # TODO target.target_steal() should be called from main loop
        self.coins += 2

    def lose_influence(self, discard) -> int:
        card = self._lose_influence()
        self.logger.info(f"Lost a {card.name} influence")
        discard.cards.append(card)
        return len(self.cards)

    async def _lose_influence(self):
        raise NotImplementedError

    async def _finalize_exchange(self, extra_cards: list):
        raise NotImplementedError

    async def _counter_action(self, action, source):
        raise NotImplementedError

    async def _proactive_action(self):
        raise NotImplementedError
