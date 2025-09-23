# Rustivig
<p align="center">
    <em>🧙 A Rust implementation of Peter Norvig's spell corrector algorithm for use in Python</em>
    <br>
    <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/ashkanfeyzollahi/rustivig">
    <img alt="GitHub License" src="https://img.shields.io/github/license/ashkanfeyzollahi/rustivig">
    <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/rustivig">
    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/rustivig">
    <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/ashkanfeyzollahi/rustivig/CI.yml">
</p>

**Rustivig** brings Peter Norvig's spell corrector algorithm to Python, but written in Rust for serious performance gains.

It delivers **6x faster** complex corrections than pyspellchecker, **88x speedup** with batch processing, and **2.3x improvement** with threading. While simple single-word corrections might be slower due to Python-Rust overhead, Rustivig excels where it counts - complex misspellings and batch processing. The goal is to make the fastest spell checker based on Norvig's algorithm - contributions welcome!

## Why Rustivig?

* **Fast where it counts** - handles complex misspellings much faster than pure Python
* **Full Unicode support** - works with any language, including Persian, Arabic, and more
* **Simple and flexible** - gives you the core algorithm without extra fluff
* **Case-sensitive by default** - you control how words are processed
* **Bring your own dictionary** - use any word frequency data you want

## Installation

**Easy way:**
```bash
pip install rustivig
```

**Build it yourself:**
```bash
# Install maturin first
pipx install maturin

# Build the wheels
maturin build
```

Find your wheels in the `target/wheels` folder.

## Getting Started

You'll need a word frequency dictionary to use Rustivig. Here's how to build one from a text file:

```python
import json
import string
import rustivig

# Define your character set
en_charset = string.ascii_lowercase

# Read your corpus
with open("big_en.txt") as f:
    corpus = f.read().lower()

# Build the dictionary
en_word_freq = rustivig.build_word_frequency_dictionary(en_charset, corpus)

# Save it for later
with open("en_dict.json", "w") as f:
    json.dump(en_word_freq, f)
```

## Basic Usage

Once you have a dictionary, spell checking is simple:

```python
import json
import string
import rustivig

# Load your dictionary
en_charset = string.ascii_lowercase
with open("en_dict.json") as f:
    en_word_freq = json.load(f)

# Get correction suggestions
candidates = rustivig.get_candidates(en_charset, "helloo", en_word_freq)
print(candidates)  # {'hello', 'hellol', ...}

# Get the best correction
correction = rustivig.correct(en_charset, "helloo", en_word_freq)
print(correction)  # 'hello'
```

## Batch Processing

For better performance when checking lots of words:

```python
# Process multiple words at once
words = {"helloo", "wrold", "speling"}
results = rustivig.get_candidates_batch(en_charset, words, en_word_freq)
print(results)  # {'helloo': {'hello'}, 'wrold': {'world'}, ...}

# Auto-correct multiple words
corrections = rustivig.correct_batch(en_charset, words, en_word_freq)
print(corrections)  # {'helloo': 'hello', 'wrold': 'world', ...}
```

## Performance

Rustivig really shines with complex corrections and batch processing:

```plain
=========================================================================== test session starts ===========================================================================
platform linux -- Python 3.13.7, pytest-8.4.2, pluggy-1.6.0 -- /home/ashkanfeyzollahi/Workspace/rustivig/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/ashkanfeyzollahi/Workspace/rustivig
configfile: pyproject.toml
collected 5 items

tests/test_rustivig.py::test_simple_correction PASSED
tests/test_rustivig.py::test_batch_vs_single Single: 0.005s, Batch: 0.000s
Speedup: 88.5x
PASSED
tests/test_rustivig.py::test_vs_pyspellchecker Rustivig: 2.079s
PySpellChecker: 13.073s
Ratio: 6.3x
PASSED
tests/test_rustivig.py::test_unicode_support Unicode correction time: 0.1338s
PASSED
tests/test_rustivig.py::test_threading_vs_no_threading No threading: 0.5221s
With threading: 0.2237s
Threading speedup: 2.3x
PASSED

=========================================================================== 5 passed in 16.66s ============================================================================
```

### Benchmark Results

**Batch Processing:**
- **88x faster** than individual corrections
- Eliminates Python-Rust overhead through deduplication

**Threading:**
- **2.3x speedup** with multi-threading enabled
- Powered by Rayon's work-stealing algorithm

**vs PySpellChecker:**
- **6.3x faster** on complex corrections (2-edit distance)
- Competitive on simple corrections

**Unicode Support:**
- Full Unicode processing: ~130ms for complex words
- Supports any language (Persian, Arabic, Chinese, etc.)

### Performance Tips

* Use batch functions (`get_candidates_batch`, `correct_batch`) when processing multiple words
* Batch processing avoids Python-Rust overhead and is much faster
* For simple 1-character fixes, Python libraries might be faster due to overhead
* For complex corrections (2+ character changes), Rustivig really shines

## License

MIT License
