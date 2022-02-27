from deck import Deck
from utils import FormattedEnum


class _Player:
    pass


class IllegalActionError(Exception):
    pass


class Action(FormattedEnum):
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


class CounterAction(FormattedEnum):
    BLOCK_FOREIGNAID = 7
    BLOCK_STEAL = 8
    BLOCK_ASSASSINATION = 9
    CHALLANGE = 10

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


ACTION_TO_COUNTER_ACTION = {
    Action.FOREIGNAID: CounterAction.BLOCK_FOREIGNAID,
    Action.STEAL: CounterAction.BLOCK_STEAL,
    Action.ASSASSINATION: CounterAction.BLOCK_ASSASSINATION,
}


def requires_target(action: Action):
    return action in [Action.COUP, Action.ASSASSINATION, Action.STEAL]


def check_legal_action(
    action: Action, player: _Player, target: _Player, deck: Deck = None
):
    """If action is illegal, IllegalActionError is raised."""

    if requires_target(action):
        if target is None:
            raise IllegalActionError(f"Can't perform action {action} with no target.")
    else:
        if target is not None:
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
