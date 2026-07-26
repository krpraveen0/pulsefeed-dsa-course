from trending.rate_limiter import SlidingWindowLimiter, TokenBucket


def test_rate_limiter_survives_a_burst_then_recovers():
    bucket = TokenBucket(capacity=5, refill_rate=1)
    assert all(bucket.allow() for _ in range(5))  # burst up to capacity
    assert bucket.allow() is False  # 6th request in the same instant fails
    bucket.last_checked -= 5  # simulate 5 seconds elapsed
    assert bucket.allow() is True  # refilled enough for one more


def test_token_bucket_never_exceeds_capacity():
    bucket = TokenBucket(capacity=5, refill_rate=100)
    bucket.last_checked -= 1000  # simulate a huge elapsed time
    bucket.allow()
    assert bucket.tokens <= bucket.capacity


def test_token_bucket_rejects_when_empty():
    bucket = TokenBucket(capacity=1, refill_rate=0.0001)
    assert bucket.allow() is True
    assert bucket.allow() is False


def test_token_bucket_rejects_cost_greater_than_available_tokens():
    bucket = TokenBucket(capacity=10, refill_rate=1)
    assert bucket.allow(cost=5) is True
    assert bucket.allow(cost=10) is False  # only ~5 tokens left, refill negligible
    assert 5 <= bucket.tokens < 5.1  # tiny lazy-refill drift from elapsed wall time


def test_token_bucket_rejects_non_positive_capacity_or_rate():
    import pytest

    with pytest.raises(ValueError):
        TokenBucket(capacity=0, refill_rate=1)
    with pytest.raises(ValueError):
        TokenBucket(capacity=1, refill_rate=0)


def test_sliding_window_limiter_bounds_requests_in_window():
    limiter = SlidingWindowLimiter(max_requests=3, window_seconds=60)
    assert limiter.allow() is True
    assert limiter.allow() is True
    assert limiter.allow() is True
    assert limiter.allow() is False  # 4th request within the window fails
    assert len(limiter) == 3


def test_sliding_window_limiter_never_grows_past_max_requests():
    limiter = SlidingWindowLimiter(max_requests=2, window_seconds=60)
    for _ in range(10):
        limiter.allow()
    assert len(limiter.timestamps) <= 2


def test_sliding_window_limiter_evicts_expired_timestamps():
    limiter = SlidingWindowLimiter(max_requests=1, window_seconds=0.01)
    assert limiter.allow() is True
    assert limiter.allow() is False
    limiter.timestamps[0] -= 1  # simulate the one timestamp aging out
    assert limiter.allow() is True
