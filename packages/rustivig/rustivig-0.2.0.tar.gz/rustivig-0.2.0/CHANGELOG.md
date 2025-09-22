## [0.1.0..HEAD] - 2025-09-21

### 🚀 Features

- Add rayon for parallel processing
- Add an option for threading to function correct
- Add an option for threading to function get_candidates and rename word_frequency_dictionary to dictionary
- Get rid of known_ variant and instead make it parameter based and add threading option to function get_distance_1_edits
- Get rid of known_ variant and instead make it parameter based and add threading option to function get_distance_2_edits
- Add threading option to function get_known_words and rename word_frequency_dictionary to dictionary
- [**breaking**] Remove variant functions in favor of unified API

### 🐛 Bug Fixes

- Be case-sensitive as said in README.md

### 💼 Other

- Add rayon, bump minor version (0.1.0 -> 0.2.0) and update lock

### 🚜 Refactor

- Rename word_frequency_dictionary to dictionary
- Rename word_frequency_dictionary to dictionary

### 🧪 Testing

- Add initial test suite

### ⚙️ Miscellaneous Tasks

- Add .ruff_cache to .gitignore
- *(types)* Update .pyi file for API changes
