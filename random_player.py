import asyncio
import random
from typing import Sequence

from cards import Card, CardList
from player import Player
from utils import Action, CounterAction


def get_time_for_move():
    return 1


def get_time_for_call():
    return 2


def uniform_proactive_action(cards: CardList, players: Sequence[Player]) -> Action:
    VALID_FACTOR = 2

    prob_INCOME = 1
    prob_FOREIGNAID = 1
    prob_COUP = 1
    prob_TAX = 1
    prob_ASSASS = 1
    prob_EX = 1
    prob_STEAL = 1

    if cards.has("Duke"):
        prob_TAX *= VALID_FACTOR
    if cards.has("Assassin"):
        prob_ASSASS *= VALID_FACTOR
    if cards.has("Ambassador"):
        prob_EX *= VALID_FACTOR
    if cards.has("Captain"):
        prob_STEAL *= VALID_FACTOR

    probs = [
        prob_INCOME,
        prob_FOREIGNAID,
        prob_COUP,
        prob_TAX,
        prob_ASSASS,
        prob_EX,
        prob_STEAL,
    ]

    actions = [
        Action.INCOME,
        Action.FOREIGNAID,
        Action.COUP,
        Action.TAX,
        Action.ASSASS,
        Action.EXCHANGE,
        Action.STEAL,
    ]

    return random.choices(actions, weights=probs), random.choices(players)


def uniform_counter_action(
    cards: CardList, action: Action, source: Player
) -> CounterAction:
    prob_BLOCKFOREIGNAID = 1
    prob_BLOCKSTEAL = 1
    prob_BLOCKASSASS = 1

    if action == Action.FOREIGNAID:
        if cards.has("Duke"):
            prob_BLOCKFOREIGNAID = 0.6
        else:
            prob_BLOCKFOREIGNAID = 0.2

        actions = [CounterAction.BLOCKFOREIGNAID, None]
        probs = [prob_BLOCKFOREIGNAID, 1 - prob_BLOCKFOREIGNAID]

    if action == Action.STEAL:
        if cards.has("Captain") or cards.has("Ambassador"):
            prob_BLOCKSTEAL = 0.9
        else:
            prob_BLOCKSTEAL = 0.3

        actions = [CounterAction.BLOCKSTEAL, None]
        probs = [prob_BLOCKSTEAL, 1 - prob_BLOCKSTEAL]

    if action == Action.ASSASS:
        if cards.has("Contessa") and len(cards) == 1:
            prob_BLOCKASSASS = 1.0
        elif cards.has("Contessa") and len(cards) == 2:
            prob_BLOCKASSASS = 0.9
        else:
            prob_BLOCKASSASS = 0.3

        actions = [CounterAction.BLOCKASSASS, None]
        probs = [prob_BLOCKASSASS, 1 - prob_BLOCKASSASS]

    return random.choices(actions, weights=probs)


class RandomPlayer(Player):
    async def _lose_influence(self) -> Card:
        asyncio.sleep(get_time_for_move())
        random.shuffle(self._cards)
        return self._cards.pop()

    async def _finalize_exchange(self, extra_cards: CardList) -> CardList:
        asyncio.sleep(get_time_for_move())
        current_num_cards = len(self._cards)
        cards = self._cards + extra_cards
        random.shuffle(cards)
        return_cards = [cards.pop()]
        if current_num_cards == 1:
            return_cards.append(cards.pop())
        self._cards = CardList(cards)

        return return_cards

    async def _counter_action(self, action: Action, source: Player) -> CounterAction:
        asyncio.sleep(get_time_for_move())
        return uniform_counter_action(self._cards, action, source)

    async def _proactive_action(self, players: Sequence[Player]) -> (Action, Player):
        asyncio.sleep(get_time_for_move())
        return uniform_proactive_action(self._cards, players)

    async def _maybe_call(self, source, action: Action) -> bool:
        asyncio.sleep(get_time_for_call())
        return random.choices([True, False])
