import enum
from deck import Deck


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
        return self.name

    def __str__(self):
        return self.name


class CounterAction(enum.Enum):
    BLOCKFOREIGNAID = 0
    BLOCKSTEAL = 1
    BLOCKASSASS = 2

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


def check_legal_action(
    action: Action, player, target, deck: Deck = None
):
    """If action is illegal, IllegalActionError is raised. Otherwise, StopIteration is raised."""

    if action == Action.COUP and player.coins < 7:
        raise IllegalActionError("Can't execute Coup: not enough coins.")
    elif action == Action.ASSASS and player.coins < 3:
        raise IllegalActionError("Can't execute Assassination: not enough coins.")
    elif action == Action.STEAL and target.coins < 2:
        raise IllegalActionError(f"Can't steal from {target}. Not enough coins.")
    elif player.coins > 10 and action != Action.COUP:
        raise IllegalActionError(f"{player} Must perform COUP!")

    if action == Action.EXCHANGE and deck is not None and len(deck) < 2:
        raise IllegalActionError("Can't execute Exchange: deck is empty.")

    # TODO add assertions that target is None if it should be.

    raise StopIteration
