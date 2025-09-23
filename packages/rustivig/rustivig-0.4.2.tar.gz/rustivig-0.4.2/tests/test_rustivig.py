import pytest
import rustivig
import time
from spellchecker import SpellChecker

CHARSET = ''.join(SpellChecker().word_frequency.letters)
DICT = {"hello": 100, "world": 90, "complex": 80, "algorithm": 70}


def test_simple_correction():
    result = rustivig.correct(CHARSET, "helo", DICT, False)
    assert result == "hello"


def test_batch_vs_single():
    start = time.time()
    for _ in range(100):
        rustivig.correct(CHARSET, "helo", DICT, False)
    single_time = time.time() - start

    words: set[str] = set(("helo",) * 100)
    start = time.time()
    rustivig.correct_batch(CHARSET, words, DICT, False)
    batch_time = time.time() - start

    print(f"Single: {single_time:.3f}s, Batch: {batch_time:.3f}s")
    print(f"Speedup: {single_time / batch_time:.1f}x")


def test_vs_pyspellchecker():
    spell = SpellChecker()
    word = "complexityyy"

    start = time.time()
    for _ in range(10):
        rustivig.correct(CHARSET, word, DICT, False)
    rustivig_time = time.time() - start

    start = time.time()
    for _ in range(10):
        spell.correction(word)
    pyspell_time = time.time() - start

    print(f"Rustivig: {rustivig_time:.3f}s")
    print(f"PySpellChecker: {pyspell_time:.3f}s")
    print(f"Ratio: {pyspell_time / rustivig_time:.1f}x")


def test_unicode_support():
    charset = "abcdefghijklmnopqrstuvwxyzسلام"
    dictionary = {"complexities": 100, "سلام": 90}

    start = time.time()
    result = rustivig.correct(charset, "complexitiieis", dictionary, False)
    unicode_time = time.time() - start

    print(f"Unicode correction time: {unicode_time:.4f}s")
    assert result == "complexities"


def test_threading_vs_no_threading():
    words = {"complexityyy", "algorithmm", "performanc", "optimiztion"}

    start = time.time()
    result1 = rustivig.correct_batch(CHARSET, words, DICT, False)
    no_threading_time = time.time() - start

    start = time.time()
    result2 = rustivig.correct_batch(CHARSET, words, DICT, True)
    threading_time = time.time() - start

    print(f"No threading: {no_threading_time:.4f}s")
    print(f"With threading: {threading_time:.4f}s")
    print(f"Threading speedup: {no_threading_time/threading_time:.1f}x")

    assert result1 == result2
