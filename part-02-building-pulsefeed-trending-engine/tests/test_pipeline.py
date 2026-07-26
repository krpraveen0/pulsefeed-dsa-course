from trending.pipeline import PerUserRateLimiter, Post, PulseFeedPipeline


def test_ingest_accepts_a_post_under_the_rate_limit():
    pipeline = PulseFeedPipeline()
    result = pipeline.ingest("user-1", Post(post_id="p1", hashtags=["#python", "#pulsefeed"]))
    assert result.ok is True
    assert result.reason is None


def test_ingest_updates_trending_counter_and_autocomplete_together():
    pipeline = PulseFeedPipeline()
    pipeline.ingest("user-1", Post(post_id="p1", hashtags=["#python", "#python"]))
    assert pipeline.trending_counter.counts["#python"] == 2
    assert pipeline.autocomplete_index.contains("#python") is True


def test_ingest_rejects_when_rate_limited():
    limiter = PerUserRateLimiter(capacity=1, refill_rate=0.0001)
    pipeline = PulseFeedPipeline(rate_limiter=limiter)
    first = pipeline.ingest("user-1", Post(post_id="p1", hashtags=["#a"]))
    second = pipeline.ingest("user-1", Post(post_id="p2", hashtags=["#b"]))
    assert first.ok is True
    assert second.ok is False
    assert second.reason == "rate_limited"


def test_ingest_rejected_post_does_not_update_trending_or_autocomplete():
    limiter = PerUserRateLimiter(capacity=1, refill_rate=0.0001)
    pipeline = PulseFeedPipeline(rate_limiter=limiter)
    pipeline.ingest("user-1", Post(post_id="p1", hashtags=["#a"]))
    pipeline.ingest("user-1", Post(post_id="p2", hashtags=["#rejected"]))
    assert "#rejected" not in pipeline.trending_counter
    assert pipeline.autocomplete_index.contains("#rejected") is False


def test_ingest_rate_limits_are_independent_per_user():
    limiter = PerUserRateLimiter(capacity=1, refill_rate=0.0001)
    pipeline = PulseFeedPipeline(rate_limiter=limiter)
    result_a = pipeline.ingest("user-a", Post(post_id="p1", hashtags=["#a"]))
    result_b = pipeline.ingest("user-b", Post(post_id="p2", hashtags=["#b"]))
    assert result_a.ok is True
    assert result_b.ok is True  # separate bucket for user-b, unaffected by user-a


def test_ingest_post_with_no_hashtags_still_accepted():
    pipeline = PulseFeedPipeline()
    result = pipeline.ingest("user-1", Post(post_id="p1", hashtags=[]))
    assert result.ok is True
    assert len(pipeline.trending_counter) == 0
