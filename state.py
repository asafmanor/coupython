import logging
from typing import List
from cards import CardList
from utils import FormattedEnum


class _Player:
    pass


class ChallangeAftermath(FormattedEnum):
    WON = True
    LOST = False


class ChainOfEvents:
    def __init__(self):
        self._events = []
        self.logger = logging.getLogger("CHAIN")

    def record(self, player, action, target, info=None):
        self._events.append((player, action, target, info))

    def embed(self):
        raise NotImplementedError

    def __call__(self):
        self.logger.debug(str(self._events))
        return self._events


class ObservableState:
    def __init__(
        self,
        players: List[_Player],
        discard_pile: CardList,
        _round: int,
        chain_of_events: ChainOfEvents,
    ):
        self._player_stats = [(x.name, x.num_cards, x.coins) for x in players]
        self._discard_pile = discard_pile
        self._round = _round
        self._chain_of_events = chain_of_events

    def embed(self):
        raise NotImplementedError
