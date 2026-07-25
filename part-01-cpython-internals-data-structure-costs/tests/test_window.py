import pytest

from pulsefeed.window import Window


def test_window_holds_at_most_size_posts():
    w = Window(size=3)
    for post in range(10):
        w.ingest(post)
    assert len(w) == 3


def test_window_keeps_most_recent_posts_in_order():
    w = Window(size=3)
    for post in range(5):
        w.ingest(post)
    assert list(w) == [2, 3, 4]


def test_window_matches_naive_window_behavior():
    """Window (deque-backed) and NaiveWindow (list-backed) must agree on
    output -- Part 1's whole point is that the fix changes performance,
    not observable behavior."""
    from benchmarks.naive_window import NaiveWindow

    naive = NaiveWindow(size=4)
    fixed = Window(size=4)
    for post in range(20):
        naive.ingest(post)
        fixed.ingest(post)

    assert naive.posts == list(fixed)


def test_window_rejects_nonpositive_size():
    with pytest.raises(ValueError):
        Window(size=0)
