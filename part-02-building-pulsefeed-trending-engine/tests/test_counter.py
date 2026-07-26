import pytest

from trending.counter import PersistentTrendingQueue, TrendingCounter, top_trending


def test_empty_feed_returns_no_trending():
    assert top_trending({}, k=5) == []


def test_top_k_tie_breaking_is_deterministic():
    # three tags tied at count=3 -- nlargest must return a stable, repeatable order
    counts = {"#a": 3, "#b": 3, "#c": 3, "#d": 1}
    first = top_trending(counts, k=2)
    second = top_trending(counts, k=2)
    assert first == second


def test_top_trending_orders_by_count_descending():
    counts = {"#a": 5, "#b": 2, "#c": 1}
    assert top_trending(counts, k=2) == [("#a", 5), ("#b", 2)]


def test_top_trending_k_larger_than_dict_returns_everything():
    counts = {"#a": 1, "#b": 2}
    result = top_trending(counts, k=10)
    assert len(result) == 2


def test_trending_counter_mention_increments_count():
    c = TrendingCounter()
    c.mention("#pulsefeed")
    c.mention("#pulsefeed")
    assert c.counts["#pulsefeed"] == 2


def test_trending_counter_expire_decrements_and_deletes_at_zero():
    c = TrendingCounter()
    c.mention("#pulsefeed")
    c.expire("#pulsefeed")
    assert "#pulsefeed" not in c


def test_trending_counter_expire_on_missing_tag_is_a_noop():
    c = TrendingCounter()
    c.expire("#doesnotexist")  # should not raise
    assert len(c) == 0


def test_trending_counter_top_uses_top_trending():
    c = TrendingCounter()
    for _ in range(5):
        c.mention("#a")
    for _ in range(2):
        c.mention("#b")
    c.mention("#c")
    assert c.top(2) == [("#a", 5), ("#b", 2)]


def test_persistent_queue_pop_highest_skips_removed_entries():
    pq = PersistentTrendingQueue()
    pq.add_or_update("#a", priority=-5)  # negated count for max-first pop order
    pq.add_or_update("#b", priority=-2)
    pq.remove("#a")
    assert pq.pop_highest() == "#b"
    with pytest.raises(KeyError):
        pq.pop_highest()


def test_persistent_queue_add_or_update_replaces_stale_priority():
    pq = PersistentTrendingQueue()
    pq.add_or_update("#a", priority=-1)
    pq.add_or_update("#a", priority=-10)  # re-add with a higher (more negative) priority
    assert pq.pop_highest() == "#a"
    assert len(pq) == 0


def test_persistent_queue_contains_reflects_live_entries_only():
    pq = PersistentTrendingQueue()
    pq.add_or_update("#a", priority=-1)
    assert "#a" in pq
    pq.remove("#a")
    assert "#a" not in pq
