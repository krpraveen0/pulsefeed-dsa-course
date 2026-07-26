"""PulseFeed's prefix-autocomplete index: a trie instead of a scan per keystroke.

A `set` of hashtags gives O(1) average lookup for an *exact* match, and
nothing for "everything starting with #pu" except an O(n) scan of every
key it holds -- there's no way to ask a hash table about the shape of
its keys, only their exact values. A trie answers the same query in
O(L + m): L for the length of the prefix walked, m for however many
matches hang off that node, because every string sharing a prefix
shares the traversal down to that point.

Insert/lookup shape follows the standard reference pattern (dict-of-
children nodes with an end-of-word flag), cross-checked against
https://github.com/vivekn/autocomplete/blob/master/trie.py and
https://github.com/kylebgorman/pytrie. `_collect` is the part public
trie snippets tend to wave at and not write: a plain DFS from the
prefix node, appending every `is_end` node found below it.

Not a strictly better hash set memory-wise: a trie only wins on space
when strings actually share meaningful prefixes; for a set of strings
with little prefix overlap, a trie can use *more* memory than a flat
set of the same strings would.
"""


class TrieNode:
    __slots__ = ("children", "is_end")

    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_end = False


class AutocompleteTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, tag: str) -> None:
        node = self.root
        for ch in tag:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True

    def contains(self, tag: str) -> bool:
        """Exact-match lookup, not a prefix query."""
        node = self.root
        for ch in tag:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def _collect(self, node: TrieNode, prefix: str, out: list[str]) -> None:
        if node.is_end:
            out.append(prefix)
        for ch, child in node.children.items():
            self._collect(child, prefix + ch, out)

    def autocomplete(self, prefix: str) -> list[str]:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        matches: list[str] = []
        self._collect(node, prefix, matches)
        return matches
