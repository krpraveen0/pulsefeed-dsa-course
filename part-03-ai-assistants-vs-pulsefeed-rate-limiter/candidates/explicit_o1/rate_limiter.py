import time


class TokenBucket:
    """A token bucket rate limiter.

    Tokens refill continuously at ``refill_rate`` tokens per second, up to
    ``capacity``. Each call to :meth:`allow` lazily refills the bucket based
    on the real elapsed time since the last call, then attempts to spend
    ``cost`` tokens.

    Both ``__init__`` and ``allow`` run in O(1) time and O(1) space: no
    history of calls or timestamps is retained, only the current token
    count and the timestamp of the last check.
    """

    def __init__(self, capacity: float, refill_rate: float) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be positive")

        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_checked = time.monotonic()

    def allow(self, cost: float = 1.0) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_checked
        self.last_checked = now

        if elapsed > 0:
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)

        if self.tokens >= cost:
            self.tokens -= cost
            return True

        return False
