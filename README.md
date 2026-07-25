# PulseFeed — Data Structures and Algorithms in Python: Beyond the Cheat Sheet

Companion repo for the course *Data Structures and Algorithms in Python: Beyond the
Cheat Sheet*. PulseFeed is a real-time trending-topics tracker for a social-style
feed — it ingests a stream of posts, rate-limits ingestion per user, computes live
top-K trending hashtags, and serves prefix autocomplete over active tags. It's one
accumulating codebase built up across the course, part by part, not a fresh scaffold
each time.

## Structure

```
part-01-cpython-internals-data-structure-costs/
    The CPython internals behind list/dict costs: the naive list.pop(0) ingestion
    window that caused a real production slowdown, the fixed deque-backed version,
    a plain-dict trending-hashtag counter, and a benchmarks/ directory you run
    yourself to reproduce both slowdowns discussed in the article.

part-02-building-pulsefeed-trending-engine/
    (coming in Part 2) heap-based top-K trending counter, trie-based prefix
    autocomplete, token-bucket rate limiter — extends Part 1's repo directly.

part-03-ai-assistants-vs-pulsefeed-rate-limiter/
    (coming in Part 3) AI-generated candidate implementations of Part 2's
    rate-limiter spec, profiled against the shared benchmark harness from Part 1.
```

## Running the code

Each part directory is a self-contained Python package with its own
`pyproject.toml`. From inside a part's directory:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

See each part's own README for what its modules do and which benchmark/demo scripts
to run.

## Articles

- Part 1: link once published
- Part 2: coming soon
- Part 3: coming soon

## License

MIT — see [LICENSE](LICENSE).
