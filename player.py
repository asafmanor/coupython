from __future__ import annotations

import logging
from typing import Sequence, Tuple

import numpy as np

from action import Action
from cards import Card, CardList
from deck import Deck, CheatingError


class InsufficientFundsError(Exception):
    pass


# TODO: add a belief state per player for the distribution of cards across the game
class Player:
    # methods beginning with target_ are called when you are the target of an action
    # Gaming logic should only be implemented in subclasses of Player
    def __init__(self, name: str):
        self.name = name
        self.cards: CardList = None
        self.logger = logging.getLogger(name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @property
    def cards(self):
        self.logger.debug(
            "Cards can't be accessed. If the cards must be accessed, use `self._cards`"
        )
        raise CheatingError("Can't look at a player's cards.")

    @cards.setter
    def cards(self, cards: CardList):
        self._cards = cards

    @property
    def num_cards(self):
        return len(self._cards)

    @property
    def coins(self) -> int:
        return self._coins

    @coins.setter
    def coins(self, value):
        if value < 0:
            raise InsufficientFundsError
        self._coins = value

    def has(self, card_name: str) -> bool:
        return self._cards.has(card_name)

    def get(self, card_name: str) -> Card:
        return self._cards.get(card_name)

    def income(self):
        self.coins += 1

    def foreign_aid(self):
        self.coins += 2

    def tax(self):
        self.coins += 3

    def coup(self):
        self.coins -= 7

    def assassinate(self):
        self.coins -= 3

    def steal(self):
        self.coins += 2

    def replace(self, card_name: str, deck: Deck):
        deck.return_cards(CardList([self.get(card_name)]))
        deck._shuffle()
        self._cards.append(deck.draw_card())

    def exchange(self, deck: Deck):
        card_1 = deck.draw_card()
        card_2 = deck.draw_card()
        current_num_cards = len(self._cards)
        return_cards = self._exchange(CardList([card_1, card_2]))

        deck.return_cards(return_cards)
        deck._shuffle()

        if current_num_cards != len(self._cards):
            raise RuntimeError(
                "Number of cards returned from _exchange "
                + f"is inequivalent to {current_num_cards}"
            )

    def do_challenge(self, source, action: Action) -> bool:
        if action in [Action.INCOME, Action.FOREIGNAID, Action.COUP]:
            return False

        challange = self._do_challenge(source, action)
        if challange:
            self.logger.info(f"Challanged action {action} of player {source}")
        return challange

    def do_action(self, players: Sequence[Player]) -> Tuple[Action, None]:  # TODO change to state. this is PI.
        action, target = self._do_action(players)
        if target is not None:
            self.logger.info(f"Attempts action {action} on player {target}")
        else:
            self.logger.info(f"Attempts action {action}")

        return action, target

    def do_counter_action(self, action: Action, source: Player) -> bool:
        counter_action = self._do_counter_action(action, source)
        if counter_action is not None:
            self.logger.info(f"Performed counter-action {counter_action}")
            return True

        return False

    def target_assassinate(self, source: Player, discard_pile: CardList) -> bool:
        """Called when you the player is the target of an assassination."""
        counter_action = self.do_counter_action(Action.ASSASS, source)
        if not counter_action:
            self.lose_influence(discard_pile)

        return counter_action

    def target_steal(self, source: Player) -> bool:
        """Called when you the player is the target of stealing."""
        counter_action = self.do_counter_action(Action.STEAL, source)
        if counter_action is False:
            self.coins -= 2

        return counter_action

    def target_coup(self, discard_pile: CardList):
        return self.lose_influence(discard_pile)

    def lose_influence(self, discard_pile: CardList) -> int:
        card = self._lose_influence()
        self.logger.info(f"Lost a {card.name} influence")
        discard_pile.append(card)
        return len(self._cards)

    def _lose_influence(self) -> Card:
        raise NotImplementedError

    def _exchange(self, extra_cards: CardList) -> CardList:
        raise NotImplementedError

    def _do_counter_action(self, action: Action, source: Player) -> Action:
        raise NotImplementedError

    def _do_action(
        self, players: Sequence[Player]
    ) -> Tuple[Action, None]:  # Actually, returns a different player
        raise NotImplementedError

    def _do_challenge(self, source: Player, action: Action) -> bool:
        raise NotImplementedError


import torch
import torch.nn.functional as F

from board import Board
from card import CARDS
from cards import DiscardPile
from typing import List


class BasePlayer:

    def __init__(self, indx: int, name: str, board: Board, discarded: DiscardPile):
        self._indx = indx
        self._name = name
        self._board = board
        self._discarded = discarded

        self._cards: List[Card] = []
        self._coins: int = 0
        self._logger = logging.getLogger(name)

        self._beliefs = torch.rand(board.num_players, len(CARDS.keys()), requires_grad=True)
        self._beliefs = F.softmax(self._beliefs, dim=0)

    def __str__(self):
        return f"{self._name} (player #{self._indx})."

    def __repr__(self):
        return f"{str(self)} [cards={len(self._cards)} ; coins={self._coins}]"

    @property
    def board(self) -> torch.Tensor:
        return self._board.view(self._indx)

    @property
    def state(self) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        return (self.board, self._discarded.cards, self._beliefs)

    @property
    def cards(self) -> List[Card]:
        return self._cards

    @cards.setter
    def cards(self, x):
        raise PermissionError

    @property
    def coins(self) -> int:
        return self._coins

    @coins.setter
    def coins(self, x):
        raise PermissionError

    def add_card(self, card: Card):
        self._cards.append(card)
        self._board.add_player_cards(self._indx, 1)

    def sub_card(self, card: Card):
        self._cards.remove(card)
        self._board.sub_player_cards(self._indx, 1)

    def add_coins(self, num_coins: int):
        self._coins = self._coins + num_coins
        self._board.add_player_coins(self._indx, num_coins)

    def sub_coins(self, num_coins: int):
        self._coins = self._coins - num_coins
        self._board.sub_player_coins(self._indx, num_coins)

    def has(self, card: Card) -> bool:
        return type(card) in self._cards

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