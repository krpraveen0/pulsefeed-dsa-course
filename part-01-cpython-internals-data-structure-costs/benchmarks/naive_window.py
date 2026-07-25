"""PulseFeed's deliberately naive first-pass ingestion window.

This is the exact `NaiveWindow` implementation Part 1 of the course
profiles with `cProfile` and then fixes. It uses `list.pop(0)` as its FIFO
eviction strategy, which is O(n) per call: CPython's `list_pop_impl` has
to memmove every remaining element down one slot whenever the popped index
isn't the last one (see `Objects/listobject.c` on the CPython source, and
the Python wiki's TimeComplexity page, which lists list "pop intermediate"
as O(n) for exactly this reason: https://wiki.python.org/moin/TimeComplexity).

Do not use this in production code. It exists so you can profile it
yourself and watch `list.pop(0)` become the top line in the cProfile stats
table under a burst-shaped stream -- run it against `window_bench.py` in
this same directory to see the fixed version
(`pulsefeed.window.Window`, backed by `collections.deque`) win by a
widening margin as the window grows.
"""


class NaiveWindow:
    """First-pass PulseFeed ingestion window. Do not ship this."""

    def __init__(self, size):
        self.size = size
        self.posts = []

    def ingest(self, post):
        self.posts.append(post)
        if len(self.posts) > self.size:
            self.posts.pop(0)   # <-- the line the postmortem circled


def _profile_demo(window_size=5_000, num_posts=20_000):
    """Run NaiveWindow under cProfile, the exact pattern from Part 1.

    Call this directly (`python -m benchmarks.naive_window`) to reproduce
    the article's "list.pop(0) is the top line in the stats table" result
    on your own machine.
    """
    import cProfile
    import io
    import pstats
    from pstats import SortKey

    window = NaiveWindow(window_size)

    pr = cProfile.Profile()
    pr.enable()
    for i in range(num_posts):
        window.ingest(i)
    pr.disable()

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats(SortKey.CUMULATIVE)
    ps.print_stats()
    print(s.getvalue())


if __name__ == "__main__":
    _profile_demo()
