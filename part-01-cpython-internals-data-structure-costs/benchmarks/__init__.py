"""Benchmarks reproducing the two slowdowns discussed in Part 1 of
"Data Structures and Algorithms in Python: Beyond the Cheat Sheet":

- `naive_window.py`   -- the deliberately naive first-pass ingestion window
                         (`list.pop(0)` as a FIFO), the exact code the
                         article profiles and fixes.
- `window_bench.py`   -- timeit A/B of `list.pop(0)` vs `deque.popleft()`
                         across window sizes.
- `dict_churn_bench.py` -- timeit benchmark of dict insert/delete churn,
                         the shape of PulseFeed's trending-hashtag counter.
- `dict_memory_bench.py` -- memory-tracking variant modeled on the
                         bpo-33205 reproduction: watches `sys.getsizeof()`
                         across a mass-delete-then-reinsert churn cycle.

Run any of them directly, e.g.:

    python -m benchmarks.window_bench
    python -m cProfile -s cumulative -m benchmarks.window_bench
"""
