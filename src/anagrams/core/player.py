from dataclasses import dataclass
from uuid import UUID


@dataclass
class Player:
    id: UUID
    name: str
    words: list[str]
    """A list of words that the player has found"""

    @property
    def score(self):
        return sum(len(w) for w in self.words)
