from __future__ import annotations

import logging
from typing import Sequence, Tuple

from action import ACTION_TO_COUNTER_ACTION, Action
from cards import Card, CardList
from deck import CheatingError, Deck
from state import ObservableState


class InsufficientFundsError(Exception):
    pass


# TODO: add a belief state per player for the distribution of cards across the game
class Player:
    def __init__(self, name: str):
        self.name = name
        self._cards: CardList = None
        self._coins = 0
        self.logger = logging.getLogger(name=name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @property
    def cards(self):
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

        # TODO add assertion that no card is both in the deck and in a player's hand!

    def do_challenge(self, source, action: Action, state: ObservableState) -> bool:
        if action in [Action.INCOME, Action.FOREIGNAID, Action.COUP]:
            return False

        challange = self._do_challenge(source, action, state)
        assert isinstance(challange, bool)
        if challange:
            self.logger.info(f"Challanged action {action} of player {source}")
        return challange

    def do_action(
        self, players: Sequence[Player], state: ObservableState
    ) -> Tuple[Action, None]:
        action, target = self._do_action(players, state)
        assert isinstance(action, Action)
        if target:
            assert isinstance(target, Player)
        if target is not None:
            self.logger.info(f"Attempts action {action} on player {target}")
        else:
            self.logger.info(f"Attempts action {action}")

        return action, target

    def __do_counter_action__(
        self, action: Action, source: Player, state: ObservableState
    ) -> Tuple[bool, str]:
        counter_action, with_card = self._do_counter_action(action, source, state)
        assert isinstance(counter_action, bool)
        if with_card:
            assert isinstance(with_card, str)

        if counter_action:
            counter_action_type = ACTION_TO_COUNTER_ACTION[action]
            self.logger.info(
                f"Performs counter-action {counter_action_type} with {with_card} on {source}"
            )
        else:
            self.logger.info(f"Does not counter {action} by {source}")
        return counter_action, with_card

    def counter_foreign_aid(
        self, source: Player, state: ObservableState
    ) -> Tuple[bool, str]:
        ca, with_card = self.__do_counter_action__(Action.FOREIGNAID, source, state)
        if ca:
            assert with_card == "Duke"
        return ca, with_card

    def counter_assassinate(
        self, source: Player, discard_pile: CardList, state: ObservableState
    ) -> Tuple[bool, str]:
        """Called when you the player is the target of an assassination."""
        ca, with_card = self.__do_counter_action__(Action.ASSASSINATION, source, state)
        if ca:
            assert with_card == "Contessa"
        else:
            self.lose_influence(discard_pile)
        return ca, with_card

    def counter_steal(self, source: Player, state: ObservableState) -> bool:
        """Called when you the player is the target of stealing."""
        ca, with_card = self.__do_counter_action__(Action.STEAL, source, state)
        if ca:
            assert with_card in ["Captain", "Ambassador"]
        else:
            self.coins -= 2
        return ca, with_card

    def lose_influence(self, discard_pile: CardList):
        # TODO: move appending to discard_pile into the Game controller
        card = self._lose_influence()
        self.logger.info(f"Lost a {card.name} influence")
        discard_pile.append(card)

    def _lose_influence(self) -> Card:
        raise NotImplementedError

    def _exchange(self, extra_cards: CardList) -> CardList:
        raise NotImplementedError

    def _do_counter_action(
        self, action: Action, source: Player, state: ObservableState
    ) -> Tuple[bool, str]:
        raise NotImplementedError

    def _do_action(
        self, players: Sequence[Player], state: ObservableState
    ) -> Tuple[Action, Player]:
        raise NotImplementedError

    def _do_challenge(
        self, source: Player, action: Action, state: ObservableState
    ) -> bool:
        raise NotImplementedError
