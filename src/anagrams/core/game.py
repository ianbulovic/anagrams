from typing import Counter
from uuid import UUID

from .player import Player
from .utils import weighted_random_letter

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
        self.letter_pool_counter: Counter[str] = Counter()
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

    def add_letter(self, letter: str):
        self.letter_pool.append(letter)
        self.letter_pool_counter.update(letter)

    def remove_letter(self, letter: str):
        self.letter_pool.remove(letter)
        self.letter_pool_counter.subtract(letter)

    def new_letter(self, temperature: float = 0):
        letter = weighted_random_letter(temperature)
        self.add_letter(letter)

    def get_anagram_strategies(self, target: str):
        """
        Find all ways to assemble a target string by anagramming any number
        of player words and letter pool letters.
        """
        candidates: list[tuple[UUID | None, str, Counter[str]]] = []

        target_counter = Counter(target)
        for pid, player in self.players.items():
            for word in player.words:
                ctr = Counter(word)
                if ctr <= target_counter and not ctr == target_counter:
                    candidates.append((pid, word, Counter(word)))

        results: list[AnagramStrategy] = []
        current_strategy: list[tuple[UUID | None, str]] = []

        def backtrack(remaining: Counter, start: int):
            if remaining <= self.letter_pool_counter:
                strat = tuple(
                    current_strategy
                    + [(None, letter) for letter in remaining.elements()]
                )
                results.append(strat)
                return

            for i in range(start, len(candidates)):
                src, w, c = candidates[i]
                if not c <= remaining:
                    continue
                current_strategy.append((src, w))
                backtrack(remaining - c, i + 1)
                current_strategy.pop()

        backtrack(target_counter, 0)
        return results

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
                self.remove_letter(word)
            else:
                player = self.players[source]
                player.words.remove(word)

        self.log.append(strategy)
