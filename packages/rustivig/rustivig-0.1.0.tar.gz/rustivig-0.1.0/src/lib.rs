use std::collections::{HashMap, HashSet};

use pyo3::prelude::*;

#[pyfunction]
fn build_word_frequency_dictionary(
    charset: &str,
    corpus: &str,
) -> PyResult<HashMap<String, usize>> {
    Ok(build_word_frequency_dictionary_impl(charset, corpus))
}

fn build_word_frequency_dictionary_impl(charset: &str, corpus: &str) -> HashMap<String, usize> {
    let mut word_frequency_dictionary: HashMap<String, usize> = HashMap::new();
    let extracted_words = extract_words_impl(charset, corpus);
    for word in extracted_words.iter() {
        word_frequency_dictionary
            .entry(word.clone())
            .and_modify(|f| *f += 1)
            .or_insert(1);
    }
    word_frequency_dictionary
}

#[pyfunction]
fn correct(
    charset: &str,
    word: &str,
    word_frequency_dictionary: HashMap<String, usize>,
) -> PyResult<String> {
    Ok(correct_impl(charset, word, &word_frequency_dictionary))
}

fn correct_impl(
    charset: &str,
    word: &str,
    word_frequency_dictionary: &HashMap<String, usize>,
) -> String {
    match get_candidates_impl(charset, word, word_frequency_dictionary)
        .iter()
        .max_by(|x, y| {
            get_probability_impl(x, word_frequency_dictionary)
                .total_cmp(&get_probability_impl(y, word_frequency_dictionary))
        }) {
        Some(word) => word.clone(),
        None => word.to_string(),
    }
}

#[pyfunction]
fn extract_words(charset: &str, corpus: &str) -> PyResult<Vec<String>> {
    Ok(extract_words_impl(charset, corpus))
}

fn extract_words_impl(charset: &str, corpus: &str) -> Vec<String> {
    let corpus: String = corpus.to_lowercase();
    let mut extracted_words: Vec<String> = Vec::new();
    for word in corpus.split(|c| !charset.contains(c)) {
        extracted_words.push(word.to_string());
    }
    extracted_words
}

#[pyfunction]
fn get_candidates(
    charset: &str,
    word: &str,
    word_frequency_dictionary: HashMap<String, usize>,
) -> PyResult<HashSet<String>> {
    Ok(get_candidates_impl(
        charset,
        word,
        &word_frequency_dictionary,
    ))
}

fn get_candidates_impl(
    charset: &str,
    word: &str,
    word_frequency_dictionary: &HashMap<String, usize>,
) -> HashSet<String> {
    let no_edits = HashSet::from([word.to_string()]);
    let known_no_edits = get_known_words_impl(&no_edits, word_frequency_dictionary);
    if !known_no_edits.is_empty() {
        return known_no_edits;
    }
    let known_distance_1_edits =
        get_known_distance_1_edits_impl(charset, word, word_frequency_dictionary);
    if !known_distance_1_edits.is_empty() {
        return known_distance_1_edits;
    }
    let known_distance_2_edits =
        get_known_distance_2_edits_impl(charset, word, word_frequency_dictionary);
    if !known_distance_2_edits.is_empty() {
        return known_distance_2_edits;
    }
    no_edits
}

#[pyfunction]
fn get_distance_1_edits(charset: &str, word: &str) -> PyResult<HashSet<String>> {
    Ok(get_distance_1_edits_impl(charset, word))
}

fn get_distance_1_edits_impl(charset: &str, word: &str) -> HashSet<String> {
    let splits: Vec<_> = (0..=word.len()).map(|i| word.split_at(i)).collect();
    splits
        .iter()
        .filter(|(_, r)| !r.is_empty())
        .map(|(l, r)| format!("{}{}", l, &r[1..]))
        .chain(
            splits
                .iter()
                .filter(|(_, r)| r.len() >= 2)
                .map(|(l, r)| format!("{}{}{}{}", l, &r[1..2], &r[0..1], &r[2..])),
        )
        .chain(charset.chars().flat_map(|c| {
            splits
                .iter()
                .filter(move |(_, r)| !r.is_empty())
                .map(move |(l, r)| format!("{}{}{}", l, c, &r[1..]))
        }))
        .chain(
            charset
                .chars()
                .flat_map(|c| splits.iter().map(move |(l, r)| format!("{}{}{}", l, c, r))),
        )
        .collect()
}

#[pyfunction]
fn get_distance_2_edits(charset: &str, word: &str) -> PyResult<HashSet<String>> {
    Ok(get_distance_2_edits_impl(charset, word))
}

