"""PulseFeed's trending-hashtag counter and its top-K query.

The counter itself is still Part 1's plain dict (`{hashtag: count}`,
incremented on every mention, decremented and deleted at zero as posts
age out of the window). What's new here is `top_trending`: answering
"what are the top-k right now" with `heapq.nlargest` -- a single pass
over the dict that keeps only k items in a heap, instead of sorting the
whole dict on every request.

`PersistentTrendingQueue` is the documented fix for the case PulseFeed
does *not* need yet: a persistent max-heap whose entries can go stale
because `heapq` has no decrease-key/delete operation ("removing the
entry or changing its priority is more difficult because it would break
the heap structure invariants" -- heapq docs, Priority Queue
Implementation Notes:
https://docs.python.org/3/library/heapq.html#priority-queue-implementation-notes).
The fix is an `entry_finder` dict plus a `REMOVED` sentinel for lazy
deletion, adapted here almost line-for-line from the official docs.
"""

import heapq
import itertools


class TrendingCounter:
    """A plain-dict trending-hashtag counter, insert/delete churn included.

    See Part 1 of the course for the full CPython-internals case for why
    a plain dict is the right container for this workload (bpo-33205,
    "GROWTH_RATE prevents dict shrinking":
    https://bugs.python.org/issue33205).
    """

    def __init__(self):
        self.counts: dict[str, int] = {}

    def mention(self, tag: str) -> None:
        """Record a mention of `tag`, incrementing its live count."""
        self.counts[tag] = self.counts.get(tag, 0) + 1

    def expire(self, tag: str) -> None:
        """Age one mention of `tag` out of the trending window.

        Deletes the key entirely once its count reaches zero.
        """
        if tag not in self.counts:
            return
        self.counts[tag] -= 1
        if self.counts[tag] <= 0:
            del self.counts[tag]

    def top(self, k: int = 5) -> list[tuple[str, int]]:
        """Top-k hashtags by count, queried on demand via `top_trending`."""
        return top_trending(self.counts, k)

    def __len__(self) -> int:
        return len(self.counts)

    def __contains__(self, tag: str) -> bool:
        return tag in self.counts

    def __repr__(self) -> str:
        return f"TrendingCounter({self.counts!r})"


def top_trending(counts: dict[str, int], k: int = 5) -> list[tuple[str, int]]:
    """Top-k `(tag, count)` pairs, without sorting the whole dict.

    `heapq.nlargest` makes a single pass over `counts.items()`, keeping
    only `k` items in an internal heap as it goes -- cheaper than
    `sorted(counts.items(), key=..., reverse=True)[:k]`, which sorts
    everything just to throw most of it away.
    """
    return heapq.nlargest(k, counts.items(), key=lambda kv: kv[1])


class PersistentTrendingQueue:
    """The documented fix for heapq's decrease-key gap, entry_finder style.

    PulseFeed's default (`TrendingCounter` + `top_trending`) does *not*
    use this -- it queries the dict on demand, which sidesteps the
    stale-entry problem entirely because there's no persistent heap to
    go stale. This class is here for the case the article calls out
    explicitly: a query rate high enough that even `nlargest`'s
    O(n log k) pass gets expensive, profiled, not assumed.

    Callers control max-vs-min behavior by choice of `priority`: pass a
    negated count (as the article's naive max-heap example does) to get
    max-priority-first pop order out of `pop_highest()`.
    """

    REMOVED = "<removed-hashtag>"

    def __init__(self):
        self._pq: list[list] = []
        self._entry_finder: dict[str, list] = {}
        self._counter = itertools.count()

    def add_or_update(self, tag: str, priority: int) -> None:
        """Add a new tag or update the priority of an existing one."""
        if tag in self._entry_finder:
            self.remove(tag)
        count = next(self._counter)
        entry = [priority, count, tag]
        self._entry_finder[tag] = entry
        heapq.heappush(self._pq, entry)

    def remove(self, tag: str) -> None:
        """Mark an existing tag's entry as removed. Raises KeyError if absent."""
        entry = self._entry_finder.pop(tag)
        entry[-1] = self.REMOVED

    def pop_highest(self) -> str:
        """Pop and return the tag at the front of the heap. Skips stale entries."""
        while self._pq:
            _priority, _count, tag = heapq.heappop(self._pq)
            if tag is not self.REMOVED:
                del self._entry_finder[tag]
                return tag
        raise KeyError("pop from an empty priority queue")

    def __contains__(self, tag: str) -> bool:
        return tag in self._entry_finder

    def __len__(self) -> int:
        return len(self._entry_finder)
