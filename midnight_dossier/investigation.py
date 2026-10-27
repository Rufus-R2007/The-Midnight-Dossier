"""
Investigation Manager and Detective Theory State.
Connects UI actions, case queries, graph traversals, and hypothesis building.
"""

from typing import List, Set, Optional, Dict, Any, Tuple
from .case_data import CaseData
from .dsa.stack import UndoRedoManager


class InvestigationState:
    """
    Maintains the detective's active investigation session.
    Tracks examined clues, working theory, query history, and undo/redo actions.
    """

    def __init__(self, case_data: Optional[CaseData] = None) -> None:
        self.case = case_data if case_data is not None else CaseData()
        self.examined_entity_ids: Set[str] = set()
        self.theory_evidence_ids: List[str] = []
        self.active_entity_id: Optional[str] = None
        self.active_path: List[str] = []
        self.active_edges: List[dict] = []
        self.last_query_result: Optional[dict] = None
        self.undo_redo = UndoRedoManager[dict](max_history=50)

        # Mark initial artifact and first suspect as noticed
        self.mark_examined("EV-01")
        self.mark_examined("SUS-01")

    def mark_examined(self, entity_id: str) -> None:
        """Record that player clicked or inspected this clue/entity."""
        if entity_id:
            self.examined_entity_ids.add(entity_id)

    def is_examined(self, entity_id: str) -> bool:
        return entity_id in self.examined_entity_ids

    def toggle_theory_evidence(self, evidence_id: str) -> bool:
        """
        Add or remove evidence from working theory.
        Returns True if added, False if removed.
        """
        if evidence_id in self.theory_evidence_ids:
            self.theory_evidence_ids.remove(evidence_id)
            self.undo_redo.record_action({
                "type": "remove_theory",
                "evidence_id": evidence_id,
            })
            return False
        else:
            self.theory_evidence_ids.append(evidence_id)
            self.mark_examined(evidence_id)
            self.undo_redo.record_action({
                "type": "add_theory",
                "evidence_id": evidence_id,
            })
            return True

    def is_in_theory(self, evidence_id: str) -> bool:
        return evidence_id in self.theory_evidence_ids

    def query_relationship(self, start_id: str, dest_id: str, use_bfs: bool = True) -> dict:
        """
        Find relationship path between two entities using real graph algorithms.
        BFS: Guarantees shortest path in unweighted graph.
        DFS: Explores depth-first exploration route.
        """
        self.mark_examined(start_id)
        self.mark_examined(dest_id)

        if use_bfs:
            res = self.case.graph.bfs_shortest_path(start_id, dest_id)
            if res["found"]:
                self.active_path = res["path"]
                self.active_edges = res["edges"]
            else:
                self.active_path = []
                self.active_edges = []
            res["algorithm"] = "BFS (Shortest Path)"
            self.last_query_result = res
            return res
        else:
            # DFS Traversal exploration
            dfs_res = self.case.graph.dfs_traversal(start_id)
            order = dfs_res["traversal_order"]
            found = dest_id in order
            path = []
            if found:
                idx = order.index(dest_id)
                path = order[:idx + 1]

            res = {
                "found": found,
                "path": path,
                "edges": [],
                "nodes_explored": order,
                "edge_count": max(0, len(path) - 1),
                "algorithm": "DFS (Depth-First Exploration)",
                "cycles_detected": dfs_res["cycles_detected"],
                "explanation": (
                    f"DFS visited {dfs_res['visited_count']} nodes starting from "
                    f"{self.case.graph.nodes[start_id].name}."
                ),
            }
            self.active_path = path
            self.active_edges = []
            self.last_query_result = res
            return res

    def clear_active_path(self) -> None:
        self.active_path.clear()
        self.active_edges.clear()
        self.last_query_result = None

    def autocomplete(self, prefix: str) -> List[Tuple[str, Any]]:
        """Query suspect and evidence autocomplete via custom Trie."""
        return self.case.autocomplete_trie.autocomplete(prefix, max_results=8)

    def get_progress_metrics(self) -> dict:
        """Calculate investigation progress stats for the case header."""
        total_evidence = len(self.case.evidence)
        examined_evidence = sum(1 for ev in self.case.evidence if ev["id"] in self.examined_entity_ids)
        examined_suspects = sum(1 for s in self.case.suspects if s["id"] in self.examined_entity_ids)

        progress_pct = int((examined_evidence / total_evidence) * 70 + (examined_suspects / 4) * 30)
        progress_pct = min(100, max(10, progress_pct))

        return {
            "progress_percent": progress_pct,
            "examined_evidence_count": examined_evidence,
            "total_evidence_count": total_evidence,
            "examined_suspects_count": examined_suspects,
            "total_suspects_count": 4,
            "theory_items_count": len(self.theory_evidence_ids),
        }
