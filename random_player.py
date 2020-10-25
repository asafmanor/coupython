import asyncio
import random

from cards import Ambassador, Assassin, Captain, Card, CardList, Contessa, Duke
from game import Player
from utils import Action


def get_time_for_move():
    return 1


def get_time_for_call():
    return 2


def uniform_proactive_action(cards: CardList) -> list:
    VALID_FACTOR = 3

    prob_INCOME = 1
    prob_FOREIGNAID = 1
    prob_COUP = 1
    prob_TAKE3 = 1
    prob_ASSA = 1
    prob_EX = 1
    prob_STEAL = 1

    if cards.has("Duke"):
        prob_TAKE3 *= VALID_FACTOR
    if cards.has("Assassin"):
        prob_ASSA *= VALID_FACTOR
    if cards.has("Ambassador"):
        prob_EX *= VALID_FACTOR
    if cards.has("Captain"):
        prob_STEAL *= VALID_FACTOR

    probs = [
        prob_INCOME,
        prob_FOREIGNAID,
        prob_COUP,
        prob_TAKE3,
        prob_ASSA,
        prob_EX,
        prob_STEAL,
    ]

    actions = [
        Action.INCOME,
        Action.FOREIGNAID,
        Action.COUP,
        Action.TAKE3,
        Action.ASSA,
        Action.EX,
        Action.STEAL,
    ]

    return random.choice(actions, weights=probs)


def uniform_counter_action(cards: CardList) -> list:
    raise NotImplementedError


class RandomPlayer(Player):
    async def _lose_influence(self) -> Card:
        asyncio.sleep(get_time_for_move())
        random.shuffle(self.cards)
        return self.cards.pop()

    async def _finalize_exchange(self, extra_cards: CardList) -> CardList:
        asyncio.sleep(get_time_for_move())
        current_num_cards = len(self.cards)
        cards = self.cards + extra_cards
        random.shuffle(cards)
        return_cards = [cards.pop()]
        if current_num_cards == 1:
            return_cards.append(cards.pop())
        self.cards = CardList(cards)

        return return_cards

    async def _counter_action(self, action: Action, source: Player) -> Action:
        asyncio.sleep(get_time_for_move())
        raise NotImplementedError

    async def _proactive_action(self) -> Action:
        asyncio.sleep(get_time_for_move())
        return uniform_proactive_action(self.cards)
