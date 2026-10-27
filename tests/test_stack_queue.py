"""
Unit tests for CO1: Stack, UndoRedoManager, Queue, CircularQueue, PriorityQueue.
"""

import unittest
from midnight_dossier.dsa.stack import Stack, UndoRedoManager, StackUnderflowError
from midnight_dossier.dsa.queue import Queue, CircularQueue, QueueUnderflowError, QueueOverflowError
from midnight_dossier.dsa.heap import PriorityQueue, HeapEmptyError


class TestStack(unittest.TestCase):
    def test_stack_operations(self):
        s: Stack[str] = Stack()
        self.assertTrue(s.is_empty())
        self.assertEqual(s.size(), 0)

        s.push("card_A")
        s.push("card_B")
        self.assertFalse(s.is_empty())
        self.assertEqual(s.size(), 2)
        self.assertEqual(s.peek(), "card_B")

        popped = s.pop()
        self.assertEqual(popped, "card_B")
        self.assertEqual(s.peek(), "card_A")
        self.assertEqual(s.size(), 1)

    def test_stack_underflow(self):
        s: Stack[int] = Stack()
        with self.assertRaises(StackUnderflowError):
            s.pop()
        with self.assertRaises(StackUnderflowError):
            s.peek()

    def test_undo_redo_manager(self):
        mgr: UndoRedoManager[str] = UndoRedoManager()
        self.assertFalse(mgr.can_undo())
        self.assertFalse(mgr.can_redo())

        mgr.record_action("drag_card_EV01")
        mgr.record_action("add_theory_EV04")
        self.assertTrue(mgr.can_undo())
        self.assertFalse(mgr.can_redo())

        # Undo
        action = mgr.undo()
        self.assertEqual(action, "add_theory_EV04")
        self.assertTrue(mgr.can_redo())

        # Redo
        action2 = mgr.redo()
        self.assertEqual(action2, "add_theory_EV04")
        self.assertFalse(mgr.can_redo())

        # New action clears redo stack
        mgr.undo()
        mgr.record_action("new_action")
        self.assertFalse(mgr.can_redo())


class TestQueue(unittest.TestCase):
    def test_fifo_order(self):
        q: Queue[str] = Queue()
        self.assertTrue(q.is_empty())
        q.enqueue("lead_1")
        q.enqueue("lead_2")
        q.enqueue("lead_3")

        self.assertEqual(q.peek(), "lead_1")
        self.assertEqual(q.dequeue(), "lead_1")
        self.assertEqual(q.dequeue(), "lead_2")
        self.assertEqual(q.dequeue(), "lead_3")
        self.assertTrue(q.is_empty())

    def test_queue_underflow(self):
        q: Queue[str] = Queue()
        with self.assertRaises(QueueUnderflowError):
            q.dequeue()
        with self.assertRaises(QueueUnderflowError):
            q.peek()

    def test_circular_queue(self):
        cq: CircularQueue[int] = CircularQueue(capacity=3)
        self.assertTrue(cq.is_empty())
        cq.enqueue(10)
        cq.enqueue(20)
        cq.enqueue(30)
        self.assertTrue(cq.is_full())

        with self.assertRaises(QueueOverflowError):
            cq.enqueue(40)

        self.assertEqual(cq.dequeue(), 10)
        cq.enqueue(40)  # should wrap around
        self.assertEqual(cq.dequeue(), 20)
        self.assertEqual(cq.dequeue(), 30)
        self.assertEqual(cq.dequeue(), 40)
        self.assertTrue(cq.is_empty())


class TestPriorityQueue(unittest.TestCase):
    def test_priority_order(self):
        pq: PriorityQueue[dict] = PriorityQueue(key=lambda x: x["priority"])
        pq.enqueue({"title": "Check gate", "priority": 3})
        pq.enqueue({"title": "Camera outage", "priority": 9})
        pq.enqueue({"title": "Interrogate guard", "priority": 7})

        top = pq.peek()
        self.assertEqual(top["title"], "Camera outage")

        first = pq.dequeue()
        self.assertEqual(first["title"], "Camera outage")
        second = pq.dequeue()
        self.assertEqual(second["title"], "Interrogate guard")
        third = pq.dequeue()
        self.assertEqual(third["title"], "Check gate")

        with self.assertRaises(HeapEmptyError):
            pq.dequeue()


if __name__ == "__main__":
    unittest.main()
