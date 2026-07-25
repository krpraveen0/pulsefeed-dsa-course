"""PulseFeed — Part 1: the fixed containers.

`pulsefeed.window.Window` and `pulsefeed.trending.TrendingCounter` are the
*fixed* versions of the two containers the Part 1 article profiles and
diagnoses. The deliberately naive, pre-fix version (`NaiveWindow`, the one
that shipped `list.pop(0)` to production) lives in `benchmarks/naive_window.py`
so it stays next to the benchmark that reproduces its cost, not mixed in
with code meant to actually run in PulseFeed.
"""

from pulsefeed.window import Window
from pulsefeed.trending import TrendingCounter

__all__ = ["Window", "TrendingCounter"]
