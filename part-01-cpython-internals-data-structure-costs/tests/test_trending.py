from pulsefeed.trending import TrendingCounter


def test_mention_increments_count():
    c = TrendingCounter()
    c.mention("#pulsefeed")
    c.mention("#pulsefeed")
    assert c.counts["#pulsefeed"] == 2


def test_expire_decrements_and_deletes_at_zero():
    c = TrendingCounter()
    c.mention("#pulsefeed")
    c.expire("#pulsefeed")
    assert "#pulsefeed" not in c


def test_expire_on_missing_tag_is_a_noop():
    c = TrendingCounter()
    c.expire("#doesnotexist")  # should not raise
    assert len(c) == 0


def test_top_k_orders_by_count_descending():
    c = TrendingCounter()
    for _ in range(5):
        c.mention("#a")
    for _ in range(2):
        c.mention("#b")
    c.mention("#c")
    assert c.top(2) == [("#a", 5), ("#b", 2)]


def test_churn_leaves_len_consistent():
    c = TrendingCounter()
    tags = [f"#tag{i}" for i in range(50)]
    for t in tags:
        c.mention(t)
    assert len(c) == 50
    for t in tags[:30]:
        c.expire(t)
    assert len(c) == 20
