import pytest
import rustivig


@pytest.mark.benchmark
def test_performance_vs_target(benchmark):
    charset = "abcdefghijklmnopqrstuvwxyz"
    dictionary = {"complexities": 1}

    result = benchmark(rustivig.correct, charset, "complexitiieis", dictionary, True)
    assert result == "complexities"
