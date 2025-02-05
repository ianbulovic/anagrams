from anagrams.core.dictionary import Dictionary, same_root


def test_load_default():
    # 2of12inf dictionary (http://wordlist.aspell.net/12dicts/)
    d = Dictionary.load_from_file()
    assert len(d) == 75535


def test_same_root():
    assert same_root("anagram", "anagrams")
    assert same_root("play", "played")
    assert same_root("test", "testing")
    assert same_root("great", "greater")
