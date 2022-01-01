from __future__ import annotations

import enum
import logging
from typing import Sequence, Tuple

import numpy as np

# from action import Action
from cards import Card
# from deck import Deck, CheatingError


class InsufficientFundsError(Exception):
    pass


# # TODO: add a belief state per player for the distribution of cards across the game
# class Player:
#     # methods beginning with target_ are called when you are the target of an action
#     # Gaming logic should only be implemented in subclasses of Player
#     def __init__(self, name: str):
#         self.name = name
#         self.cards: CardList = None
#         self.logger = logging.getLogger(name)
#
#     def __str__(self):
#         return self.name
#
#     def __repr__(self):
#         return self.name
#
#     @property
#     def cards(self):
#         self.logger.debug(
#             "Cards can't be accessed. If the cards must be accessed, use `self._cards`"
#         )
#         raise CheatingError("Can't look at a player's cards.")
#
#     @cards.setter
#     def cards(self, cards: CardList):
#         self._cards = cards
#
#     @property
#     def num_cards(self):
#         return len(self._cards)
#
#     @property
#     def coins(self) -> int:
#         return self._coins
#
#     @coins.setter
#     def coins(self, value):
#         if value < 0:
#             raise InsufficientFundsError
#         self._coins = value
#
#     def has(self, card_name: str) -> bool:
#         return self._cards.has(card_name)
#
#     def get(self, card_name: str) -> Card:
#         return self._cards.get(card_name)
#
#     def income(self):
#         self.coins += 1
#
#     def foreign_aid(self):
#         self.coins += 2
#
#     def tax(self):
#         self.coins += 3
#
#     def coup(self):
#         self.coins -= 7
#
#     def assassinate(self):
#         self.coins -= 3
#
#     def steal(self):
#         self.coins += 2
#
#     def replace(self, card_name: str, deck: Deck):
#         deck.return_cards(CardList([self.get(card_name)]))
#         deck._shuffle()
#         self._cards.append(deck.draw_card())
#
#     def exchange(self, deck: Deck):
#         card_1 = deck.draw_card()
#         card_2 = deck.draw_card()
#         current_num_cards = len(self._cards)
#         return_cards = self._exchange(CardList([card_1, card_2]))
#
#         deck.return_cards(return_cards)
#         deck._shuffle()
#
#         if current_num_cards != len(self._cards):
#             raise RuntimeError(
#                 "Number of cards returned from _exchange "
#                 + f"is inequivalent to {current_num_cards}"
#             )
#
#     def do_challenge(self, source, action: Action) -> bool:
#         if action in [Action.INCOME, Action.FOREIGNAID, Action.COUP]:
#             return False
#
#         challange = self._do_challenge(source, action)
#         if challange:
#             self.logger.info(f"Challanged action {action} of player {source}")
#         return challange
#
#     def do_action(self, players: Sequence[Player]) -> Tuple[Action, None]:  # TODO change to state. this is PI.
#         action, target = self._do_action(players)
#         if target is not None:
#             self.logger.info(f"Attempts action {action} on player {target}")
#         else:
#             self.logger.info(f"Attempts action {action}")
#
#         return action, target
#
#     def do_counter_action(self, action: Action, source: Player) -> bool:
#         counter_action = self._do_counter_action(action, source)
#         if counter_action is not None:
#             self.logger.info(f"Performed counter-action {counter_action}")
#             return True
#
#         return False
#
#     def target_assassinate(self, source: Player, discard_pile: CardList) -> bool:
#         """Called when you the player is the target of an assassination."""
#         counter_action = self.do_counter_action(Action.ASSASS, source)
#         if not counter_action:
#             self.lose_influence(discard_pile)
#
#         return counter_action
#
#     def target_steal(self, source: Player) -> bool:
#         """Called when you the player is the target of stealing."""
#         counter_action = self.do_counter_action(Action.STEAL, source)
#         if counter_action is False:
#             self.coins -= 2
#
#         return counter_action
#
#     def target_coup(self, discard_pile: CardList):
#         return self.lose_influence(discard_pile)
#
#     def lose_influence(self, discard_pile: CardList) -> int:
#         card = self._lose_influence()
#         self.logger.info(f"Lost a {card.name} influence")
#         discard_pile.append(card)
#         return len(self._cards)
#
#     def _lose_influence(self) -> Card:
#         raise NotImplementedError
#
#     def _exchange(self, extra_cards: CardList) -> CardList:
#         raise NotImplementedError
#
#     def _do_counter_action(self, action: Action, source: Player) -> Action:
#         raise NotImplementedError
#
#     def _do_action(
#         self, players: Sequence[Player]
#     ) -> Tuple[Action, None]:  # Actually, returns a different player
#         raise NotImplementedError
#
#     def _do_challenge(self, source: Player, action: Action) -> bool:
#         raise NotImplementedError


