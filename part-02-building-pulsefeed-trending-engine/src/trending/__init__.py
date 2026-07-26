"""PulseFeed's trending engine: rate limiter, top-K counter, autocomplete trie.

Three access patterns, three stdlib-backed structures, wired together by
`pipeline.PulseFeedPipeline.ingest()`. This is the Part 2 module of the
"Data Structures and Algorithms in Python" course; it extends Part 1's
`pulsefeed` package (deque-backed window, plain-dict trending counter)
rather than replacing it.
"""

from .autocomplete import AutocompleteTrie, TrieNode
from .counter import PersistentTrendingQueue, TrendingCounter, top_trending
from .pipeline import IngestResult, PerUserRateLimiter, Post, PulseFeedPipeline
from .rate_limiter import SlidingWindowLimiter, TokenBucket

__all__ = [
    "AutocompleteTrie",
    "TrieNode",
    "PersistentTrendingQueue",
    "TrendingCounter",
    "top_trending",
    "IngestResult",
    "PerUserRateLimiter",
    "Post",
    "PulseFeedPipeline",
    "SlidingWindowLimiter",
    "TokenBucket",
]
