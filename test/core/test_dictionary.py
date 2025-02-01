from anagrams.core.dictionary import Dictionary


def test_load_default():
    d = Dictionary.load_from_file()  # scrabble dictionary
    assert len(d) == 178691
