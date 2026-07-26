"""Production token-bucket rate limiter.

Designed for use inside a live backend service (e.g. one instance per
API key / client behind a request path). Key production concerns:

- Thread-safe: a single ``TokenBucket`` instance may be hit concurrently
  by multiple worker threads (WSGI/ASGI thread pools, gunicorn threads,
  etc.), so token accounting is protected by a lock.
- Uses ``time.monotonic()`` instead of ``time.time()`` so behavior is
  immune to wall-clock adjustments (NTP sync, DST, manual clock changes)
  that could otherwise let a client burst extra tokens or get starved.
- O(1) time and O(1) memory per call: refill is computed lazily from
  elapsed time rather than via a background timer/thread, so idle
  buckets cost nothing and there's nothing to schedule or clean up.
- No unbounded growth: tokens are always clamped to ``capacity``, so a
  bucket that hasn't been touched in a long time can't accumulate an
  unbounded credit.
"""

from __future__ import annotations

import threading
import time


class TokenBucket:
    """A thread-safe token-bucket rate limiter.

    Tokens refill continuously at ``refill_rate`` tokens/second, up to
    ``capacity``. Each call to :meth:`allow` lazily refills based on
    elapsed wall-clock time (via a monotonic clock) since the last call,
    then attempts to deduct ``cost`` tokens.
    """

    __slots__ = ("capacity", "refill_rate", "tokens", "last_checked", "_lock")

    def __init__(self, capacity: float, refill_rate: float) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be positive")

        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self.tokens = float(capacity)
        self.last_checked = time.monotonic()
        self._lock = threading.Lock()

    def allow(self, cost: float = 1.0) -> bool:
        """Attempt to consume ``cost`` tokens.

        Returns True and deducts ``cost`` tokens if enough were
        available (after accounting for refill since the last call).
        Returns False and leaves the bucket untouched otherwise.
        """
        with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_checked
            if elapsed > 0:
                self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_checked = now

            if self.tokens >= cost:
                self.tokens -= cost
                return True
            return False
