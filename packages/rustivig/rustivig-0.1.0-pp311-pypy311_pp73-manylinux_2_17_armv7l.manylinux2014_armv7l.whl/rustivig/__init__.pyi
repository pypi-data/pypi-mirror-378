"""
A Rust implementation of Peter Norvig's spell corrector algorithm for use in Python
"""

from typing import Dict, List, Set


def build_word_frequency_dictionary(charset: str, corpus: str) -> Dict[str, int]:
    """Extract and build a word frequency dictionary from the given corpus

    :param charset: A charset that what are words made of
    :type charset: str
    :param corpus: A source of words for extracting words and building word frequency
        dictionary out of them
    :type corpus: str
    :return: A word frequency dictionary made out of the words extracted from the corpus
    :rtype: Dict[str, int]
    """


def correct(charset: str, word: str, word_frequency_dictionary: Dict[str, int]) -> str:
    """Correct the potential misspelled word

    :param charset: A charset that what are words made of
    :type charset: str
    :param word: A potential misspelled word
    :type word: str
    :param word_frequency_dictionary: A dictionary of `word: frequency` pairs
    :type word_frequency_dictionary: Dict[str, int]
    :return: Potential corrected word
    """


def extract_words(charset: str, corpus: str) -> List[str]:
    """Extract the words from the given corpus

    :param charset: A charset that what are words made of
    :type charset: str
    :param corpus: A source of words for extracting words and building word frequency
        dictionary out of them
    :type corpus: str
    :return: A list of words extracted from the corpus
    :rtype: List[str]
    """


def get_candidates(charset: str, word: str, word_frequency_dictionary: Dict[str, int]) -> Set[str]:
    """Find the similiar words to the `word` that is correctly spelled

    :param charset: A charset that what are words made of
    :type charset: str
    :param word: A potential misspelled word
    :type word: str
    :param word_frequency_dictionary: A dictionary of `word: frequency` pairs
    :type word_frequency_dictionary: Dict[str, int]
    :return: A set of similiar words to the `word` that is correctly spelled
    :rtype: Set[str]
    """


def get_distance_1_edits(charset: str, word: str) -> Set[str]:
    """Get a set of distance 1 edits of a word

    :param charset: A charset that what are words made of
    :type charset: str
    :param word: A word
    :type word: str
    :return: A set of distance 1 edits of the given word
    :rtype: Set[str]
    """


def get_distance_2_edits(charset: str, word: str) -> Set[str]:
    """Get a set of distance 2 edits of a word

    :param charset: A charset that what are words made of
    :type charset: str
    :param word: A word
    :type word: str
    :return: A set of distance 2 edits of the given word
    :rtype: Set[str]
    """


def get_known_distance_1_edits(charset: str, word: str, word_frequency_dictionary: Dict[str, int]) -> Set[str]:
    """Get a set of known distance 1 edits of a word

    :param charset: A charset that what are words made of
    :type charset: str
    :param word: A word
    :type word: str
    :param word_frequency_dictionary: A dictionary of `word: frequency` pairs
    :type word_frequency_dictionary: Dict[str, int]
    :return: A set of known distance 1 edits of the given word
    :rtype: Set[str]
    """


def get_known_distance_2_edits(charset: str, word: str, word_frequency_dictionary: Dict[str, int]) -> Set[str]:
    """Get a set of known distance 2 edits of a word

    :param charset: A charset that what are words made of
    :type charset: str
    :param word: A word
    :type word: str
    :param word_frequency_dictionary: A dictionary of `word: frequency` pairs
    :type word_frequency_dictionary: Dict[str, int]
    :return: A set of known distance 2 edits of the given word
    :rtype: Set[str]
    """


def get_known_words(words: Set[str], word_frequency_dictionary: Dict[str, int]) -> Set[str]:
    """Select a set of known words from the `words` set

    :param words: A set of words
    :type words: Set[str]
    :param word_frequency_dictionary: A dictionary of `word: frequency` pairs
    :type word_frequency_dictionary: Dict[str, int]
    :return: A set of known words selected from the `words` set
    :rtype: Set[str]
    """


def get_probability(word: str, word_frequency_dictionary: Dict[str, int]) -> float:
    """Get probability of a word based on the given word frequency dictionary.
    `word_frequency_dictionary.get(word) / sum(word_frequency_dictionary.values())`

    :param word: A word
    :type word: str
    :param word_frequency_dictionary: A dictionary of `word: frequency` pairs
    :type word_frequency_dictionary: Dict[str, int]
    :return: Probability of a word based on the given word frequency dictionary
    :rtype: float
    """
