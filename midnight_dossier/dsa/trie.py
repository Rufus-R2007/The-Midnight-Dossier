"""
CO4: Custom Trie (Prefix Tree).
Pure Python implementation of Trie for suspect and clue name autocomplete.
Powers the detective case search field with dynamic prefix matching.
"""

from typing import Dict, List, Optional, Tuple, Any


class TrieNode:
    """A single node in the Trie structure."""

    def __init__(self) -> None:
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end_of_word: bool = False
        self.original_text: Optional[str] = None
        self.metadata: Optional[Any] = None


class Trie:
    """
    Custom Prefix Tree (Trie) ADT.
    Provides O(L) time complexity for insert, search, and prefix matching,
    where L is the length of the query string.
    """

    def __init__(self) -> None:
        self.root = TrieNode()
        self._word_count = 0

    def insert(self, word: str, metadata: Optional[Any] = None) -> None:
        """
        Insert a word into the trie. Case-insensitive normalization.
        O(L) time, where L is len(word).
        """
        if not word:
            return

        normalized = word.strip().lower()
        node = self.root

        for char in normalized:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        if not node.is_end_of_word:
            node.is_end_of_word = True
            self._word_count += 1
        node.original_text = word.strip()
        node.metadata = metadata

    def search(self, word: str) -> bool:
        """
        Check if an exact word exists in the trie. O(L).
        """
        if not word:
            return False

        normalized = word.strip().lower()
        node = self.root

        for char in normalized:
            if char not in node.children:
                return False
            node = node.children[char]

        return node.is_end_of_word

    def starts_with(self, prefix: str) -> bool:
        """
        Check if any word in the trie starts with prefix. O(L).
        """
        if not prefix:
            return True

        normalized = prefix.strip().lower()
        node = self.root

        for char in normalized:
            if char not in node.children:
                return False
            node = node.children[char]

        return True

    def autocomplete(self, prefix: str, max_results: int = 10) -> List[Tuple[str, Any]]:
        """
        Find all stored items matching the prefix.
        Returns list of (original_word, metadata) tuples.
        Time: O(L + K) where L is prefix length, K is number of nodes in subtree.
        """
        normalized = prefix.strip().lower()
        node = self.root

        # 1. Walk down the prefix path
        for char in normalized:
            if char not in node.children:
                return []
            node = node.children[char]

        # 2. Collect all completions starting from node using DFS
        results: List[Tuple[str, Any]] = []

        def _dfs(curr: TrieNode) -> None:
            if len(results) >= max_results:
                return
            if curr.is_end_of_word and curr.original_text:
                results.append((curr.original_text, curr.metadata))
            # Sort children deterministically
            for ch in sorted(curr.children.keys()):
                _dfs(curr.children[ch])

        _dfs(node)
        return results

    def get_all_words(self) -> List[str]:
        """Return all words stored in the trie in alphabetical order."""
        return [w for w, _ in self.autocomplete("")]

    def size(self) -> int:
        """Return total number of words in the trie."""
        return self._word_count

    def clear(self) -> None:
        self.root = TrieNode()
        self._word_count = 0

    def __len__(self) -> int:
        return self.size()
