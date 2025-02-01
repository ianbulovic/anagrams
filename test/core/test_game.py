from uuid import uuid4

from anagrams.core import Game, Player


def test_assembly_strategies():
    game = Game()
    game.letter_pool = ["a", "s"]
    game.add_player(Player(id=uuid4(), name="Player 1", words=["man", "gram"]))
    game.add_player(Player(id=uuid4(), name="Player 2", words=["rag", "nags", "mar"]))

    assert len(game.get_anagram_strategies("grass")) == 0
    assert len(game.get_anagram_strategies("as")) == 1  # a s
    assert len(game.get_anagram_strategies("grams")) == 1  # gram s
    assert len(game.get_anagram_strategies("anagrams")) == 2  # a nags mar, a s man rag
