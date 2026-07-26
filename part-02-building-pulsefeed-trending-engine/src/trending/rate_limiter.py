"""PulseFeed's per-user rate limiter: a lazy-refill token bucket.

Follows the pattern Stripe documented publicly for its own API (a bucket
holds tokens up to a fixed capacity, tokens refill at a fixed rate, and
each request spends one token) with a lazy, on-demand refill computed at
request time instead of a background thread ticking tokens in. See:
https://stripe.com/blog/rate-limiters and
https://gist.github.com/ptarjan/e38f45f2dfe601419ca3af937fff574d.

`SlidingWindowLimiter` is the honest alternative PulseFeed does *not* ship:
a hard "no more than N requests in this exact rolling window" guarantee,
built on a bounded `collections.deque(maxlen=N)` so the timestamp log can
never grow past `max_requests` -- no manual pruning loop, no
ever-growing list of timestamps.
"""

import time
from collections import deque


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


class SlidingWindowLimiter:
    """A hard 'at most `max_requests` in the last `window_seconds`' limiter.

    Built on a bounded deque: appends are O(1), and once the deque hits
    `maxlen`, every new append silently evicts the oldest timestamp --
    no manual pruning loop, no unbounded growth.
    """

    def __init__(self, max_requests: int, window_seconds: float):
        if max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self.window_seconds = window_seconds
        self.timestamps: deque = deque(maxlen=max_requests)

    def allow(self) -> bool:
        now = time.monotonic()
        while self.timestamps and now - self.timestamps[0] > self.window_seconds:
            self.timestamps.popleft()
        if len(self.timestamps) < self.timestamps.maxlen:
            self.timestamps.append(now)
            return True
        return False

    def __len__(self) -> int:
        return len(self.timestamps)

    def __repr__(self) -> str:
        return (
            f"SlidingWindowLimiter(max_requests={self.timestamps.maxlen}, "
            f"window_seconds={self.window_seconds}, current={len(self.timestamps)})"
        )
