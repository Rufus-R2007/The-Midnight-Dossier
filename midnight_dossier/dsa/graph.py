"""
CO5: Custom Adjacency-List Graph.
Pure Python implementation of Graph ADT for the case evidence network.
Powers connection tracing, BFS shortest path leads, DFS exploration, and cycle detection.
Deterministic neighbor ordering ensures repeatable viva demonstrations.
"""

from typing import Dict, List, Optional, Tuple, Any, Set
from collections import deque


class GraphEdge:
    """An edge representing an investigative relationship between two entities."""

    def __init__(
        self,
        source: str,
        target: str,
        rel_type: str,
        explanation: str,
        evidence_id: Optional[str] = None,
        reliability: str = "VERIFIED"
    ) -> None:
        self.source: str = source
        self.target: str = target
        self.rel_type: str = rel_type
        self.explanation: str = explanation
        self.evidence_id: Optional[str] = evidence_id
        self.reliability: str = reliability  # e.g., VERIFIED, TESTIMONY, UNCONFIRMED, CONTRADICTORY

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "rel_type": self.rel_type,
            "explanation": self.explanation,
            "evidence_id": self.evidence_id,
            "reliability": self.reliability,
        }

    def __repr__(self) -> str:
        return f"Edge({self.source} -[{self.rel_type}]-> {self.target})"


class GraphNode:
    """A node representing an entity (suspect, clue, location, event, artifact)."""

    def __init__(self, node_id: str, name: str, node_type: str, metadata: Optional[dict] = None) -> None:
        self.node_id: str = node_id
        self.name: str = name
        self.node_type: str = node_type  # suspect, clue, location, event, artifact
        self.metadata: dict = metadata or {}

    def __repr__(self) -> str:
        return f"GraphNode({self.node_id}: {self.name})"


class Graph:
    """
    Custom Adjacency-List Graph.
    Uses dictionary of node_id -> GraphNode and node_id -> List[GraphEdge].
    Deterministic neighbor order is maintained by sorting neighbors by target ID.
    """

    def __init__(self) -> None:
        self.nodes: Dict[str, GraphNode] = {}
        self.adj: Dict[str, List[GraphEdge]] = {}

    def add_node(self, node_id: str, name: str, node_type: str, metadata: Optional[dict] = None) -> GraphNode:
        """Add a node to the graph if it doesn't already exist."""
        if node_id not in self.nodes:
            node = GraphNode(node_id, name, node_type, metadata)
            self.nodes[node_id] = node
            self.adj[node_id] = []
        else:
            node = self.nodes[node_id]
            node.name = name
            node.node_type = node_type
            if metadata:
                node.metadata.update(metadata)
        return node

    def add_edge(
        self,
        u: str,
        v: str,
        rel_type: str,
        explanation: str,
        evidence_id: Optional[str] = None,
        reliability: str = "VERIFIED",
        bidirectional: bool = True
    ) -> None:
        """Add an edge between nodes u and v."""
        if u not in self.nodes or v not in self.nodes:
            raise KeyError(f"Both nodes must exist before adding edge: {u} -> {v}")

        edge_fwd = GraphEdge(u, v, rel_type, explanation, evidence_id, reliability)
        self.adj[u].append(edge_fwd)

        if bidirectional and u != v:
            edge_rev = GraphEdge(v, u, rel_type, explanation, evidence_id, reliability)
            self.adj[v].append(edge_rev)

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str) -> List[GraphEdge]:
        """Return deterministic sorted list of outgoing edges."""
        if node_id not in self.adj:
            return []
        return sorted(self.adj[node_id], key=lambda e: (e.target, e.rel_type))

    def bfs_shortest_path(self, start: str, target: str) -> dict:
        """
        Breadth-First Search (BFS) to find the shortest relationship chain between two nodes.
        Guarantees minimum number of edges in an unweighted graph.
        Time Complexity: O(V + E)
        Space Complexity: O(V)
        Returns:
            {
                "found": bool,
                "path": List[str], # node IDs
                "edges": List[dict], # edge metadata along path
                "nodes_explored": List[str],
                "edge_count": int,
                "explanation": str
            }
        """
        if start not in self.nodes or target not in self.nodes:
            return {
                "found": False,
                "path": [],
                "edges": [],
                "nodes_explored": [],
                "edge_count": 0,
                "explanation": f"Node {start if start not in self.nodes else target} does not exist in graph."
            }

        if start == target:
            return {
                "found": True,
                "path": [start],
                "edges": [],
                "nodes_explored": [start],
                "edge_count": 0,
                "explanation": f"Source and destination are the same entity ({self.nodes[start].name})."
            }

        queue: deque = deque([start])
        visited: Set[str] = {start}
        parent: Dict[str, Tuple[str, GraphEdge]] = {}
        nodes_explored: List[str] = []

        found = False
        while queue:
            curr = queue.popleft()
            nodes_explored.append(curr)

            if curr == target:
                found = True
                break

            for edge in self.get_neighbors(curr):
                neighbor = edge.target
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = (curr, edge)
                    queue.append(neighbor)

        if not found:
            return {
                "found": False,
                "path": [],
                "edges": [],
                "nodes_explored": nodes_explored,
                "edge_count": 0,
                "explanation": f"No investigative connection found between {self.nodes[start].name} and {self.nodes[target].name}."
            }

        # Reconstruct path from target to start
        path: List[str] = []
        edges: List[dict] = []
        curr_step = target
        while curr_step != start:
            path.append(curr_step)
            prev_node, edge_used = parent[curr_step]
            edges.append(edge_used.to_dict())
            curr_step = prev_node
        path.append(start)
        path.reverse()
        edges.reverse()

        return {
            "found": True,
            "path": path,
            "edges": edges,
            "nodes_explored": nodes_explored,
            "edge_count": len(edges),
            "explanation": f"Shortest chain connects via {len(edges)} lead(s)."
        }

    def dfs_traversal(self, start: str) -> dict:
        """
        Depth-First Search (DFS) starting from start node.
        Explores each branch deeply before backtracking.
        Time Complexity: O(V + E)
        Space Complexity: O(V)
        Returns:
            {
                "traversal_order": List[str],
                "visited_count": int,
                "cycles_detected": List[Tuple[str, str]],
            }
        """
        if start not in self.nodes:
            return {"traversal_order": [], "visited_count": 0, "cycles_detected": []}

        visited: Set[str] = set()
        traversal_order: List[str] = []
        cycles: List[Tuple[str, str]] = []

        def _dfs(u: str, p: Optional[str]) -> None:
            visited.add(u)
            traversal_order.append(u)
            for edge in self.get_neighbors(u):
                v = edge.target
                if v not in visited:
                    _dfs(v, u)
                elif v != p and v in visited:
                    cycles.append((u, v))

        _dfs(start, None)

        return {
            "traversal_order": traversal_order,
            "visited_count": len(traversal_order),
            "cycles_detected": cycles,
        }

    def node_count(self) -> int:
        return len(self.nodes)

    def edge_count(self) -> int:
        total = sum(len(edges) for edges in self.adj.values())
        return total // 2  # Bidirectional pairs counted once

    def clear(self) -> None:
        self.nodes.clear()
        self.adj.clear()
