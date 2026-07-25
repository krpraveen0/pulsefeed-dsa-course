"""PulseFeed's trending-hashtag counter: a plain dict under constant churn.

This is the dict half of the Part 1 article. Hashtags get incremented on
every mention and decremented -- then deleted once they hit zero -- as
posts age out of the trending window. That insert/delete churn is exactly
the workload CPython bug bpo-33205 ("GROWTH_RATE prevents dict shrinking",
https://bugs.python.org/issue33205) was filed against: a dict can get
pinned at several times its live data's needed size purely from deleting
and reinserting keys, even while the live key count stays flat.

`benchmarks/dict_churn_bench.py` times this churn pattern;
`benchmarks/dict_memory_bench.py` tracks the *memory* side of it.
"""


class TrendingCounter:
    """A plain-dict trending-hashtag counter, insert/delete churn included."""

    def __init__(self):
        self.counts = {}

    def mention(self, tag):
        """Record a mention of `tag`, incrementing its live count."""
        self.counts[tag] = self.counts.get(tag, 0) + 1

    def expire(self, tag):
        """Age one mention of `tag` out of the trending window.

        Deletes the key entirely once its count reaches zero -- the
        delete half of the insert/delete churn this module exists to
        demonstrate.
        """
        if tag not in self.counts:
            return
        self.counts[tag] -= 1
        if self.counts[tag] <= 0:
            del self.counts[tag]

    def top(self, k):
        """Return the `k` highest-count tags. Naive full sort on purpose --

        Part 2 replaces this with a `heapq`-based top-K. This part is only
        about the container behind `self.counts`, not the ranking.
        """
        return sorted(self.counts.items(), key=lambda kv: kv[1], reverse=True)[:k]

    def __len__(self):
        return len(self.counts)

    def __contains__(self, tag):
        return tag in self.counts

    def __repr__(self):
        return f"TrendingCounter({self.counts!r})"
