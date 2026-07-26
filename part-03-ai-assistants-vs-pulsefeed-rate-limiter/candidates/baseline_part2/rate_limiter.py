"""PulseFeed's Part 2 baseline `TokenBucket`, copied verbatim (not AI-generated).

This is not a candidate produced by an AI assistant. It's the actual, human-authored
`TokenBucket` implementation from Part 2 of this course
(`part-02-building-pulsefeed-trending-engine/src/trending/rate_limiter.py` in this
same repo), copied here unmodified so the benchmark harness in `benchmark.py` has a
non-AI reference point to measure the three AI-generated candidates against.

Source: https://github.com/krpraveen0/pulsefeed-dsa-course/blob/master/part-02-building-pulsefeed-trending-engine/repo-module/src/trending/rate_limiter.py

Follows the pattern Stripe documented publicly for its own API rate limiter (a
bucket holds tokens up to a fixed capacity, tokens refill at a fixed rate, and each
request spends one token), with a lazy, on-demand refill computed at request time
instead of a background thread ticking tokens in.
"""

import time


class TokenBucket:
    """Per-user rate limiter. Lazy refill -- no timer thread required.

    Two knobs: `capacity` bounds how big a burst is tolerated, `refill_rate`
    (tokens/sec) bounds sustained throughput. Stripe's own production
    example uses capacity=500, refill_rate=100 (~100 req/s sustained,
    bursts up to 500 before throttling).
    """

    def __init__(self, capacity: float, refill_rate: float):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be positive")
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_checked = time.monotonic()

    def allow(self, cost: float = 1.0) -> bool:
        """Return True and spend `cost` tokens if enough are available."""
        now = time.monotonic()
        elapsed = now - self.last_checked
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_checked = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

    def __repr__(self) -> str:
        return (
            f"TokenBucket(capacity={self.capacity}, refill_rate={self.refill_rate}, "
            f"tokens={self.tokens:.2f})"
        )
