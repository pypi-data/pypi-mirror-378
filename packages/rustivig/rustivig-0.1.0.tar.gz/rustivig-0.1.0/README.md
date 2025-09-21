# Rustivig

<p align="center">
    <em>🧙 A Rust implementation of Peter Norvig's spell corrector algorithm for use in Python</em>
    <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/ashkanfeyzollahi/rustivig">
    <img alt="GitHub License" src="https://img.shields.io/github/license/ashkanfeyzollahi/rustivig">
    <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/rustivig">
    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/rustivig">
    <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/ashkanfeyzollahi/rustivig/CI.yml">
</p>

**rustivig** is a Rust implementation of Peter Norvig's spell corrector algorithm for use in Python.
It is 10x slower than the pure Python implementation `pyspellchecker` in 1 distance edit cases but 2-3x faster
in 2 distance edits cases due to PyO3's expensive type conversion. Open sourced this hoping people will
contribute and optimize this implementation much more and make it fastest spell checker based on
Peter Norvig's spell checking algorithm.

## Features

* **Rustivig** is more like bare algorithm implementation unlike **pyspellchecker** which does
everything for you.
* **Rustivig** is case-sensitive by default.
* For using **Rustivig** you will
need a corpus or a word frequency dictionary unlike **pyspellchecker** which comes with word
frequency dictionaries for different languages.

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

en_word_frequency_dictionary = rustivig.build_word_frequency_dictionary(corpus)

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
