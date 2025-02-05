import functools
import os
import re
from typing import Iterable

from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()


class TrieNode:  # TODO needs tests but i think it works
    def __init__(self, terminal: bool = False) -> None:
        self.children: dict[str, TrieNode] = {}
        self.terminal: bool = terminal

    def add(self, value: str):
        if value == "":
            self.terminal = True
            return
        i = 0
        for k in self.children.keys():
            if k[0] == value[0]:
                terminal = False
                while k[i] == value[i]:
                    i += 1
                    if i == len(k):
                        self.children[k].add(value.removeprefix(k))
                        return
                    if i == len(value):
                        terminal = True
                        break
                branch = TrieNode(terminal)
                existing_word = self.children.pop(k)
                common_prefix = k[:i]
                existing_suffix = k[i:]
                new_suffix = value[i:]

                self.children[common_prefix] = branch
                branch.children[existing_suffix] = existing_word
                if not terminal:
                    branch.children[new_suffix] = TrieNode(True)

                break
        else:
            self.children[value] = TrieNode(True)

    def __contains__(self, value: str):
        if not isinstance(value, str):
            return False
        if value == "":
            return self.terminal
        i = 0
        for k in self.children.keys():
            if k[0] == value[0]:
                while k[i] == value[i]:
                    i += 1
                    if i == len(k):
                        return self.children[k].__contains__(value[i:])
                    if i == len(value):
                        return False
                return False
        return False


SCRABBLE_DICTIONARY_FILE = os.path.join(os.path.split(__file__)[0], "scrabble.txt")
TWO_OF_TWELVE_INF_FILE = os.path.join(os.path.split(__file__)[0], "2of12inf.txt")
DEFAULT_DICTIONARY_FILE = TWO_OF_TWELVE_INF_FILE


class Dictionary:
    def __init__(self, words: Iterable[str] | None = None) -> None:
        self.root = TrieNode()
        self._size = 0
        for word in words or []:
            self.add_word(word)

    @classmethod
    def load_from_file(
        cls,
        filepath: str = DEFAULT_DICTIONARY_FILE,
        pattern: str | None = None,
    ):
        rgx = None
        if pattern is not None:
            rgx = re.compile(pattern)

        def _iter():
            with open(filepath) as f:
                if rgx is None:
                    for line in f:
                        line = line.strip()
                        if line:
                            yield line
                else:
                    for line in f:
                        line = line.strip()
                        if line and rgx.fullmatch(line) is not None:
                            yield line

        return Dictionary(_iter())

    def add_word(self, word: str):
        if word not in self:
            self.root.add(word)
            self._size += 1

    def __contains__(self, word: str):
        return word in self.root

    def __len__(self):
        return self._size


@functools.cache
def same_root(word_1: str, word_2: str):
    def lemma_set(word: str):
        return {lemmatizer.lemmatize(word, pos) for pos in "nvars"}

    return len(lemma_set(word_1).intersection(lemma_set(word_2))) > 0
