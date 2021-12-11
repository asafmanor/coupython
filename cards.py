import random
import torch

from card import Card, CARDS


NUM_CARDS_PER_TYPE = 3


class DiscardPile:

    def reset(self):
        self._discarded_cards = {x: i for i, x in enumerate(CARDS.values())}
        self._cards = torch.zeros(len(self._discarded_cards), dtype=torch.uint8, requires_grad=False)

    def __init__(self, num_cards_per_type: int = NUM_CARDS_PER_TYPE):
        self._num_cards_per_type = num_cards_per_type
        self._discarded_cards, self._cards = None, None
        self.reset()

    @property
    def cards(self) -> torch.Tensor:
        return self._cards

    def discard(self, card: Card):
        card_type = type(card)
        card_indx = self._discarded_cards[card_type]
        self._cards[card_indx] += 1

        if not 0 <= self._cards[card_indx] <= self._num_cards_per_type:
            raise RuntimeError

    def __str__(self):
        return str(self._discarded_cards)

    def __repr__(self):
        return str(self)


class GamePile:

    def reset(self):
        self._named_cards_to_ids = {x: i for i, x in enumerate(CARDS.values())}
        self._ids_to_named_cards = {i: x for i, x in enumerate(CARDS.values())}
        self._cards = self._num_cards_per_type * torch.ones(len(self._named_cards_to_ids), dtype=torch.uint8, requires_grad=False)

    def __init__(self, num_cards_per_type: int = NUM_CARDS_PER_TYPE):
        self._num_cards_per_type = num_cards_per_type
        self._named_cards, self._cards = None, None
        self.reset()

    def has(self, card: Card) -> bool:
        card_type = type(card)
        card_indx = self._named_cards_to_ids[card_type]
        return self._cards[card_indx] > 0

    def pop(self) -> Card:
        cards_in_pile = []
        [cards_in_pile.extend(self._cards[x] * [x]) for x in range(len(self._cards))]
        card_idx = random.choice(cards_in_pile)
        self._cards[card_idx] = self._cards[card_idx] - 1
        return self._ids_to_named_cards[card_idx]()
