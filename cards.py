import random
import torch

from card import Card, CARDS_TO_IDS


NUM_CARDS_PER_TYPE = 3


class DiscardPile:

    _ids_to_named_cards = {v: k for k, v in CARDS_TO_IDS.items()}

    def reset(self):
        self._cards = torch.zeros(len(CARDS_TO_IDS), dtype=torch.uint8, requires_grad=False)

    def __init__(self, num_cards_per_type: int = NUM_CARDS_PER_TYPE):
        self._num_cards_per_type = num_cards_per_type
        self._cards = None
        self.reset()

    def view(self, player: int) -> torch.Tensor:
        return self._cards

    def discard(self, card: Card):
        card_indx = CARDS_TO_IDS[card]
        self._cards[card_indx] += 1

        if not 0 <= self._cards[card_indx] <= self._num_cards_per_type:
            raise RuntimeError("developer error")

    @property
    def discarded(self) -> dict:
        return {self._ids_to_named_cards[i]: self._cards[i].item() for i in range(len(CARDS_TO_IDS))}

    def __str__(self):
        return str(self.discarded)

    def __repr__(self):
        return str(self)


class GamePile:

    _ids_to_named_cards = {v: k for k, v in CARDS_TO_IDS.items()}

    def reset(self):
        self._cards = self._num_cards_per_type * torch.ones(len(CARDS_TO_IDS), dtype=torch.uint8, requires_grad=False)

    def __init__(self, num_cards_per_type: int = NUM_CARDS_PER_TYPE):
        self._num_cards_per_type = num_cards_per_type
        self._cards = None
        self.reset()

    @property
    def num_cards_in_pile(self):
        return torch.sum(self._cards)

    def empty(self):
        return self.num_cards_in_pile == 0

    def pop(self) -> Card:
        try:
            cards_in_pile = []
            [cards_in_pile.extend(self._cards[x] * [x]) for x in range(len(self._cards))]
            card_idx = random.choice(cards_in_pile)
            self._cards[card_idx] = self._cards[card_idx] - 1
            return self._ids_to_named_cards[card_idx]()
        except IndexError:
            raise RuntimeError("developer error")
