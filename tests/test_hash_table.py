"""
Unit tests for CO3: Custom Separate-Chaining Hash Table.
"""

import unittest
from midnight_dossier.dsa.hash_table import HashTable


class TestHashTable(unittest.TestCase):
    def test_insert_and_search(self):
        ht: HashTable[str, str] = HashTable(capacity=7)
        ht.insert("EV-01", "The Asterion Compass")
        ht.insert("EV-02", "Camera Maintenance Log")
        ht.insert("EV-03", "CCTV Outage Record")

        self.assertEqual(ht.search("EV-01"), "The Asterion Compass")
        self.assertEqual(ht.search("EV-02"), "Camera Maintenance Log")
        self.assertEqual(ht.search("EV-03"), "CCTV Outage Record")
        self.assertIsNone(ht.search("EV-99"))

    def test_update_existing_key(self):
        ht: HashTable[str, str] = HashTable(capacity=7)
        ht.insert("EV-01", "Draft note")
        self.assertEqual(ht.search("EV-01"), "Draft note")
        ht.insert("EV-01", "Verified Evidence")
        self.assertEqual(ht.search("EV-01"), "Verified Evidence")
        self.assertEqual(ht.size(), 1)

    def test_delete(self):
        ht: HashTable[str, str] = HashTable(capacity=7)
        ht.insert("EV-01", "Item A")
        ht.insert("EV-02", "Item B")

        # Delete existing
        self.assertTrue(ht.delete("EV-01"))
        self.assertIsNone(ht.search("EV-01"))
        self.assertEqual(ht.size(), 1)

        # Delete non-existent
        self.assertFalse(ht.delete("EV-01"))
        self.assertFalse(ht.delete("UNKNOWN"))

    def test_collision_handling(self):
        # Force collisions by creating table with capacity 3
        ht: HashTable[str, int] = HashTable(capacity=3)
        for i in range(10):
            ht.insert(f"CLUE-{i}", i * 10)

        # Verify all 10 keys are intact and retrievable
        self.assertEqual(ht.size(), 10)
        for i in range(10):
            self.assertEqual(ht.search(f"CLUE-{i}"), i * 10)

        stats = ht.collision_stats()
        self.assertGreater(stats["total_items"], 0)
        self.assertGreaterEqual(stats["total_collisions"], 0)

    def test_inspect_bucket(self):
        ht: HashTable[str, str] = HashTable(capacity=5)
        ht.insert("A", "Alpha")
        idx = ht.get_bucket_index("A")
        bucket_items = ht.inspect_bucket(idx)
        self.assertTrue(any(k == "A" and v == "Alpha" for k, v in bucket_items))


if __name__ == "__main__":
    unittest.main()
