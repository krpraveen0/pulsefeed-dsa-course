"""timeit benchmark for dict insert/delete churn -- the shape of
PulseFeed's trending-hashtag counter (`pulsefeed.trending.TrendingCounter`):
constant increment on mention, constant decrement-then-delete as posts age
out of the trending window.

This measures wall-clock cost per churn cycle. It intentionally does NOT
measure memory -- dict lookup/insert/delete staying O(1) average case
doesn't mean the dict's *memory footprint* behaves the way you'd expect
under a delete-heavy workload. `dict_memory_bench.py` in this directory
covers that half, modeled on CPython bug bpo-33205.

Run directly:

    python -m benchmarks.dict_churn_bench
"""

import timeit

NUM_TAGS = 500
CHURN_CYCLES = (1_000, 10_000, 50_000)
NUMBER = 20

SETUP = f"""
tags = [f"#tag{{i}}" for i in range({NUM_TAGS})]
counts = {{tag: 1 for tag in tags}}
"""

STMT_TEMPLATE = """
for i in range({cycles}):
    tag = tags[i % len(tags)]
    # mention: insert-or-increment
    counts[tag] = counts.get(tag, 0) + 1
    # expire: decrement, delete at zero
    counts[tag] -= 1
    if counts[tag] <= 0:
        del counts[tag]
    # re-mention so the next cycle's lookup for this tag has something
    # to find -- keeps the dict at a steady live-key count, matching
    # PulseFeed's actual churn shape instead of draining to empty.
    counts[tag] = counts.get(tag, 0) + 1
"""


def bench_churn(cycles, number=NUMBER):
    stmt = STMT_TEMPLATE.format(cycles=cycles)
    return timeit.timeit(stmt, setup=SETUP, number=number)


def main():
    print(f"{'churn_cycles':>14} {'total_seconds':>16} {'us_per_cycle':>14}")
    for cycles in CHURN_CYCLES:
        elapsed = bench_churn(cycles)
        per_cycle_us = (elapsed / NUMBER / cycles) * 1e6
        print(f"{cycles:>14} {elapsed:>16.6f} {per_cycle_us:>14.3f}")


if __name__ == "__main__":
    main()
