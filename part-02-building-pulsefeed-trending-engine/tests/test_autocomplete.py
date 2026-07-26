from trending.autocomplete import AutocompleteTrie


def test_autocomplete_on_prefix_with_no_matches():
    trie = AutocompleteTrie()
    trie.insert("#python")
    assert trie.autocomplete("#java") == []


def test_autocomplete_returns_all_shared_prefix_matches():
    trie = AutocompleteTrie()
    for tag in ("#python", "#pythonic", "#pythonista", "#postgres"):
        trie.insert(tag)
    matches = set(trie.autocomplete("#py"))
    assert matches == {"#python", "#pythonic", "#pythonista"}


def test_autocomplete_on_empty_trie_returns_no_matches():
    trie = AutocompleteTrie()
    assert trie.autocomplete("#anything") == []


def test_autocomplete_with_empty_prefix_returns_every_tag():
    trie = AutocompleteTrie()
    trie.insert("#a")
    trie.insert("#b")
    assert set(trie.autocomplete("")) == {"#a", "#b"}


def test_exact_match_tag_is_included_in_its_own_prefix_results():
    trie = AutocompleteTrie()
    trie.insert("#python")
    trie.insert("#pythonic")
    assert "#python" in trie.autocomplete("#python")


def test_contains_is_exact_match_not_prefix():
    trie = AutocompleteTrie()
    trie.insert("#python")
    assert trie.contains("#python") is True
    assert trie.contains("#py") is False
