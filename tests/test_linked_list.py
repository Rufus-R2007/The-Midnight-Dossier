"""
Unit tests for CO2: Doubly Linked List for Chronological Timeline.
"""

import unittest
from midnight_dossier.dsa.linked_list import DoublyLinkedList


class TestDoublyLinkedList(unittest.TestCase):
    def test_empty_list(self):
        dll: DoublyLinkedList[str] = DoublyLinkedList()
        self.assertTrue(dll.is_empty())
        self.assertEqual(dll.size(), 0)
        self.assertIsNone(dll.head)
        self.assertIsNone(dll.tail)
        self.assertEqual(dll.to_list(), [])

    def test_append_and_bidirectional_traversal(self):
        dll: DoublyLinkedList[str] = DoublyLinkedList()
        dll.append("21:15 - Curator Dinner")
        dll.append("21:47 - CCTV Glitch")
        dll.append("21:56 - Power Restored")

        self.assertEqual(dll.size(), 3)
        self.assertEqual(
            dll.to_list(),
            ["21:15 - Curator Dinner", "21:47 - CCTV Glitch", "21:56 - Power Restored"]
        )

        # Backward traversal
        backward = list(dll.backward_iter())
        self.assertEqual(
            backward,
            ["21:56 - Power Restored", "21:47 - CCTV Glitch", "21:15 - Curator Dinner"]
        )

    def test_prepend(self):
        dll: DoublyLinkedList[int] = DoublyLinkedList()
        dll.append(2)
        dll.prepend(1)
        dll.append(3)
        self.assertEqual(dll.to_list(), [1, 2, 3])
        self.assertEqual(dll.head.data, 1)
        self.assertEqual(dll.tail.data, 3)

    def test_insert_after(self):
        dll: DoublyLinkedList[str] = DoublyLinkedList()
        n1 = dll.append("Event A")
        n3 = dll.append("Event C")
        dll.insert_after(n1, "Event B")

        self.assertEqual(dll.to_list(), ["Event A", "Event B", "Event C"])
        self.assertEqual(n1.next.data, "Event B")
        self.assertEqual(n3.prev.data, "Event B")

    def test_delete_nodes(self):
        dll: DoublyLinkedList[int] = DoublyLinkedList()
        n1 = dll.append(10)
        n2 = dll.append(20)
        n3 = dll.append(30)

        # Delete middle node
        val = dll.delete_node(n2)
        self.assertEqual(val, 20)
        self.assertEqual(dll.to_list(), [10, 30])
        self.assertEqual(n1.next, n3)
        self.assertEqual(n3.prev, n1)

        # Delete head
        val_head = dll.delete_node(n1)
        self.assertEqual(val_head, 10)
        self.assertEqual(dll.head, n3)

        # Delete tail
        val_tail = dll.delete_node(n3)
        self.assertEqual(val_tail, 30)
        self.assertTrue(dll.is_empty())

    def test_delete_by_predicate(self):
        dll: DoublyLinkedList[dict] = DoublyLinkedList()
        dll.append({"id": "E1", "time": "21:00"})
        dll.append({"id": "E2", "time": "21:30"})
        dll.append({"id": "E3", "time": "22:00"})

        deleted = dll.delete(lambda x: x["id"] == "E2")
        self.assertEqual(deleted["id"], "E2")
        self.assertEqual(dll.size(), 2)

        # Non-existent
        deleted_none = dll.delete(lambda x: x["id"] == "E99")
        self.assertIsNone(deleted_none)


if __name__ == "__main__":
    unittest.main()
