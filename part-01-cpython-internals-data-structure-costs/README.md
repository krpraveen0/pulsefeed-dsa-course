# Part 1 — The CPython Internals Your Data Structure Choices Are Actually Paying For

Companion code for Part 1 of *Data Structures and Algorithms in Python: Beyond the
Cheat Sheet*. This is the PulseFeed repo's first module: the deliberately naive
first-pass ingestion window that shipped `list.pop(0)` to production, the fixed
version built on `collections.deque`, the plain-dict trending-hashtag counter used
to talk about dict tombstones and `bpo-33205`, and a `benchmarks/` directory you run
yourself instead of trusting the article's numbers.

## What's here

```
src/pulsefeed/
    window.py      Window — the fixed ingestion window (deque-backed)
    trending.py     TrendingCounter — plain-dict trending-hashtag counter

benchmarks/
    naive_window.py     NaiveWindow — the exact naive class the article profiles
                         and fixes (list.pop(0) as FIFO eviction), plus a
                         cProfile demo you can run directly.
    window_bench.py      timeit A/B: list.pop(0) vs deque.popleft(), across
                          window sizes.
    dict_churn_bench.py  timeit benchmark of dict insert/delete churn (the
                          trending-counter's mention/expire cycle).
    dict_memory_bench.py Memory-tracking benchmark modeled on the bpo-33205
                          reproduction: builds a large dict, deletes almost
                          all of it, reinserts a small batch, and reports
                          sys.getsizeof() at each stage against a dict built
                          fresh at the same final size.

tests/                pytest suite covering the fixed containers and a smoke
                      test that every benchmark script actually runs.
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

Reproduce the `list.pop(0)` vs `deque.popleft()` numbers from the article:

```bash
python -m benchmarks.window_bench
```

Profile `NaiveWindow` with `cProfile`, the exact pattern the article uses, and watch
`list.pop(0)` become the top line in the stats table:

```bash
python -m benchmarks.naive_window
```

Time the dict insert/delete churn PulseFeed's trending counter does constantly:

```bash
python -m benchmarks.dict_churn_bench
```

Watch the dict-memory behavior from `bpo-33205` ("GROWTH_RATE prevents dict
shrinking", https://bugs.python.org/issue33205) reproduced on your own interpreter:

```bash
python -m benchmarks.dict_memory_bench
```

Every number these scripts print depends on your machine and your Python build — run
them yourself before trusting anything the article says about the multiples.

## Article

Part 1: "list.pop(0) Was Quietly Costing PulseFeed O(n²) — Here's What CPython's
Source Says About Every Container You Reach For" (link once published).
