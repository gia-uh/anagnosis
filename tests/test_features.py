from collections import Counter

from anagnosis.features import Pool, pool, ratio


def test_pooled_ratio_is_not_a_mean_of_ratios():
    a = Pool(Counter(words=2, syllables=10))
    b = Pool(Counter(words=8, syllables=8))
    spw = ratio("syllables", "words")
    assert spw(pool([a, b])) == 1.8  # 18 / 10; the mean of ratios would be 3.0


def test_pool_concatenates_bags_in_order():
    a, b = Pool(bags={"t": ["x", "y"]}), Pool(bags={"t": ["z"]})
    assert pool([a, b]).bags["t"] == ["x", "y", "z"]


def test_ratio_of_empty_pool_is_none():
    assert ratio("syllables", "words")(Pool()) is None
