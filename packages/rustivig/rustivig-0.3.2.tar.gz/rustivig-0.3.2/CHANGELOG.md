## [0.3.2] - 2025-09-22

### 🐛 Bug Fixes

- *(release)* Remove forgotten dbg macro

### 💼 Other

- Bump minor version and update lock

### 📚 Documentation

- Update CHANGELOG.md
- Update CHANGELOG.md
## [0.3.1] - 2025-09-22

### 🐛 Bug Fixes

- *(lib)* Fix broken unicode support

### 💼 Other

- Bump minor version and update lock

### 📚 Documentation

- Update CHANGELOG.md
- Remove performance section

### 🧪 Testing

- *(unicode)* Make unicode test suite proper
## [0.3.0] - 2025-09-22

### 🚀 Features

- Add unicode support

### 💼 Other

- Bump minor version and update lock

### 📚 Documentation

- Change HEAD to 0.2.0
- Fix a mistake in Usage section
- Add performance section
- Fix a mistake

### 🧪 Testing

- Add unicode support tests

### ⚙️ Miscellaneous Tasks

- Add .benchmarks to .gitignore
## [0.2.0] - 2025-09-21

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

### 📚 Documentation

- Add CHANGELOG.md
- Add line break to README.md

### 🧪 Testing

- Add initial test suite

### ⚙️ Miscellaneous Tasks

- Add .ruff_cache to .gitignore
- *(types)* Update .pyi file for API changes
## [0.1.0] - 2025-09-20

### ⚙️ Miscellaneous Tasks

- Init
