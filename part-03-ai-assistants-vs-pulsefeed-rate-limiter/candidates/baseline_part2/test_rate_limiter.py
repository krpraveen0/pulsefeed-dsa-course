"""Part 2's actual pytest suite, run here against the baseline TokenBucket copy.

Identical to the test file handed to each AI assistant as the spec/acceptance
criteria for the three `candidates/*` implementations -- included here so the
baseline passes the exact same bar before it's used as the benchmark's reference
point.
"""

from rate_limiter import TokenBucket


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
    assert bucket.allow(cost=10) is False
    assert 5 <= bucket.tokens < 5.1


def test_token_bucket_rejects_non_positive_capacity_or_rate():
    import pytest
    with pytest.raises(ValueError):
        TokenBucket(capacity=0, refill_rate=1)
    with pytest.raises(ValueError):
        TokenBucket(capacity=1, refill_rate=0)
