use std::collections::{HashMap, HashSet};

use pyo3::prelude::*;
use rayon::prelude::*;

#[pyfunction]
fn build_word_frequency_dictionary(
    charset: &str,
    corpus: &str,
) -> PyResult<HashMap<String, usize>> {
    Ok(build_word_frequency_dictionary_impl(charset, corpus))
}

fn build_word_frequency_dictionary_impl(charset: &str, corpus: &str) -> HashMap<String, usize> {
    let mut dictionary: HashMap<String, usize> = HashMap::new();
    let extracted_words = extract_words_impl(charset, corpus);
    for word in extracted_words.iter() {
        dictionary
            .entry(word.clone())
            .and_modify(|f| *f += 1)
            .or_insert(1);
    }
    dictionary
}

#[pyfunction]
#[pyo3(signature = (charset, word, dictionary, use_threading=false))]
fn correct(
    charset: &str,
    word: &str,
    dictionary: HashMap<String, usize>,
    use_threading: bool,
) -> PyResult<String> {
    Ok(correct_impl(charset, word, &dictionary, use_threading))
}

fn correct_impl(
    charset: &str,
    word: &str,
    dictionary: &HashMap<String, usize>,
    use_threading: bool,
) -> String {
    match get_candidates_impl(charset, word, dictionary, use_threading)
        .iter()
        .max_by(|x, y| {
            get_probability_impl(x, dictionary).total_cmp(&get_probability_impl(y, dictionary))
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
    let corpus: String = corpus.to_string();
    let mut extracted_words: Vec<String> = Vec::new();
    for word in corpus.split(|c| !charset.contains(c)) {
        extracted_words.push(word.to_string());
    }
    extracted_words
}

#[pyfunction]
#[pyo3(signature = (charset, word, dictionary, use_threading=false))]
fn get_candidates(
    charset: &str,
    word: &str,
    dictionary: HashMap<String, usize>,
    use_threading: bool,
) -> PyResult<HashSet<String>> {
    Ok(get_candidates_impl(
        charset,
        word,
        &dictionary,
        use_threading,
    ))
}

fn get_candidates_impl(
    charset: &str,
    word: &str,
    dictionary: &HashMap<String, usize>,
    use_threading: bool,
) -> HashSet<String> {
    let no_edits = HashSet::from([word.to_string()]);
    let known_no_edits = get_known_words_impl(&no_edits, dictionary, use_threading);
    if !known_no_edits.is_empty() {
        return known_no_edits;
    }
    let known_distance_1_edits =
        get_distance_1_edits_impl(charset, word, dictionary, true, use_threading);
    if !known_distance_1_edits.is_empty() {
        return known_distance_1_edits;
    }
    let known_distance_2_edits =
        get_distance_2_edits_impl(charset, word, dictionary, true, use_threading);
    if !known_distance_2_edits.is_empty() {
        return known_distance_2_edits;
    }
    no_edits
}

#[pyfunction]
#[pyo3(signature = (charset, word, dictionary, filter_known=false, use_threading=false))]
fn get_distance_1_edits(
    charset: &str,
    word: &str,
    dictionary: HashMap<String, usize>,
    filter_known: bool,
    use_threading: bool,
) -> PyResult<HashSet<String>> {
    Ok(get_distance_1_edits_impl(
        charset,
        word,
        &dictionary,
        filter_known,
        use_threading,
    ))
}

fn get_nth_char(s: &str, n: usize) -> char {
    s.chars().nth(n).unwrap()
}

fn skip_n_and_get_rest(s: &str, n: usize) -> String {
    s.chars().skip(n).collect()
}

fn get_distance_1_edits_impl(
    charset: &str,
    word: &str,
    dictionary: &HashMap<String, usize>,
    filter_known: bool,
    use_threading: bool,
) -> HashSet<String> {
    let word_chars = word.chars();
    let splits: Vec<_> = (0..word_chars.count())
        .map(|i| word.char_indices().nth(i).unwrap().0)
        .map(|i| word.split_at(i))
        .collect();
    if use_threading {
        return splits
            .par_iter()
            .filter(|(_, r)| !r.is_empty())
            .map(|(l, r)| format!("{}{}", l, skip_n_and_get_rest(r, 1)))
            .filter(|candidate| !filter_known || dictionary.contains_key(candidate))
            .chain(
                splits
                    .par_iter()
                    .filter(|(_, r)| r.chars().count() >= 2)
                    .map(|(l, r)| {
                        format!(
                            "{}{}{}{}",
                            l,
                            get_nth_char(r, 1),
                            get_nth_char(r, 0),
                            skip_n_and_get_rest(r, 2)
                        )
                    })
                    .filter(|candidate| !filter_known || dictionary.contains_key(candidate)),
            )
            .chain({
                charset.par_chars().flat_map(|c| {
                    splits
                        .par_iter()
                        .filter(move |(_, r)| !r.is_empty())
                        .map(move |(l, r)| format!("{}{}{}", l, c, skip_n_and_get_rest(r, 1)))
                        .filter(|candidate| !filter_known || dictionary.contains_key(candidate))
                })
            })
            .chain(
                charset
                    .par_chars()
                    .flat_map(|c| {
                        splits
                            .par_iter()
                            .map(move |(l, r)| format!("{}{}{}", l, c, r))
                    })
                    .filter(|candidate| !filter_known || dictionary.contains_key(candidate)),
            )
            .collect();
    }
    splits
        .iter()
        .filter(|(_, r)| !r.is_empty())
        .map(|(l, r)| format!("{}{}", l, skip_n_and_get_rest(r, 1)))
        .filter(|candidate| !filter_known || dictionary.contains_key(candidate))
        .chain(
            splits
                .iter()
                .filter(|(_, r)| r.chars().count() >= 2)
                .map(|(l, r)| {
                    format!(
                        "{}{}{}{}",
                        l,
                        get_nth_char(r, 1),
                        get_nth_char(r, 0),
                        skip_n_and_get_rest(r, 2)
                    )
                })
                .filter(|candidate| !filter_known || dictionary.contains_key(candidate)),
        )
        .chain({
            charset.chars().flat_map(|c| {
                splits
                    .iter()
                    .filter(move |(_, r)| !r.is_empty())
                    .map(move |(l, r)| format!("{}{}{}", l, c, skip_n_and_get_rest(r, 1)))
                    .filter(|candidate| !filter_known || dictionary.contains_key(candidate))
            })
        })
        .chain(
            charset
                .chars()
                .flat_map(|c| splits.iter().map(move |(l, r)| format!("{}{}{}", l, c, r)))
                .filter(|candidate| !filter_known || dictionary.contains_key(candidate)),
        )
        .collect()
}

#[pyfunction]
#[pyo3(signature = (charset, word, dictionary, filter_known=false, use_threading=false))]
fn get_distance_2_edits(
    charset: &str,
    word: &str,
    dictionary: HashMap<String, usize>,
    filter_known: bool,
    use_threading: bool,
) -> PyResult<HashSet<String>> {
    Ok(get_distance_2_edits_impl(
        charset,
        word,
        &dictionary,
        filter_known,
        use_threading,
    ))
}

fn get_distance_2_edits_impl(
    charset: &str,
    word: &str,
    dictionary: &HashMap<String, usize>,
    filter_known: bool,
    use_threading: bool,
) -> HashSet<String> {
    let empty_dictionary: HashMap<String, usize> = HashMap::new();
    if use_threading {
        return get_distance_1_edits_impl(charset, word, &empty_dictionary, false, true)
            .par_iter()
            .flat_map(|e1| get_distance_1_edits_impl(charset, e1, dictionary, filter_known, true))
            .collect();
    }
    get_distance_1_edits_impl(charset, word, &empty_dictionary, false, false)
        .iter()
        .flat_map(|e1| get_distance_1_edits_impl(charset, e1, dictionary, filter_known, false))
        .collect()
}

#[pyfunction]
#[pyo3(signature = (words, dictionary, use_threading=false))]
fn get_known_words(
    words: HashSet<String>,
    dictionary: HashMap<String, usize>,
    use_threading: bool,
) -> PyResult<HashSet<String>> {
    Ok(get_known_words_impl(&words, &dictionary, use_threading))
}

fn get_known_words_impl(
    words: &HashSet<String>,
    dictionary: &HashMap<String, usize>,
    use_threading: bool,
) -> HashSet<String> {
    if use_threading {
        return words
            .par_iter()
            .filter(|word| dictionary.contains_key(*word))
            .map(|word| word.clone())
            .collect();
    }
    words
        .iter()
        .filter(|word| dictionary.contains_key(*word))
        .map(|word| word.clone())
        .collect()
}

#[pyfunction]
fn get_probability(word: &str, dictionary: HashMap<String, usize>) -> PyResult<f32> {
    Ok(get_probability_impl(word, &dictionary))
}

fn get_probability_impl(word: &str, dictionary: &HashMap<String, usize>) -> f32 {
    match dictionary.get(word) {
        Some(frequency) => *frequency as f32 / dictionary.values().sum::<usize>() as f32,
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
    m.add_function(wrap_pyfunction!(get_known_words, m)?)?;
    m.add_function(wrap_pyfunction!(get_probability, m)?)?;
    Ok(())
}
