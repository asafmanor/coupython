import enum


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
    TAKE3 = 3
    ASSA = 4
    EX = 5
    STEAL = 6


class TargetAction(enum.Enum):
    STEAL_AS_TARGET = 0
    ASSA_AS_TARGET = 1


class CounterAction(enum.Enum):
    BLOCKFOREIGNAID = 0
    BLOCKSTEALING = 1
    BLOCKASSA = 2
