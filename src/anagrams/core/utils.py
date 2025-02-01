from collections import Counter
from collections.abc import Iterable
from random import random


def contains_anagrammed_substring(word: str, sub: str):
    w_counter = Counter(word)
    s_counter = Counter(sub)
    for letter in s_counter:
        if letter not in w_counter or w_counter[letter] < s_counter[letter]:
            return False
    return True


def is_anagram(target: str, pieces: Iterable[str]):
    return Counter(target) == Counter("".join(pieces))


# fmt: off
LETTER_WEIGHTS = {
    "e": 12.0, "t": 9.10, "a": 8.12, "o": 7.68, "i": 7.31,
    "n": 6.95, "s": 6.28, "r": 6.02, "h": 5.92, "d": 4.32,
    "l": 3.98, "u": 2.88, "c": 2.71, "m": 2.61, "f": 2.30,
    "y": 2.11, "w": 2.09, "g": 2.03, "p": 1.82, "b": 1.49, 
    "v": 1.11, "k": 0.69, "x": 0.17, "q": 0.11, "j": 0.10,
    "z": 0.07,
}
# fmt: on


def weighted_random_letter(temperature: float):
    total = sum(w + temperature for w in LETTER_WEIGHTS.values())
    target = random() * total
    for letter, weight in LETTER_WEIGHTS.items():
        target -= weight + temperature
        if target < 0:
            return letter
    return "E"