fn get_distance_2_edits_impl(charset: &str, word: &str) -> HashSet<String> {
    get_distance_1_edits_impl(charset, word)
        .iter()
        .flat_map(|e1| get_distance_1_edits_impl(charset, e1))
        .collect()
}

#[pyfunction]
fn get_known_distance_1_edits(
    charset: &str,
    word: &str,
    word_frequency_dictionary: HashMap<String, usize>,
) -> PyResult<HashSet<String>> {
    Ok(get_known_distance_1_edits_impl(
        charset,
        word,
        &word_frequency_dictionary,
    ))
}

fn get_known_distance_1_edits_impl(
    charset: &str,
    word: &str,
    word_frequency_dictionary: &HashMap<String, usize>,
) -> HashSet<String> {
    let splits: Vec<_> = (0..=word.len()).map(|i| word.split_at(i)).collect();
    splits
        .iter()
        .filter(|(_, r)| !r.is_empty())
        .map(|(l, r)| format!("{}{}", l, &r[1..]))
        .filter(|candidate| word_frequency_dictionary.contains_key(candidate))
        .chain(
            splits
                .iter()
                .filter(|(_, r)| r.len() >= 2)
                .map(|(l, r)| format!("{}{}{}{}", l, &r[1..2], &r[0..1], &r[2..]))
                .filter(|candidate| word_frequency_dictionary.contains_key(candidate)),
        )
        .chain(charset.chars().flat_map(|c| {
            splits
                .iter()
                .filter(move |(_, r)| !r.is_empty())
                .map(move |(l, r)| format!("{}{}{}", l, c, &r[1..]))
                .filter(|candidate| word_frequency_dictionary.contains_key(candidate))
        }))
        .chain(
            charset
                .chars()
                .flat_map(|c| splits.iter().map(move |(l, r)| format!("{}{}{}", l, c, r)))
                .filter(|candidate| word_frequency_dictionary.contains_key(candidate)),
        )
        .collect()
}

#[pyfunction]
fn get_known_distance_2_edits(
    charset: &str,
    word: &str,
    word_frequency_dictionary: HashMap<String, usize>,
) -> PyResult<HashSet<String>> {
    Ok(get_known_distance_2_edits_impl(
        charset,
        word,
        &word_frequency_dictionary,
    ))
}

fn get_known_distance_2_edits_impl(
    charset: &str,
    word: &str,
    word_frequency_dictionary: &HashMap<String, usize>,
) -> HashSet<String> {
    get_distance_1_edits_impl(charset, word)
        .iter()
        .flat_map(|e1| get_distance_1_edits_impl(charset, e1))
        .filter(|e2| word_frequency_dictionary.contains_key(e2))
        .collect()
}

#[pyfunction]
fn get_known_words(
    words: HashSet<String>,
    word_frequency_dictionary: HashMap<String, usize>,
) -> PyResult<HashSet<String>> {
    Ok(get_known_words_impl(&words, &word_frequency_dictionary))
}

fn get_known_words_impl(
    words: &HashSet<String>,
    word_frequency_dictionary: &HashMap<String, usize>,
) -> HashSet<String> {
    words
        .iter()
        .filter(|word| word_frequency_dictionary.contains_key(*word))
        .map(|word| word.clone())
        .collect()
}

#[pyfunction]
fn get_probability(word: &str, word_frequency_dictionary: HashMap<String, usize>) -> PyResult<f32> {
    Ok(get_probability_impl(word, &word_frequency_dictionary))
}

fn get_probability_impl(word: &str, word_frequency_dictionary: &HashMap<String, usize>) -> f32 {
    match word_frequency_dictionary.get(word) {
        Some(frequency) => {
            *frequency as f32 / word_frequency_dictionary.values().sum::<usize>() as f32
        }
        None => 0.0,
    }
}

#[pymodule]
fn rustivig(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(build_word_frequency_dictionary, m)?)?;
    m.add_function(wrap_pyfunction!(correct, m)?)?;
    m.add_function(wrap_pyfunction!(extract_words, m)?)?;
    m.add_function(wrap_pyfunction!(get_candidates, m)?)?;
    m.add_function(wrap_pyfunction!(get_distance_1_edits, m)?)?;
    m.add_function(wrap_pyfunction!(get_distance_2_edits, m)?)?;
    m.add_function(wrap_pyfunction!(get_known_distance_1_edits, m)?)?;
    m.add_function(wrap_pyfunction!(get_known_distance_2_edits, m)?)?;
    m.add_function(wrap_pyfunction!(get_known_words, m)?)?;
    m.add_function(wrap_pyfunction!(get_probability, m)?)?;
    Ok(())
}
