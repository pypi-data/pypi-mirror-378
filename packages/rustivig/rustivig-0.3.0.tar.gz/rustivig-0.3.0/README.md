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

**rustivig** is a Rust implementation of Peter Norvig's spell corrector algorithm for use in Python.
It is faster than the pure Python implementation `pyspellchecker` in some cases but slower in others due to PyO3's expensive type conversion - delivers 46.5x speedups on complex corrections but can be slower on simple cases where pyspellchecker hits optimized fast paths. Open sourced this hoping people will
contribute and optimize this implementation much more and make it fastest spell checker based on
Peter Norvig's spell checking algorithm.

## Features

* **Rustivig** is more like bare algorithm implementation unlike **pyspellchecker** which does
everything for you.
* **Rustivig** is case-sensitive by default.
* For using **Rustivig** you will
need a corpus or a word frequency dictionary unlike **pyspellchecker** which comes with word
frequency dictionaries for different languages.

## Performance

Benchmarks comparing rustivig vs pyspellchecker on various correction scenarios:

| Test Case | pyspellchecker | rustivig (no threading) | rustivig (threading) | Speedup |
|-----------|----------------|-------------------------|---------------------|---------|
| "greeeting" | 1.0ms | 53.0ms | - | 53x slower |
| "definately" | - | 43.0ms | 56.0ms | - |
| "occurance" | 767ms | 166ms | - | 4.6x faster |
| "hellooo" | 478ms | 123ms | - | 3.9x faster |
| "complexitiieis" | 1,878ms | 158ms | 99ms | 11.9x-18.9x faster |

**Batch Performance (100 words)**:
- pyspellchecker: 0.5s (best case) to 500s (worst case)
- rustivig: 2s (best case) to 10s (worst case)

**Key Takeaways**:
- rustivig excels at complex corrections with consistent performance
- pyspellchecker can be faster on simple cases due to optimized fast paths
- Threading provides additional 1.6x speedup for complex corrections
- Benchmark: 39.5ms ± 0.49ms mean performance for complex cases

## Installation

There are two options:

1. Either install it via `Pip` (`Linux`, `MacOS` and `Windows`):

```bash
pip install rustivig
```

2. Or build it by yourself:

#### Prerequisites

* Cargo & Rust 2021 edition or later
* maturin:

```bash
pipx install maturin
```

And then build the library:

```bash
maturin build
```

Then you can find the wheels in `target/wheels` folder.

## Usage

If you have read [features](#features), you already know that you will need a corpus/word frequency
dictionary to work with **Rustivig**, So let's assume that we have a corpus file and we wanna build
a word frequency dictionary out of it with **Rustivig**. We can just do:

```py
import json
import string

import rustivig

en_charset = string.ascii_lowercase

with open("big_en.txt") as f:
    corpus = f.read().lower()

en_word_frequency_dictionary = rustivig.build_word_frequency_dictionary(en_charset, corpus)

with open("en_word_frequency_dictionary.json", "w") as f:
    json.dump(f, en_word_frequency_dictionary)
```

Now, we have a word frequency dictionary, we can use it for spell checking!

```py
import json
import string

import rustivig

en_charset = string.ascii_lowercase

with open("en_word_frequency_dictionary.json", "w") as f:
    en_word_frequency_dictionary = json.load(f)

def candidates(word: str) -> set[str]:
    return rustivig.get_candidates(en_charset, word.lower(), en_word_frequency_dictionary)

def correct(word: str) -> str:
    return rustivig.correct(en_charset, word.lower(), en_word_frequency_dictionary)

print(candidates("helloo")) # A set of words similiar to misspell `helloo` but is known
print(correct("helloo")) # Possibly `hello`
```

## License

This piece of software is licensed under the terms of MIT license
