"""Wires the rate limiter, trending counter, and autocomplete trie into ingest().

`ingest()` is the whole integration: rate limiter first (cheapest check,
and the one that should short-circuit everything else), then the dict
update, then the trie insert. The three structures don't share state
with each other -- that's deliberate. A bug in the trie can't corrupt
the rate limiter's token count, because nothing about `TokenBucket`
knows the trie exists.
"""

from dataclasses import dataclass, field

from .autocomplete import AutocompleteTrie
from .counter import TrendingCounter
from .rate_limiter import TokenBucket


@dataclass
class Post:
    post_id: str
    hashtags: list[str] = field(default_factory=list)


@dataclass
class IngestResult:
    ok: bool
    reason: str | None = None

    @classmethod
    def accepted(cls) -> "IngestResult":
        return cls(ok=True)

    @classmethod
    def rejected(cls, reason: str) -> "IngestResult":
        return cls(ok=False, reason=reason)


class PerUserRateLimiter:
    """One `TokenBucket` per `user_id`, created lazily on first use.

    `TokenBucket` itself has no notion of "user" -- it's one bucket's
    worth of state. This is the thin per-user registry PulseFeed's
    ingestion pipeline actually needs on top of it.
    """

    def __init__(self, capacity: float = 500, refill_rate: float = 100):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._buckets: dict[str, TokenBucket] = {}

    def allow(self, user_id: str, cost: float = 1.0) -> bool:
        bucket = self._buckets.get(user_id)
        if bucket is None:
            bucket = TokenBucket(self.capacity, self.refill_rate)
            self._buckets[user_id] = bucket
        return bucket.allow(cost)

    def __len__(self) -> int:
        return len(self._buckets)


class PulseFeedPipeline:
    """Owns the three structures and exposes the single `ingest()` entry point."""

    def __init__(
        self,
        rate_limiter: PerUserRateLimiter | None = None,
        trending_counter: TrendingCounter | None = None,
        autocomplete_index: AutocompleteTrie | None = None,
    ):
        self.rate_limiter = rate_limiter if rate_limiter is not None else PerUserRateLimiter()
        self.trending_counter = (
            trending_counter if trending_counter is not None else TrendingCounter()
        )
        self.autocomplete_index = (
            autocomplete_index if autocomplete_index is not None else AutocompleteTrie()
        )

    def ingest(self, user_id: str, post: Post) -> IngestResult:
        if not self.rate_limiter.allow(user_id):
            return IngestResult.rejected("rate_limited")

        for tag in post.hashtags:
            self.trending_counter.mention(tag)
            self.autocomplete_index.insert(tag)

        return IngestResult.accepted()
