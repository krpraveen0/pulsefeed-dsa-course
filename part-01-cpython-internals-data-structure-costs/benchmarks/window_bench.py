"""timeit A/B: list.pop(0) vs deque.popleft(), scaling window size.

Reproduces the sliding-window slowdown Part 1 of the course walks through:
`window.append(1); window.pop(0)` against a plain list, versus
`window.append(1); window.popleft()` against a `collections.deque`, at a
handful of window sizes. The exact multiple you get depends on your
machine and Python build -- that's the point. Run it yourself instead of
trusting the article's numbers.

Run directly:

    python -m benchmarks.window_bench

Or profile the list version with cProfile, the same pattern used on
`NaiveWindow` in `naive_window.py`:

    python -m cProfile -s cumulative -m benchmarks.window_bench
"""

import timeit

WINDOW_SIZES = (100, 1_000, 10_000, 50_000)
NUMBER = 2_000


def bench_list_pop0(window_size, number=NUMBER):
    return timeit.timeit(
        "window.append(1); window.pop(0)",
        setup=f"window = list(range({window_size}))",
        number=number,
    )


def bench_deque_popleft(window_size, number=NUMBER):
    return timeit.timeit(
        "window.append(1); window.popleft()",
        setup=f"from collections import deque; window = deque(range({window_size}))",
        number=number,
    )


def main():
    print(f"{'window_size':>12} {'list.pop(0) s':>16} {'deque.popleft() s':>20} {'ratio':>10}")
    for size in WINDOW_SIZES:
        list_time = bench_list_pop0(size)
        deque_time = bench_deque_popleft(size)
        ratio = list_time / deque_time if deque_time else float("inf")
        print(f"{size:>12} {list_time:>16.6f} {deque_time:>20.6f} {ratio:>9.1f}x")


if __name__ == "__main__":
    main()
