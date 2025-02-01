import itertools
from typing import Counter
from uuid import UUID

from .player import Player
from .utils import contains_anagrammed_substring, weighted_random_letter

AnagramStrategy = tuple[tuple[UUID | None, str], ...]
"""
A tuple of (`source`, `word`) pairs, where `source` is a player id 
and `word` is one of that player's words. `source` can also be `None`, 
indicating a letter from the game's letter pool.
"""


class Game:
    """
    This class manages all state for a game of Anagrams.
    """

    def __init__(self):
        self.letter_pool: list[str] = []
        self.players: dict[UUID, Player] = {}
        self.turn_order: list[UUID] = []
        self._turn_idx: int = 0
        self.turns: int = 0
        self.log: list[AnagramStrategy] = []

    def add_player(self, player: Player):
        """Add a player to the game."""
        self.players[player.id] = player
        self.turn_order.append(player.id)

    def remove_player(self, player_id: UUID):
        """Remove the player with id `player_id` from the game."""
        self.players.pop(player_id)
        self.turn_order.remove(player_id)
        if self._turn_idx == len(self.players):
            self._turn_idx = 0

    @property
    def turn(self):
        """The player whose turn it is."""
        if len(self.turn_order) > 0:
            return self.players[self.turn_order[self._turn_idx]]
        return None

    def next_turn(self):
        """Advance the game to the next turn."""
        self._turn_idx += 1
        self._turn_idx %= len(self.turn_order)
        self.turns += 1

    def new_letter(self, temperature: float = 0):
        self.letter_pool.append(weighted_random_letter(temperature))

    def get_anagram_strategies(self, target: str):
        """
        Find all ways to assemble a target string by anagramming any number
        of player words and letter pool letters.
        """
        candidates: list[tuple[UUID | None, str]] = [
            (None, letter) for letter in self.letter_pool if letter in target
        ]
        for id, player in self.players.items():
            candidates.extend(
                [
                    (id, w)
                    for w in player.words
                    if contains_anagrammed_substring(target, w)
                ]
            )
        strategies: list[AnagramStrategy] = []
        target_counter = Counter(target)
        for n in range(2, len(candidates) + 1):
            for combo in itertools.combinations(candidates, n):
                if target_counter == Counter("".join([sub for _, sub in combo])):
                    strategies.append(combo)
        return strategies

    def validate_anagram_strategy(self, strategy: AnagramStrategy):
        """Checks if an anagram strategy can be executed."""
        for source, word in strategy:
            if source is None:
                if word not in self.letter_pool:
                    return False
            else:
                player = self.players[source]
                if word not in player.words:
                    return False
        return True

    def execute_anagram_strategy(self, strategy: AnagramStrategy):
        """
        Executes an anagram strategy, removing words and letters from
        players and the letter pool as needed.
        """
        for source, word in strategy:
            if source is None:
                self.letter_pool.remove(word)
            else:
                player = self.players[source]
                player.words.remove(word)

        self.log.append(strategy)
