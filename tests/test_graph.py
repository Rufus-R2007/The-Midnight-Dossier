"""
Unit tests for CO5: Adjacency-List Graph, BFS Shortest Path, and DFS Exploration.
"""

import unittest
from midnight_dossier.dsa.graph import Graph


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.g = Graph()
        # Create a diamond graph:
        #       B
        #     /   \
        #    A     D
        #     \   /
        #       C
        # And an isolated node E
        self.g.add_node("A", "Suspect A", "suspect")
        self.g.add_node("B", "Corridor B", "location")
        self.g.add_node("C", "Service C", "location")
        self.g.add_node("D", "Vault D", "location")
        self.g.add_node("E", "Isolated Clue E", "clue")

        self.g.add_edge("A", "B", "ACCESSED", "Entered corridor B", "EV-01")
        self.g.add_edge("A", "C", "ACCESSED", "Entered service C", "EV-02")
        self.g.add_edge("B", "D", "CONNECTS_TO", "Leads to vault D", "EV-03")
        self.g.add_edge("C", "D", "CONNECTS_TO", "Alternative door to vault D", "EV-04")

    def test_node_and_edge_counts(self):
        self.assertEqual(self.g.node_count(), 5)
        self.assertEqual(self.g.edge_count(), 4)

    def test_bfs_shortest_path(self):
        result = self.g.bfs_shortest_path("A", "D")
        self.assertTrue(result["found"])
        self.assertEqual(result["edge_count"], 2)
        # Deterministic neighbor order (B comes before C)
        self.assertEqual(result["path"], ["A", "B", "D"])
        self.assertEqual(len(result["edges"]), 2)
        self.assertEqual(result["edges"][0]["source"], "A")
        self.assertEqual(result["edges"][0]["target"], "B")

    def test_bfs_same_node(self):
        result = self.g.bfs_shortest_path("A", "A")
        self.assertTrue(result["found"])
        self.assertEqual(result["path"], ["A"])
        self.assertEqual(result["edge_count"], 0)

    def test_bfs_disconnected_node(self):
        result = self.g.bfs_shortest_path("A", "E")
        self.assertFalse(result["found"])
        self.assertEqual(result["path"], [])
        self.assertIn("No investigative connection", result["explanation"])

    def test_bfs_missing_node(self):
        result = self.g.bfs_shortest_path("A", "NON_EXISTENT")
        self.assertFalse(result["found"])
        self.assertIn("does not exist", result["explanation"])

    def test_dfs_traversal_and_cycles(self):
        dfs_res = self.g.dfs_traversal("A")
        self.assertEqual(dfs_res["visited_count"], 4)  # A, B, D, C (E is disconnected)
        self.assertIn("A", dfs_res["traversal_order"])
        self.assertIn("D", dfs_res["traversal_order"])
        self.assertGreater(len(dfs_res["cycles_detected"]), 0)


if __name__ == "__main__":
    unittest.main()
