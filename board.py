import torch


class Board:

    def __init__(self, num_players: int):
        self._players = torch.zeros((num_players, 2), dtype=torch.uint8, requires_grad=False)

    @property
    def shape(self):
        return self._players.shape

    @property
    def num_players(self):
        return self.shape[0]

    def view(self, player: int) -> torch.Tensor:
        """
        Return a new board as viewed by the player.

        Args:
            player: Player's index.

        Returns:
            torch tensor of shape (num_players, 2), where the 1st row is the state of the player,
            the 2nd row is the state of the player to her left, ... the last row is of the player to her right.
        """
        return torch.roll(self._players, player, dims=0)

    def add_player_cards(self, player: int, num_cards: int = 1):
        """
        Adds card/s to the player's cards count.

        Args:
            player: Player's index.
            num_cards: number of cards to add to count.
        """
        assert 0 <= player < self._num_players
        self._players[player][0] = self._players[player][0] + num_cards

    def sub_player_cards(self, player: int, num_cards: int = 1):
        """
        Subtracts card/s to the player's cards count.

        Args:
            player: Player's index.
            num_cards: number of cards to subtract from count.
        """
        assert 0 <= player < self._num_players
        self._players[player][0] = self._players[player][0] - num_cards

    def add_player_coins(self, player: int, num_coins: int = 1):
        """
        Adds coin/s to the player's cards count.

        Args:
            player: Player's index.
            num_coins: number of coins to add to count.
        """
        assert 0 <= player < self._num_players
        self._players[player][1] = self._players[player][1] + num_coins

    def sub_player_coins(self, player: int, num_coins: int = 1):
        """
        Subtract coin/s to the player's cards count.

        Args:
            player: Player's index.
            num_coins: number of coins to subtract from count.
        """
        assert 0 <= player < self._num_players
        self._players[player][1] = self._players[player][1] - num_coins
