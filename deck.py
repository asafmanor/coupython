import logging
import random

from cards import Ambassador, Assassin, Captain, CardList, Contessa, Duke

logger = logging.getLogger(__name__)


class CheatingError(Exception):
    pass


class EmptyDeckError(Exception):
    pass


class Deck:
    def __init__(self):
        """Create a new 15 cards deck."""
        cards = [Duke(i) for i in range(3)]
        cards += [Assassin(i) for i in range(3)]
        cards += [Ambassador(i) for i in range(3)]
        cards += [Captain(i) for i in range(3)]
        cards += [Contessa(i) for i in range(3)]
        self.cards = CardList(cards)
        self._shuffle()

    @property
    def cards(self):
        raise CheatingError("Can't look at the Deck's cards.")

    @cards.setter
    def cards(self, cards):
        self._cards = cards

    def _shuffle(self):
        random.shuffle(self._cards)

    def draw_card(self):
        if len(self) == 0:
            raise EmptyDeckError
        return self._cards.pop()

    def return_cards(self, cards: CardList):
        self._cards += cards
        assert isinstance(self._cards, CardList)
        self._shuffle()

    def __len__(self):
        return len(self._cards)
