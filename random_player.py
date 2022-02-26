from __future__ import annotations

import logging
import random
from typing import Dict, Sequence, Tuple

from action import Action
from cards import Card, CardList
from deck import Deck, CheatingError
from player import Player


class InsufficientFundsError(Exception):
    pass


# TODO: add a belief state per player for the distribution of cards across the game
class RandomPlayer(Player):
    def _lose_influence(self) -> Card:
        # TODO change after there is a better implementation for "cardlist"
        card = random.choice(self._cards)  # This does not remove the card.
        card = self._cards.get(card.name)  # And this does.
        self.logger.debug(f"Player {self} loses influence: {card}")

    def _exchange(self, extra_cards: CardList) -> CardList:
        all_cards = self._cards + extra_cards
        indices = random.sample(range(len(all_cards)), 2)
        card0, card1 = self._cards.pop(indices[0]), self._cards.pop(indices[1])
        self.logger.debug(f"Player {self} returns {card0} and {card1} to the pile.")

    def _do_counter_action(self, action: Action, source: Player) -> Action:
        raise NotImplementedError

    def _do_action(
        self, players: Sequence[Player]
    ) -> Tuple[Action, Player]:  # Actually, returns a different player

        raise NotImplementedError

    def _do_challenge(self, source: Player, action: Action, state: Dict) -> bool:
        raise NotImplementedError
