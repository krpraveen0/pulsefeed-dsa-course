"""Smoke tests that the benchmark scripts actually run end to end, at
tiny sizes -- not asserting on specific timings (those are hardware- and
build-dependent by design), just that nothing's broken.
"""

from benchmarks import dict_churn_bench, dict_memory_bench, naive_window, window_bench


def test_window_bench_runs():
    list_time = window_bench.bench_list_pop0(window_size=50, number=20)
    deque_time = window_bench.bench_deque_popleft(window_size=50, number=20)
    assert list_time > 0
    assert deque_time > 0


def test_dict_churn_bench_runs():
    elapsed = dict_churn_bench.bench_churn(cycles=100, number=2)
    assert elapsed > 0


def test_dict_memory_bench_runs():
    d, size_full, size_after_delete, size_after_reinsert = dict_memory_bench.build_and_churn(
        initial_size=200, keep=20
    )
    assert len(d) == 40  # kept 20 + reinserted 20 new keys
    assert size_full > 0
    assert size_after_delete > 0
    assert size_after_reinsert > 0


def test_naive_window_profile_demo_runs():
    # tiny sizes -- this is a smoke test for the cProfile wiring, not a
    # benchmark run.
    naive_window._profile_demo(window_size=10, num_posts=50)


def test_dict_memory_bench_default_params_demonstrate_shrink():
    """At the bug report's own scale (10,900 deleted, 923 inserted), the
    fixed GROWTH_RATE formula should shrink the churned dict back down to
    match a freshly built dict -- this is the actual point of the
    benchmark, not just "it runs"."""
    d, size_full, size_after_delete, size_after_reinsert = dict_memory_bench.build_and_churn()
    fresh_size = dict_memory_bench.fresh_dict_size(len(d))
    assert size_after_reinsert == fresh_size
