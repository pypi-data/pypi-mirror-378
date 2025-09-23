"""
A Rust implementation of Peter Norvig's spell corrector algorithm for use in Python
"""

from typing import Dict, List, Set

def build_word_frequency_dictionary(charset: str, corpus: str) -> Dict[str, int]:
    """Build a word frequency dictionary from text corpus.

    Extracts words from the corpus using the given charset and counts their frequencies.
    Words are identified as sequences of characters that exist in the charset.

    Args:
        charset: Characters that define valid word components (e.g., "abcdefg...")
        corpus: Text to extract words from

    Returns:
        Dictionary mapping words to their frequency counts

    Example:
        >>> charset = "abcdefghijklmnopqrstuvwxyz"
        >>> corpus = "hello world hello"
        >>> build_word_frequency_dictionary(charset, corpus)
        {'hello': 2, 'world': 1}
    """

def correct(
    charset: str, word: str, dictionary: Dict[str, int], use_threading: bool = False
) -> str:
    """Auto-correct a potentially misspelled word.

    Finds the most likely correct spelling by selecting the dictionary word with
    the highest frequency among candidates within edit distance.

    Args:
        charset: Characters that define valid word components
        word: Word that might be misspelled
        dictionary: Word frequency dictionary (word -> count)
        use_threading: Enable parallel processing for better performance

    Returns:
        Most likely correct spelling, or original word if no candidates found

    Example:
        >>> correct("abc...", "helo", {"hello": 100, "help": 50})
        "hello"
    """

def correct_batch(
    charset: str,
    words: Set[str],
    dictionary: Dict[str, int],
    use_threading: bool = False,
) -> Dict[str, str]:
    """Auto-correct multiple words efficiently.

    Batch processing eliminates Python-Rust overhead and provides significant
    performance improvements over individual corrections.

    Args:
        charset: Characters that define valid word components
        words: Set of potentially misspelled words
        dictionary: Word frequency dictionary (word -> count)
        use_threading: Enable parallel processing for better performance

    Returns:
        Dictionary mapping each input word to its best correction

    Example:
        >>> correct_batch("abc...", {"helo", "wrld"}, {"hello": 100, "world": 90})
        {"helo": "hello", "wrld": "world"}
    """

def extract_words(charset: str, corpus: str) -> List[str]:
    """Extract all words from text corpus.

    Splits the corpus into words using the charset to identify valid characters.
    Returns words in the order they appear (may contain duplicates).

    Args:
        charset: Characters that define valid word components
        corpus: Text to extract words from

    Returns:
        List of words found in the corpus (preserves order and duplicates)

    Example:
        >>> extract_words("abc...", "Hello, world! Hello again.")
        ["Hello", "world", "Hello", "again"]
    """

def get_candidates(
    charset: str,
    word: str,
    word_frequency_dictionary: Dict[str, int],
    use_threading: bool = False,
) -> Set[str]:
    """Find spelling correction candidates for a word.

    Generates words within edit distance 1-2 and returns those found in the dictionary.
    Uses early termination - if edit distance 1 candidates exist, distance 2 are skipped.

    Args:
        charset: Characters that define valid word components
        word: Word to find candidates for
        word_frequency_dictionary: Word frequency dictionary (word -> count)
        use_threading: Enable parallel processing for better performance

    Returns:
        Set of dictionary words that could be corrections for the input word

    Example:
        >>> get_candidates("abc...", "helo", {"hello": 100, "help": 50})
        {"hello", "help"}
    """

def get_candidates_batch(
    charset: str,
    words: Set[str],
    dictionary: Dict[str, int],
    use_threading: bool = False,
) -> Dict[str, Set[str]]:
    """Find correction candidates for multiple words efficiently.

    Batch processing provides significant performance improvements over individual
    candidate generation calls.

    Args:
        charset: Characters that define valid word components
        words: Set of words to find candidates for
        dictionary: Word frequency dictionary (word -> count)
        use_threading: Enable parallel processing for better performance

    Returns:
        Dictionary mapping each input word to its set of correction candidates

    Example:
        >>> get_candidates_batch("abc...", {"helo", "tset"}, {"hello": 100, "test": 90})
        {"helo": {"hello"}, "tset": {"test"}}
    """

def get_distance_1_edits(
    charset: str, word: str, filter_known: bool = False, use_threading: bool = False
) -> Set[str]:
    """Generate all words within edit distance 1 of the input word.

    Creates variations by: deleting characters, inserting characters from charset,
    substituting characters, and transposing adjacent characters.

    Args:
        charset: Characters that can be used for insertions and substitutions
        word: Base word to generate edits from
        filter_known: If True, only return edits that exist in a known dictionary
        use_threading: Enable parallel processing for better performance

    Returns:
        Set of all possible 1-edit variations of the word

    Note:
        Can generate thousands of candidates for long words. Use filter_known=True
        if you have a dictionary to reduce memory usage.
    """

def get_distance_2_edits(
    charset: str, word: str, filter_known: bool = False, use_threading: bool = False
) -> Set[str]:
    """Generate all words within edit distance 2 of the input word.

    Creates variations by applying two edit operations. This can generate very large
    candidate sets for long words (potentially millions of candidates).

    Args:
        charset: Characters that can be used for insertions and substitutions
        word: Base word to generate edits from
        filter_known: If True, only return edits that exist in a known dictionary
        use_threading: Enable parallel processing for better performance

    Returns:
        Set of all possible 2-edit variations of the word

    Warning:
        Can generate extremely large result sets. Consider using filter_known=True
        or limiting to shorter words to avoid memory issues.
    """

def get_known_words(
    words: Set[str],
    word_frequency_dictionary: Dict[str, int],
    use_threading: bool = False,
) -> Set[str]:
    """Filter words to only those present in the dictionary.

    Efficiently checks which words from the input set exist in the dictionary.
    Useful for filtering large candidate sets to only valid words.

    Args:
        words: Set of words to check
        word_frequency_dictionary: Word frequency dictionary (word -> count)
        use_threading: Enable parallel processing for better performance

    Returns:
        Subset of input words that exist in the dictionary

    Example:
        >>> get_known_words({"hello", "xyz123", "world"}, {"hello": 100, "world": 90})
        {"hello", "world"}
    """

def get_probability(word: str, word_frequency_dictionary: Dict[str, int]) -> float:
    """Calculate the probability of a word based on frequency data.

    Computes: word_frequency / total_frequency_sum
    Returns 0.0 for words not in the dictionary.

    Args:
        word: Word to calculate probability for
        word_frequency_dictionary: Word frequency dictionary (word -> count)

    Returns:
        Probability value between 0.0 and 1.0

    Example:
        >>> get_probability("hello", {"hello": 2, "world": 1})
        0.6666666666666666  # 2/(2+1)
    """
