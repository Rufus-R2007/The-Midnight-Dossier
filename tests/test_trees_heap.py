"""
Unit tests for CO4: Trie, Binary Search Tree, and Max-Heap.
"""

import unittest
from midnight_dossier.dsa.trie import Trie
from midnight_dossier.dsa.bst import BinarySearchTree
from midnight_dossier.dsa.heap import MaxHeap, HeapEmptyError


class TestTrie(unittest.TestCase):
    def test_trie_autocomplete_and_search(self):
        t = Trie()
        t.insert("Oliver Reed", metadata={"role": "Contractor"})
        t.insert("Evelyn Shaw", metadata={"role": "Archivist"})
        t.insert("Marcus Vale", metadata={"role": "Guard"})
        t.insert("Dr. Lena Hart", metadata={"role": "Curator"})
        t.insert("Asterion Compass", metadata={"type": "Artifact"})

        # Search exact
        self.assertTrue(t.search("Oliver Reed"))
        self.assertTrue(t.search("oliver reed"))  # case-insensitive
        self.assertFalse(t.search("Oliver"))

        # Starts with
        self.assertTrue(t.starts_with("oli"))
        self.assertTrue(t.starts_with("ev"))
        self.assertFalse(t.starts_with("xyz"))

        # Autocomplete
        completions = t.autocomplete("ol")
        self.assertEqual(len(completions), 1)
        self.assertEqual(completions[0][0], "Oliver Reed")
        self.assertEqual(completions[0][1]["role"], "Contractor")

        # Unknown prefix
        self.assertEqual(t.autocomplete("unknown_prefix"), [])


class TestBST(unittest.TestCase):
    def test_bst_insert_and_traversals(self):
        bst: BinarySearchTree[int, str] = BinarySearchTree()
        # Insert keys: 50, 30, 70, 20, 40, 60, 80
        keys = [50, 30, 70, 20, 40, 60, 80]
        for k in keys:
            bst.insert(k, f"val_{k}")

        self.assertEqual(bst.size(), 7)

        # Inorder traversal must be strictly ascending
        inorder = [k for k, _ in bst.inorder()]
        self.assertEqual(inorder, [20, 30, 40, 50, 60, 70, 80])

        # Preorder traversal (Root, Left, Right)
        preorder = [k for k, _ in bst.preorder()]
        self.assertEqual(preorder, [50, 30, 20, 40, 70, 60, 80])

        # Postorder traversal (Left, Right, Root)
        postorder = [k for k, _ in bst.postorder()]
        self.assertEqual(postorder, [20, 40, 30, 60, 80, 70, 50])

    def test_bst_search_with_visited_path(self):
        bst: BinarySearchTree[int, str] = BinarySearchTree()
        for k in [50, 30, 70, 20, 40]:
            bst.insert(k, f"val_{k}")

        # Search existing key 40: path should be 50 -> 30 -> 40
        val, path = bst.search(40)
        self.assertEqual(val, "val_40")
        self.assertEqual(path, [50, 30, 40])

        # Search missing key 25: path should be 50 -> 30 -> 20 -> None
        val_miss, path_miss = bst.search(25)
        self.assertIsNone(val_miss)
        self.assertEqual(path_miss, [50, 30, 20])

    def test_bst_deletions(self):
        bst: BinarySearchTree[int, str] = BinarySearchTree()
        for k in [50, 30, 70, 20, 40, 60, 80]:
            bst.insert(k, f"val_{k}")

        # Case 1: Delete leaf node (20)
        self.assertTrue(bst.delete(20))
        self.assertEqual([k for k, _ in bst.inorder()], [30, 40, 50, 60, 70, 80])

        # Case 2: Delete node with one child (30 has only right child 40 now)
        self.assertTrue(bst.delete(30))
        self.assertEqual([k for k, _ in bst.inorder()], [40, 50, 60, 70, 80])

        # Case 3: Delete node with two children (root 50 has 40 and 70)
        self.assertTrue(bst.delete(50))
        # 60 is inorder successor of 50
        self.assertEqual([k for k, _ in bst.inorder()], [40, 60, 70, 80])
        self.assertEqual(bst.size(), 4)


class TestMaxHeap(unittest.TestCase):
    def test_max_heap_operations(self):
        heap: MaxHeap[int] = MaxHeap()
        self.assertTrue(heap.is_empty())

        for num in [15, 30, 8, 45, 22]:
            heap.insert(num)

        self.assertEqual(heap.size(), 5)
        self.assertEqual(heap.peek_max(), 45)

        # Extraction must yield descending order
        extracted = []
        while not heap.is_empty():
            extracted.append(heap.extract_max())

        self.assertEqual(extracted, [45, 30, 22, 15, 8])

    def test_heap_empty_error(self):
        heap: MaxHeap[int] = MaxHeap()
        with self.assertRaises(HeapEmptyError):
            heap.extract_max()
        with self.assertRaises(HeapEmptyError):
            heap.peek_max()


if __name__ == "__main__":
    unittest.main()