import enum
import torch
import torch.nn.functional as F

from board import Board
from card import CARDS, CARDS_TO_IDS
from cards import DiscardPile, NUM_CARDS_PER_TYPE
from contextlib import contextmanager


class PlayerModesEnum(enum.Enum):
    active = 0
    challenged = 1
    challenging = 2
    responding = 3

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class PlayerModes:

    def __init__(self):
        self._mode = torch.zeros(4, dtype=torch.uint8)

    def set(self, mode, val):
        assert mode.value in PlayerModesEnum.list()
        assert val == 0 or val == 1
        self._mode[mode.value] = val


class BasePlayer:

    def __init__(self, indx: int, name: str, board: Board, discarded: DiscardPile):

        if not indx < board.num_players:
            raise IndexError

        self._indx = indx
        self._name = name
        self._board = board
        self._discarded = discarded

        self._cards = torch.zeros(len(CARDS.keys()), dtype=torch.uint8)
        self._coins = torch.tensor([0], dtype=torch.uint8)
        self._logger = logging.getLogger(name)

        self._beliefs = torch.rand(board.num_players, len(CARDS.keys()), requires_grad=True)
        self._beliefs = F.softmax(self._beliefs, dim=0)

        self._player_mode = PlayerModes()

    def __str__(self):
        return f"{self._name} (player #{self._indx})."

    def __repr__(self):
        return f"{str(self)} [cards={len(self._cards)} ; coins={self._coins}]"

    @property
    def board(self) -> torch.Tensor:
        return self._board.view(self._indx)

    @property
    def discarded(self) -> torch.Tensor:
        return self._discarded.view(self._indx)

    @property
    def cards(self) -> torch.Tensor:
        return self._cards

    @property
    def coins(self) -> torch.Tensor:
        return self._coins

    @property
    def state(self) -> Tuple:
        return (self.board, self.discarded, self.cards, self.coins, self._beliefs, self._player_mode._mode)

    def add_card(self, card: Card):
        card_idx = CARDS_TO_IDS[card]
        self._cards[card_idx] += 1
        assert self._cards[card_idx] <= NUM_CARDS_PER_TYPE
        self._board.add_player_cards(self._indx, 1)

    def sub_card(self, card: Card):
        card_idx = CARDS_TO_IDS[card]
        self._cards[card_idx] -= 1
        assert self._cards[card_idx] >= 0
        self._board.sub_player_cards(self._indx, 1)

    def add_coins(self, num_coins: int):
        self._coins = self._coins + num_coins
        self._board.add_player_coins(self._indx, num_coins)

    def sub_coins(self, num_coins: int):
        self._coins = self._coins - num_coins
        self._board.sub_player_coins(self._indx, num_coins)

    def has(self, card: Card) -> bool:
        card_idx = CARDS_TO_IDS[card]
        return self._cards[card_idx] > 0

    def income(self):
        self.add_coins(1)

    def foreign_aid(self):
        self.add_coins(2)

    def tax(self):
        self.add_coins(3)

    def coup(self):
        self.sub_coins(7)

    def assassinate(self):
        self.sub_coins(3)

    def steal(self):
        self.add_coins(2)


@contextmanager
def act(player, player_mode):
    """
    Context manager for players taking actions.
    :param player:
    :param player_mode:
    :return:
    """
    modes_stack = []
    try:
        player._player_mode.set(mode=player_mode, val=1)
        modes_stack.append(player_mode)
        yield
    finally:
        player._player_mode.set(mode=player_mode, val=0)
        modes_stack = modes_stack[:-1]


if __name__ == "__main__":
    board = Board(2)
    discarded = DiscardPile()
    asaf = BasePlayer(indx=0, name="Asaf Manor", board=board, discarded=discarded)
    hossein = BasePlayer(indx=1, name="Hossein Mousavi", board=board, discarded=discarded)
    print(asaf._player_mode._mode)
    with act(asaf, PlayerModesEnum.active):
        print(asaf._player_mode._mode)
        with act(asaf, PlayerModesEnum.challenged):
            print(asaf._player_mode._mode)
            with act(asaf, PlayerModesEnum.responding):
                print(asaf._player_mode._mode)
            print(asaf._player_mode._mode)
        print(asaf._player_mode._mode)
    print(asaf._player_mode._mode)
