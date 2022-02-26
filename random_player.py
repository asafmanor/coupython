from __future__ import annotations

import random
from typing import Dict, Sequence, Tuple

import numpy as np

from action import Action, requires_target
from cards import Card, CardList
from player import Player


class InsufficientFundsError(Exception):
    pass


# TODO: add a belief state per player for the distribution of cards across the game
class RandomPlayer(Player):
    def _lose_influence(self) -> Card:
        random.shuffle(self._cards)
        return self._cards.pop()

    def _exchange(self, extra_cards: CardList) -> CardList:
        self.logger.debug(f"Has {self._cards} and got {extra_cards} from the deck.")
        all_cards = self._cards + extra_cards
        random.shuffle(all_cards)
        card0, card1 = all_cards.pop(), all_cards.pop()
        self.logger.debug(f"Player {self} returns {card0} and {card1} to the pile.")
        self._cards = CardList(all_cards)
        self.logger.debug(f"Has {self._cards} now.")
        return CardList([card0, card1])

    def _do_counter_action(self, action: Action, source: Player) -> Tuple[bool, str]:
        if action == Action.FOREIGNAID:
            with_card = "Duke"
        elif action == Action.ASSASSINATION:
            with_card = "Contessa"
        elif action == Action.STEAL:
            with_card = random.choice(["Captain", "Ambassador"])

        return np.random.choice([True, False], 1, p=[0.5, 0.5]), with_card

    def _do_action(self, players: Sequence[Player], state: Dict) -> Tuple[Action, Player]:
        all_actions = [x for x in Action]

        if self.coins > 10:
            all_actions = [Action.COUP]
        if self.coins < 7:
            all_actions.remove(Action.COUP)
        if self.coins < 3:
            all_actions.remove(Action.ASSASSINATION)

        while True:
            action = random.choice(all_actions)
            if requires_target(action):
                target = random.choice(players)
            else:
                target = None
            if action == Action.STEAL and target.coins < 2:
                continue
            break

        return action, target

    def _do_challenge(self, source: Player, action: Action, state: Dict) -> bool:
        return np.random.choice([True, False], 1, p=[0.5, 0.5])
