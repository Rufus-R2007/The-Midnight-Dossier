"""
Unit tests for Case Data, Graph Connectivity, and Accusation Logic.
"""

import unittest
from midnight_dossier.case_data import CaseData


class TestCaseLogic(unittest.TestCase):
    def setUp(self):
        self.case = CaseData()

    def test_entity_and_relationship_counts(self):
        # Guideline: 20-25 entities, 25-35 relationships
        entities = self.case.get_all_entities()
        self.assertGreaterEqual(len(entities), 20)
        self.assertLessEqual(len(entities), 30)

        # 4 suspects, 6 locations, 14 evidence items = 24 entities
        self.assertEqual(len(self.case.suspects), 4)
        self.assertEqual(len(self.case.locations), 6)
        self.assertEqual(len(self.case.evidence), 14)
        self.assertGreaterEqual(len(self.case.relationships), 24)

    def test_bfs_shortest_path_oliver_to_gallery(self):
        # Shortest path between Oliver Reed (SUS-01) and Antiquities Gallery (LOC-01)
        res = self.case.graph.bfs_shortest_path("SUS-01", "LOC-01")
        self.assertTrue(res["found"])
        self.assertIn("SUS-01", res["path"])
        self.assertIn("LOC-01", res["path"])
        self.assertGreater(res["edge_count"], 0)
        self.assertGreater(len(res["edges"]), 0)

    def test_bfs_shortest_path_oliver_to_compass(self):
        # Shortest path between Oliver Reed (SUS-01) and Asterion Compass (EV-01)
        res = self.case.graph.bfs_shortest_path("SUS-01", "EV-01")
        self.assertTrue(res["found"])
        self.assertEqual(res["path"][0], "SUS-01")
        self.assertEqual(res["path"][-1], "EV-01")

    def test_hash_table_evidence_lookup(self):
        ev01 = self.case.evidence_hash_table.search("EV-01")
        self.assertIsNotNone(ev01)
        self.assertEqual(ev01["name"], "Asterion Compass (Stolen)")

        ev04 = self.case.evidence_hash_table.search("EV-04")
        self.assertIsNotNone(ev04)
        self.assertEqual(ev04["name"], "Keycard KC-09 Service Scan")

    def test_timeline_chronological_order(self):
        # Events in DLL must be strictly ascending by minutes
        events = self.case.timeline_dll.to_list()
        self.assertEqual(len(events), 10)
        times = [e["time_minutes"] for e in events]
        self.assertEqual(times, sorted(times))

    def test_autocomplete_trie(self):
        # Typing "ol" should return Oliver Reed
        matches = self.case.autocomplete_trie.autocomplete("ol")
        names = [m[0] for m in matches]
        self.assertIn("Oliver Reed", names)

        # Typing "ast" should return Asterion Compass
        matches_ast = self.case.autocomplete_trie.autocomplete("ast")
        names_ast = [m[0] for m in matches_ast]
        self.assertIn("Asterion Compass (Stolen)", names_ast)

    def test_accusation_correct_with_evidence(self):
        # Oliver Reed with >= 3 key clues
        res = self.case.evaluate_accusation(
            "SUS-01",
            ["EV-02", "EV-04", "EV-05", "EV-06"]
        )
        self.assertEqual(res["verdict"], "GUILTY")
        self.assertTrue(res["is_solved"])
        self.assertIn("WARRANT ISSUED", res["title"])

    def test_accusation_correct_insufficient_evidence(self):
        # Oliver Reed with only 1 clue
        res = self.case.evaluate_accusation(
            "SUS-01",
            ["EV-02"]
        )
        self.assertEqual(res["verdict"], "INSUFFICIENT_EVIDENCE")
        self.assertFalse(res["is_solved"])
        self.assertIn("INSUFFICIENT PROBABLE CAUSE", res["title"])

    def test_accusation_wrong_suspect(self):
        # Evelyn Shaw
        res = self.case.evaluate_accusation(
            "SUS-02",
            ["EV-08", "EV-09"]
        )
        self.assertEqual(res["verdict"], "WRONGFUL_ACCUSATION")
        self.assertFalse(res["is_solved"])
        self.assertIn("innocent", res["message"].lower())


if __name__ == "__main__":
    unittest.main()
