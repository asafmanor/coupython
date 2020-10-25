import enum

from game import Deck, Player


class InsufficientFundsError(Exception):
    pass


class EmptyDeckError(Exception):
    pass


class IllegalActionError(Exception):
    pass


class Action(enum.Enum):
    INCOME = 0
    FOREIGNAID = 1
    COUP = 2
    TAX = 3
    ASSASS = 4
    EXCHANGE = 5
    STEAL = 6


class CounterAction(enum.Enum):
    BLOCKFOREIGNAID = 0
    BLOCKSTEAL = 1
    BLOCKASSASS = 2
