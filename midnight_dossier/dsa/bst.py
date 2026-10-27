"""
CO4: Custom Binary Search Tree (BST).
Pure Python implementation of Binary Search Tree for evidence record indexing.
Supports full insertion, search with visited path tracking, three-case deletion,
and inorder/preorder/postorder traversals.
"""

from typing import Generic, TypeVar, Optional, List, Tuple, Any

K = TypeVar("K")
V = TypeVar("V")


class BSTNode(Generic[K, V]):
    """Node in a Binary Search Tree."""

    def __init__(self, key: K, value: Optional[V] = None) -> None:
        self.key: K = key
        self.value: Optional[V] = value
        self.left: Optional["BSTNode[K, V]"] = None
        self.right: Optional["BSTNode[K, V]"] = None

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

    def has_one_child(self) -> bool:
        return (self.left is not None and self.right is None) or \
               (self.left is None and self.right is not None)

    def __repr__(self) -> str:
        return f"BSTNode({self.key!r})"


class BinarySearchTree(Generic[K, V]):
    """
    Custom Binary Search Tree ADT.
    Keys must support comparison operations (<, >, ==).
    Time Complexity:
      - Average case: O(log n) for search, insert, delete
      - Worst case (skewed): O(n)
    """

    def __init__(self) -> None:
        self.root: Optional[BSTNode[K, V]] = None
        self._size: int = 0

    def insert(self, key: K, value: Optional[V] = None) -> None:
        """Insert key-value pair into the BST."""
        new_node = BSTNode(key, value)
        if self.root is None:
            self.root = new_node
            self._size += 1
            return

        curr = self.root
        while True:
            if key == curr.key:
                # Update existing key's value
                curr.value = value
                return
            elif key < curr.key:
                if curr.left is None:
                    curr.left = new_node
                    self._size += 1
                    return
                curr = curr.left
            else:
                if curr.right is None:
                    curr.right = new_node
                    self._size += 1
                    return
                curr = curr.right

    def search(self, key: K) -> Tuple[Optional[V], List[K]]:
        """
        Search for key in BST.
        Returns tuple: (value_if_found_or_None, list_of_keys_visited_during_search).
        """
        visited_keys: List[K] = []
        curr = self.root

        while curr is not None:
            visited_keys.append(curr.key)
            if key == curr.key:
                return curr.value, visited_keys
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right

        return None, visited_keys

    def contains(self, key: K) -> bool:
        val, _ = self.search(key)
        return val is not None or (self.root is not None and key == self.root.key)

    def delete(self, key: K) -> bool:
        """
        Delete a key from the BST.
        Handles:
          1. Leaf node deletion.
          2. One-child node deletion.
          3. Two-children node deletion (replaces with inorder successor).
        Returns True if deleted, False if key not found.
        """
        deleted = False

        def _delete_recursive(node: Optional[BSTNode[K, V]], target_key: K) -> Optional[BSTNode[K, V]]:
            nonlocal deleted
            if node is None:
                return None

            if target_key < node.key:
                node.left = _delete_recursive(node.left, target_key)
                return node
            elif target_key > node.key:
                node.right = _delete_recursive(node.right, target_key)
                return node
            else:
                deleted = True
                # Case 1: Leaf node (no children)
                if node.left is None and node.right is None:
                    return None

                # Case 2: One child (only right child)
                if node.left is None:
                    return node.right

                # Case 2: One child (only left child)
                if node.right is None:
                    return node.left

                # Case 3: Two children
                # Find inorder successor (minimum value in right subtree)
                successor = node.right
                while successor.left is not None:
                    successor = successor.left

                # Copy successor data to current node
                node.key = successor.key
                node.value = successor.value

                # Delete successor node from right subtree
                node.right = _delete_recursive(node.right, successor.key)
                return node

        self.root = _delete_recursive(self.root, key)
        if deleted:
            self._size -= 1
        return deleted

    def inorder(self) -> List[Tuple[K, Optional[V]]]:
        """Inorder traversal (Left, Root, Right) yields keys in sorted order."""
        res: List[Tuple[K, Optional[V]]] = []

        def _traverse(node: Optional[BSTNode[K, V]]) -> None:
            if node is not None:
                _traverse(node.left)
                res.append((node.key, node.value))
                _traverse(node.right)

        _traverse(self.root)
        return res

    def preorder(self) -> List[Tuple[K, Optional[V]]]:
        """Preorder traversal (Root, Left, Right)."""
        res: List[Tuple[K, Optional[V]]] = []

        def _traverse(node: Optional[BSTNode[K, V]]) -> None:
            if node is not None:
                res.append((node.key, node.value))
                _traverse(node.left)
                _traverse(node.right)

        _traverse(self.root)
        return res

    def postorder(self) -> List[Tuple[K, Optional[V]]]:
        """Postorder traversal (Left, Right, Root)."""
        res: List[Tuple[K, Optional[V]]] = []

        def _traverse(node: Optional[BSTNode[K, V]]) -> None:
            if node is not None:
                _traverse(node.left)
                _traverse(node.right)
                res.append((node.key, node.value))

        _traverse(self.root)
        return res

    def height(self) -> int:
        """Calculate height of tree (-1 for empty, 0 for single root)."""
        def _calc_height(node: Optional[BSTNode[K, V]]) -> int:
            if node is None:
                return -1
            return 1 + max(_calc_height(node.left), _calc_height(node.right))

        return _calc_height(self.root)

    def size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self.root is None

    def clear(self) -> None:
        self.root = None
        self._size = 0

    def get_tree_layout(self) -> List[dict]:
        """
        Generate coordinate layout suitable for Detective's Toolkit visualization.
        Returns list of node dicts with {key, x_norm, y_norm, left_key, right_key}.
        """
        if self.root is None:
            return []

        h = max(self.height(), 0)
        nodes: List[dict] = []

        def _layout(node: BSTNode[K, V], depth: int, left_bound: float, right_bound: float) -> None:
            x = (left_bound + right_bound) / 2.0
            y = depth / (h + 1.2) if h > 0 else 0.5
            nodes.append({
                "key": str(node.key),
                "value": node.value,
                "x_norm": x,
                "y_norm": y,
                "left_key": str(node.left.key) if node.left else None,
                "right_key": str(node.right.key) if node.right else None,
            })
            if node.left:
                _layout(node.left, depth + 1, left_bound, x)
            if node.right:
                _layout(node.right, depth + 1, x, right_bound)

        _layout(self.root, 1, 0.0, 1.0)
        return nodes
