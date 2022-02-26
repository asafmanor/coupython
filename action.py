import enum
from deck import Deck
from player import Player


class IllegalActionError(Exception):
    pass


class Action(enum.Enum):
    INCOME = 0
    FOREIGNAID = 1
    COUP = 2
    TAX = 3
    ASSASSINATION = 4
    EXCHANGE = 5
    STEAL = 6

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class CounterAction(enum.Enum):
    BLOCK_FOREIGNAID = 0
    BLOCK_STEAL = 1
    BLOCK_ASSASSINATION = 2

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


def check_legal_action(action: Action, player: Player, target: Player, deck: Deck = None):
    """If action is illegal, IllegalActionError is raised."""

    if action in [Action.COUP, Action.ASSASSINATION, Action.STEAL] and target is None:
        raise IllegalActionError(f"Can't perform action {action} with no target.")

    if action in [Action.INCOME, Action.FOREIGNAID, Action.TAX, Action.EXCHANGE] and target is not None:
        raise IllegalActionError(f"Can't perform action {action} with a target.")

    if action == Action.COUP and player.coins < 7:
        raise IllegalActionError("Can't execute Coup: not enough coins.")
    elif action == Action.ASSASSINATION and player.coins < 3:
        raise IllegalActionError("Can't execute Assassination: not enough coins.")
    elif action == Action.STEAL and target.coins < 2:
        raise IllegalActionError(f"Can't steal from {target}. Not enough coins.")
    elif player.coins > 10 and action != Action.COUP:
        raise IllegalActionError(f"{player} Must perform COUP!")

    if action == Action.EXCHANGE and deck is not None and len(deck) < 2:
        raise IllegalActionError("Can't execute Exchange: deck is empty.")
