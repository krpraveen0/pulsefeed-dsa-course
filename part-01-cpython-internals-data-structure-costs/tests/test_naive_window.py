from benchmarks.naive_window import NaiveWindow


def test_naive_window_holds_at_most_size_posts():
    w = NaiveWindow(size=3)
    for post in range(10):
        w.ingest(post)
    assert len(w.posts) == 3


def test_naive_window_keeps_most_recent_posts_in_order():
    w = NaiveWindow(size=3)
    for post in range(5):
        w.ingest(post)
    # oldest posts (0, 1) should have been evicted via pop(0)
    assert w.posts == [2, 3, 4]


def test_naive_window_under_size_keeps_everything():
    w = NaiveWindow(size=5)
    for post in range(3):
        w.ingest(post)
    assert w.posts == [0, 1, 2]
