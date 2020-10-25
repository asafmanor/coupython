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
    TAX = 3
    ASSASS = 4
    EXCHANGE = 5
    STEAL = 6

    def __repr__(self):
        return str(self)


class CounterAction(enum.Enum):
    BLOCKFOREIGNAID = 0
    BLOCKSTEAL = 1
    BLOCKASSASS = 2
