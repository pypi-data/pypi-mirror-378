import rustivig


def test_unicode_basic_correction():
    charset = "abcdefghijklmnopqrstuvwxyzس"
    dictionary = {"hello": 1, "world": 1, "test": 1}

    result = rustivig.correct(charset, "helo", dictionary, False)
    assert result == "hello"


def test_unicode_threading_parameter():
    charset = "abcdefghijklmnopqrstuvwxyzس"
    dictionary = {"definitely": 1}

    result_sync = rustivig.correct(charset, "definately", dictionary, False)
    result_threaded = rustivig.correct(charset, "definately", dictionary, True)

    assert result_sync == result_threaded == "definitely"
