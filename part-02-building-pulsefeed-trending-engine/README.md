# Part 2 — Building PulseFeed's Trending Engine

Companion code for Part 2 of *Data Structures and Algorithms in Python: Beyond the
Cheat Sheet*. Part 1 left PulseFeed with a `deque`-backed ingestion window and a
plain-dict trending counter. Part 2 builds the three things a real trending-topics
product actually has to answer on every request — is this user allowed to post right
now, what are the top-five hashtags this minute, and what do you show someone typing
`#pu` into search — and wires all three into a single `ingest()` call.

## What's here

```
src/trending/
    rate_limiter.py   TokenBucket (lazy-refill token bucket, PulseFeed's real
                       rate limiter) + SlidingWindowLimiter (the honest bounded-
                       deque alternative for a hard rolling-window guarantee)
    counter.py         TrendingCounter (Part 1's plain dict, unchanged) +
                       top_trending() (heapq.nlargest top-K query) +
                       PersistentTrendingQueue (the documented entry_finder/
                       REMOVED lazy-deletion fix for heapq's decrease-key gap,
                       from the official heapq docs' Priority Queue
                       Implementation Notes — not PulseFeed's default path,
                       included because the article walks through why)
    autocomplete.py     TrieNode / AutocompleteTrie — dict-of-children trie
                       with a DFS `_collect` for prefix autocomplete
    pipeline.py         Post, IngestResult, PerUserRateLimiter, and
                       PulseFeedPipeline.ingest() — wires the three
                       structures together: rate limiter first (cheapest
                       check, short-circuits everything else), then the
                       dict update, then the trie insert

tests/                 pytest suite covering the happy path and the edge
                       cases the article calls out on purpose: tie-breaking
                       determinism in top_trending, token-bucket burst-then-
                       recover math, rejected posts not touching the
                       trending counter or trie, and per-user rate-limit
                       isolation.
```

## Running it

Requires Python 3.9+. From this directory:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

Try it interactively:

```python
from trending.pipeline import Post, PulseFeedPipeline

pipeline = PulseFeedPipeline()
result = pipeline.ingest("user-1", Post(post_id="p1", hashtags=["#python", "#pulsefeed"]))
print(result)                                   # IngestResult(ok=True, reason=None)
print(pipeline.trending_counter.top(5))         # [('#python', 1), ('#pulsefeed', 1)]
print(pipeline.autocomplete_index.autocomplete("#py"))  # ['#python']
```

## Article

Part 2: "Building PulseFeed's Trending Engine: One Dict, One Trie, One Token Bucket,
No Full Scans" (link once published).
