# -*- coding: utf-8 -*-

import re
import string
from collections import Counter
import numpy as np


def read_corpus(filename):
    """
    Reads the contents of a file and returns a list of lowercase words.

    Args:
        filename (str): The file path to be read.

    Returns:
        list: A list of lowercase words in the file.
    """
    with open(filename, "r") as file:
        lines = file.readlines()
        words = []
        for line in lines:
            words += re.findall(r'\w+', line.lower())

        return words


words = read_corpus("./english.txt")
print(f"There are {len(words)} total words in the corpus")

vocabs = set(words)
print(f"There are {len(vocabs)} unique words in the vocabulary")

word_counts = Counter(words)
print(word_counts["love"])

total_word_count = float(sum(word_counts.values()))
word_probas = {word: word_counts[word] /
               total_word_count for word in word_counts.keys()}

print(word_probas["love"])


def split(word):
    return [(word[:i], word[i:]) for i in range(len(word) + 1)]


"""
    Splits a given word into all possible combinations of two substrings. 

    Parameters:
    word (str): The word to be split.

    Returns:
    list of tuples: A list of tuples containing all possible combinations of two substrings
    of the input word. The first element of each tuple is the substring before the split point,
    and the second element is the substring after the split point.
    """

print(split("trash"))


def delete(word):
    """
    Given a word, this function returns a list of all possible strings that can be
    created by deleting one letter from the input word. The input word is split
    into two parts, the left part and the right part, and for every character in the
    right part, we create a new string by concatenating the left part with the right
    part without the character. The resulting list is returned. The input is a
    string, and the output is a list of strings.
    """
    return [l + r[1:] for l, r in split(word) if r]


print(delete("trash"))


def swap(word):
    return [l + r[1] + r[0] + r[2:] for l, r in split(word) if len(r) > 1]


print(swap("trash"))

string.ascii_lowercase


def replace(word):
    letters = string.ascii_lowercase
    return [l + c + r[1:] for l, r in split(word) if r for c in letters]


print(replace("trash"))


def insert(word):
    letters = string.ascii_lowercase
    return [l + c + r for l, r in split(word) for c in letters]


print(insert("trash"))


def edit1(word):
    return set(delete(word) + swap(word) + replace(word) + insert(word))


print(edit1("trash"))


def edit2(word):
    return set(e2 for e1 in edit1(word) for e2 in edit1(e1))


print(edit2("trash"))


def correct_spelling(word, vocabulary, word_probabilities):
    if word in vocabulary:
        print(f"{word} is already correctly spelt")
        return

    suggestions = edit1(word) or edit2(word) or [word]
    best_guesses = [w for w in suggestions if w in vocabulary]
    return [(w, word_probabilities[w]) for w in best_guesses]


word = "famile"
corrections = correct_spelling(word, vocabs, word_probas)

if corrections:
    print(corrections)
    probs = np.array([c[1] for c in corrections])
    best_ix = np.argmax(probs)
    correct = corrections[best_ix][0]
    print(f"{correct} is suggested for {word}")


class SpellChecker(object):

    def __init__(self, corpus_file_path):
        with open(corpus_file_path, "r") as file:
            lines = file.readlines()
            words = []
            for line in lines:
                words += re.findall(r'\w+', line.lower())

        self.vocabs = set(words)
        self.word_counts = Counter(words)
        total_words = float(sum(self.word_counts.values()))
        self.word_probas = {
            word: self.word_counts[word] / total_words for word in self.vocabs}

    def _level_one_edits(self, word):
        """
        This function takes a word as input, and generates all possible one-edit-distance variations of it. It returns a set of all such variations.
        """
        letters = string.ascii_lowercase
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [l + r[1:] for l, r in splits if r]
        swaps = [l + r[1] + r[0] + r[2:] for l, r in splits if len(r) > 1]
        replaces = [l + c + r[1:] for l, r in splits if r for c in letters]
        inserts = [l + c + r for l, r in splits for c in letters]

        return set(deletes + swaps + replaces + inserts)

    def _level_two_edits(self, word):
        """
        Returns a set of level two edits for a given word.

        :param word: A string representing the word to generate level two edits.
        :type word: str
        :return: A set of level two edits for the given word.
        :rtype: set
        """
        return set(e2 for e1 in self._level_one_edits(word) for e2 in self._level_one_edits(e1))

    def check(self, word):
        """
        This method takes a word and checks for possible suggestions. The method first generates a list of candidate suggestions by applying level one edits to the input word. If no valid candidates are found, the method applies level two edits to the input word. If still no valid candidates are found, the input word is returned as a valid candidate. The method then filters the valid candidates by checking if they exist in the vocabulary set and then returns a sorted list of tuples containing the valid candidates and their corresponding probabilities. 

        :param word: A string representing the word to be checked for suggestions.
        :return: A sorted list of tuples where each tuple contains a valid candidate suggestion and its corresponding probability.
        """
        candidates = self._level_one_edits(
            word) or self._level_two_edits(word) or [word]
        valid_candidates = [w for w in candidates if w in self.vocabs]
        return sorted([(c, self.word_probas[c]) for c in valid_candidates], key=lambda tup: tup[1],  reverse=True)


checker = SpellChecker("./english.txt")

checker.check("obstreperos")
