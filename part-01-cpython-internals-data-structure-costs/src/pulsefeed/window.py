"""PulseFeed's fixed ingestion window, built on collections.deque.

This replaces `benchmarks.naive_window.NaiveWindow`, whose `list.pop(0)`
eviction turned a repost burst into a hockey-stick latency graph in
production. See Part 1 of the "Data Structures and Algorithms in Python"
course for the full postmortem and the CPython source-level reason why:
`list.pop(0)` has to memmove every remaining element down one slot, while
`deque` is a doubly linked list of fixed-length blocks where both ends are
genuinely O(1).
"""

from collections import deque


class Window:
    """A bounded FIFO ingestion window backed by a `deque(maxlen=...)`.

    Appending past `size` auto-evicts the oldest post for free -- no
    explicit `pop(0)` call, no O(n) shift, because `deque` never needs to
    move any element besides the one being appended or evicted.
    """

    def __init__(self, size):
        if size <= 0:
            raise ValueError("size must be a positive integer")
        self.size = size
        self.posts = deque(maxlen=size)

    def ingest(self, post):
        self.posts.append(post)  # oldest auto-evicted at maxlen, O(1)

    def __len__(self):
        return len(self.posts)

    def __iter__(self):
        return iter(self.posts)

    def __repr__(self):
        return f"Window(size={self.size}, posts={list(self.posts)!r})"
