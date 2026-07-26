import time


class TokenBucket:
    """A token-bucket rate limiter.

    Tokens refill continuously at ``refill_rate`` tokens per second, up to
    ``capacity``. Each call to ``allow`` first tops up the bucket based on
    real elapsed wall-clock time since the last check, then admits the
    request only if enough tokens are available.
    """

    def __init__(self, capacity: float, refill_rate: float):
        if capacity <= 0 or refill_rate <= 0:
            raise ValueError("capacity and refill_rate must be positive")

        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_checked = time.monotonic()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_checked
        if elapsed > 0:
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_checked = now

    def allow(self, cost: float = 1.0) -> bool:
        self._refill()

        if self.tokens >= cost:
            self.tokens -= cost
            return True

        return False
