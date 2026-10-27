"""
The Detective's Toolkit (DSA Demonstration & Evaluation Center).
Provides comprehensive interactive demonstrations, visualizations, and complexity analyses
for all 5 Course Outcomes (CO1 - CO5).
"""

import pygame
from typing import Dict, List, Optional, Tuple, Any
from .theme import (
    BG_DARKEST, BG_DARK, BG_PANEL, BG_PANEL_ALT, BG_BORDER,
    TEXT_WHITE, TEXT_LIGHT, TEXT_MUTED, TEXT_GOLD, TEXT_CYAN,
    COLOR_VERIFIED, COLOR_UNCONFIRMED, COLOR_CONTRADICTORY,
    COLOR_TESTIMONY, COLOR_SUSPECT, STRING_NORMAL, STRING_ACTIVE,
    FontManager
)
from .investigation import InvestigationState
from .dsa.benchmark import run_sorting_benchmark, run_searching_benchmark
from .dsa.sorting import bubble_sort, selection_sort, insertion_sort, merge_sort
from .dsa.searching import linear_search, binary_search, interpolation_search


class ToolkitView:
    """The Detective's Toolkit View."""

    def __init__(self, investigation_state: InvestigationState) -> None:
        self.state = investigation_state
        self.active_tab = 0  # 0: CO1, 1: CO2, 2: CO3, 3: CO4, 4: CO5

        # CO1 State
        self.co1_action_counter = 1

        # CO2 State
        self.co2_current_idx = 0

        # CO3 State
        self.co3_search_key = "EV-04"
        self.co3_search_res: Optional[dict] = None
        self.sort_benchmark_results = run_sorting_benchmark([15, 30, 60])
        self.search_benchmark_results = run_searching_benchmark(40)

        # CO4 State
        self.co4_trie_prefix = "ol"
        self.co4_trie_matches = self.state.case.autocomplete_trie.autocomplete("ol")
        self.co4_bst_search_key = "EV-06"
        self.co4_bst_search_res: Optional[Tuple[Any, List[str]]] = None
        self.co4_bst_inorder = self.state.case.evidence_bst.inorder()

        # CO5 State
        self.co5_start_node = "SUS-01"
        self.co5_dest_node = "EV-01"
        self.co5_bfs_res = self.state.case.graph.bfs_shortest_path("SUS-01", "EV-01")
        self.co5_dfs_res = self.state.case.graph.dfs_traversal("SUS-01")

    def handle_event(self, event: pygame.event.Event, rect: pygame.Rect) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            rel_x = mx - rect.x
            rel_y = my - rect.y

            # 1. Main CO Tab Switching (Top row)
            if 15 <= rel_y <= 45:
                tab_w = (rect.width - 40) // 5
                for i in range(5):
                    tx = 20 + i * tab_w
                    if tx <= rel_x <= tx + tab_w - 5:
                        self.active_tab = i
                        break

            # 2. Tab-specific interactive controls
            elif self.active_tab == 0:
                self._handle_co1_click(rel_x, rel_y)
            elif self.active_tab == 1:
                self._handle_co2_click(rel_x, rel_y)
            elif self.active_tab == 2:
                self._handle_co3_click(rel_x, rel_y)
            elif self.active_tab == 3:
                self._handle_co4_click(rel_x, rel_y)
            elif self.active_tab == 4:
                self._handle_co5_click(rel_x, rel_y)

        elif event.type == pygame.KEYDOWN:
            if self.active_tab == 3:
                # Typing in Trie prefix
                if event.key == pygame.K_BACKSPACE:
                    self.co4_trie_prefix = self.co4_trie_prefix[:-1]
                    self.co4_trie_matches = self.state.case.autocomplete_trie.autocomplete(self.co4_trie_prefix)
                elif event.unicode and len(event.unicode) == 1 and event.unicode.isalnum():
                    self.co4_trie_prefix += event.unicode
                    self.co4_trie_matches = self.state.case.autocomplete_trie.autocomplete(self.co4_trie_prefix)

    # --------------------------------------------------------------------------
    # TAB INTERACTION HANDLERS
    # --------------------------------------------------------------------------

    def _handle_co1_click(self, lx: int, ly: int) -> None:
        # Stack Undo / Redo controls
        if 200 <= ly <= 230:
            if 30 <= lx <= 140:  # Push action
                self.state.undo_redo.record_action({
                    "type": "inspect_clue",
                    "id": f"EV-0{self.co1_action_counter % 9 + 1}",
                })
                self.co1_action_counter += 1
            elif 150 <= lx <= 250:  # Undo
                self.state.undo_redo.undo()
            elif 260 <= lx <= 360:  # Redo
                self.state.undo_redo.redo()

        # Queue Enqueue / Dequeue
        if 350 <= ly <= 380:
            if 30 <= lx <= 160:  # Enqueue Lead
                self.state.case.routine_leads_queue.enqueue({
                    "name": f"Routine Lead #{self.co1_action_counter}",
                    "id": f"LD-{self.co1_action_counter}",
                })
                self.co1_action_counter += 1
            elif 170 <= lx <= 300:  # Dequeue Lead
                if not self.state.case.routine_leads_queue.is_empty():
                    self.state.case.routine_leads_queue.dequeue()

        # Priority Queue Max-Heap Extract / Peek
        if 500 <= ly <= 530:
            if 30 <= lx <= 170:  # Extract Top Urgent
                if not self.state.case.urgent_leads_heap.is_empty():
                    self.state.case.urgent_leads_heap.extract_max()
            elif 180 <= lx <= 320:  # Insert Urgent Lead
                self.state.case.urgent_leads_heap.insert({
                    "name": f"Urgent Interrogation #{self.co1_action_counter}",
                    "id": f"URG-{self.co1_action_counter}",
                    "priority": 75 + (self.co1_action_counter * 5) % 25,
                })
                self.co1_action_counter += 1

    def _handle_co2_click(self, lx: int, ly: int) -> None:
        events = self.state.case.timeline_dll.to_list()
        if 210 <= ly <= 245:
            if 30 <= lx <= 130 and self.co2_current_idx > 0:
                self.co2_current_idx -= 1
            elif 140 <= lx <= 240 and self.co2_current_idx < len(events) - 1:
                self.co2_current_idx += 1

    def _handle_co3_click(self, lx: int, ly: int) -> None:
        # Key selector buttons for Hash Table lookup
        if 210 <= ly <= 240:
            keys = ["EV-01", "EV-02", "EV-04", "EV-06", "EV-09", "EV-99"]
            for i, k in enumerate(keys):
                bx = 30 + i * 85
                if bx <= lx <= bx + 80:
                    self.co3_search_key = k
                    val = self.state.case.evidence_hash_table.search(k)
                    bucket = self.state.case.evidence_hash_table.get_bucket_index(k)
                    self.co3_search_res = {
                        "key": k,
                        "found": val is not None,
                        "value": val,
                        "bucket_index": bucket,
                    }
                    break

        # Re-run benchmark button
        if 490 <= ly <= 520 and 30 <= lx <= 200:
            self.sort_benchmark_results = run_sorting_benchmark([15, 30, 60])
            self.search_benchmark_results = run_searching_benchmark(40)

    def _handle_co4_click(self, lx: int, ly: int) -> None:
        # BST search keys
        if 320 <= ly <= 350:
            bst_keys = ["EV-02", "EV-04", "EV-06", "EV-07", "EV-12"]
            for i, k in enumerate(bst_keys):
                bx = 30 + i * 85
                if bx <= lx <= bx + 80:
                    self.co4_bst_search_key = k
                    val, path = self.state.case.evidence_bst.search(k)
                    self.co4_bst_search_res = (val, path)
                    break

    def _handle_co5_click(self, lx: int, ly: int) -> None:
        # Presets for relationship paths
        if 200 <= ly <= 230:
            presets = [
                ("SUS-01", "EV-01", "Oliver -> Compass"),
                ("SUS-01", "LOC-04", "Oliver -> Loading Bay"),
                ("SUS-02", "LOC-06", "Evelyn -> Tea Room"),
                ("SUS-03", "EV-03", "Marcus -> CCTV Glitch"),
            ]
            for i, (u, v, _) in enumerate(presets):
                bx = 30 + i * 160
                if bx <= lx <= bx + 150:
                    self.co5_start_node = u
                    self.co5_dest_node = v
                    self.co5_bfs_res = self.state.case.graph.bfs_shortest_path(u, v)
                    self.co5_dfs_res = self.state.case.graph.dfs_traversal(u)
                    break

    # --------------------------------------------------------------------------
    # RENDER DISPATCHER
    # --------------------------------------------------------------------------

    def render(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        pygame.draw.rect(surface, BG_DARKEST, rect)

        # Top Tabs (CO1 to CO5)
        self._render_tabs(surface, rect)

        # Tab Content Box
        content_rect = pygame.Rect(rect.x + 20, rect.y + 60, rect.width - 40, rect.height - 80)
        pygame.draw.rect(surface, BG_PANEL, content_rect, border_radius=6)
        pygame.draw.rect(surface, BG_BORDER, content_rect, width=1, border_radius=6)

        if self.active_tab == 0:
            self._render_co1(surface, content_rect)
        elif self.active_tab == 1:
            self._render_co2(surface, content_rect)
        elif self.active_tab == 2:
            self._render_co3(surface, content_rect)
        elif self.active_tab == 3:
            self._render_co4(surface, content_rect)
        elif self.active_tab == 4:
            self._render_co5(surface, content_rect)

    def _render_tabs(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        tab_names = [
            "CO1: Stacks & Queues",
            "CO2: Timeline & Search",
            "CO3: Hash & Sorting",
            "CO4: Trees & Priority Heap",
            "CO5: Graphs & Traversals",
        ]
        font = FontManager.get(size=12, bold=True)
        tab_w = (rect.width - 40) // 5

        for i, name in enumerate(tab_names):
            tx = rect.x + 20 + i * tab_w
            ty = rect.y + 16
            is_active = (self.active_tab == i)

            t_rect = pygame.Rect(tx, ty, tab_w - 6, 32)
            bg = BG_PANEL if is_active else BG_DARK
            border = TEXT_GOLD if is_active else BG_BORDER
            pygame.draw.rect(surface, bg, t_rect, border_top_left_radius=5, border_top_right_radius=5)
            pygame.draw.rect(surface, border, t_rect, width=1, border_top_left_radius=5, border_top_right_radius=5)

            col = TEXT_GOLD if is_active else TEXT_LIGHT
            lbl = font.render(name, True, col)
            surface.blit(lbl, (tx + (tab_w - 6 - lbl.get_width()) // 2, ty + 8))

    # --------------------------------------------------------------------------
    # TAB 1: CO1 - STACK & QUEUE
    # --------------------------------------------------------------------------

    def _render_co1(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        f_h = FontManager.get(size=16, bold=True, serif=True)
        f_b = FontManager.get(size=13, bold=False)
        f_bold = FontManager.get(size=12, bold=True)
        f_tiny = FontManager.get(size=11, bold=False)

        x = rect.x + 24
        y = rect.y + 18

        # 1. Purpose Box
        surface.blit(f_h.render("CO1: STACKS & QUEUES IN INVESTIGATION", True, TEXT_GOLD), (x, y))
        y += 24
        desc = (
            "PURPOSE: The Stack ADT (LIFO) manages undo and redo of board actions and theory notes. "
            "The Queue ADT (FIFO) schedules incoming witness interviews, while the Max-Heap Priority Queue "
            "ranks urgent leads by forensic priority."
        )
        surface.blit(f_tiny.render(desc, True, TEXT_MUTED), (x, y))
        y += 30

        # Section A: Stack Undo/Redo
        surface.blit(f_bold.render("1. Undo/Redo Stack Demonstration", True, TEXT_WHITE), (x, y))
        y += 20

        # Action Buttons
        for bx, blbl in [(x, "+ Push New Action"), (x + 120, "<- Undo (Pop)"), (x + 230, "Redo ->")]:
            btn_r = pygame.Rect(bx, y, 105, 26)
            pygame.draw.rect(surface, BG_PANEL_ALT, btn_r, border_radius=4)
            pygame.draw.rect(surface, BG_BORDER, btn_r, width=1, border_radius=4)
            surface.blit(f_tiny.render(blbl, True, TEXT_LIGHT), (bx + 8, y + 6))
        y += 34

        # Visual Stack Representation
        undo_items = self.state.undo_redo.undo_stack.to_list()[-4:]
        redo_items = self.state.undo_redo.redo_stack.to_list()[-4:]

        u_str = " | ".join(str(item.get("type", item)) for item in reversed(undo_items)) if undo_items else "[EMPTY]"
        r_str = " | ".join(str(item.get("type", item)) for item in reversed(redo_items)) if redo_items else "[EMPTY]"

        surface.blit(f_tiny.render(f"Undo Stack (Top -> Bottom): {u_str}", True, TEXT_CYAN), (x, y))
        y += 18
        surface.blit(f_tiny.render(f"Redo Stack (Top -> Bottom): {r_str}", True, TEXT_MUTED), (x, y))
        y += 18
        surface.blit(f_tiny.render("Complexity: Push O(1) amortized, Pop O(1), Peek O(1). Space: O(k) history.", True, TEXT_GOLD), (x, y))
        y += 28

        pygame.draw.line(surface, BG_BORDER, (x, y), (rect.right - 24, y), 1)
        y += 14

        # Section B: FIFO Queue for Routine Leads
        surface.blit(f_bold.render("2. FIFO Queue (Routine Investigation Leads)", True, TEXT_WHITE), (x, y))
        y += 20

        for bx, blbl in [(x, "+ Enqueue Lead"), (x + 140, "Dequeue Front Lead ->")]:
            btn_r = pygame.Rect(bx, y, 130, 26)
            pygame.draw.rect(surface, BG_PANEL_ALT, btn_r, border_radius=4)
            pygame.draw.rect(surface, BG_BORDER, btn_r, width=1, border_radius=4)
            surface.blit(f_tiny.render(blbl, True, TEXT_LIGHT), (bx + 8, y + 6))
        y += 34

        q_items = self.state.case.routine_leads_queue.to_list()[:5]
        q_str = " -> ".join(item.get("name", item.get("id", str(item))) for item in q_items) if q_items else "[QUEUE EMPTY]"
        surface.blit(f_tiny.render(f"Queue State (Front -> Rear): {q_str}", True, TEXT_CYAN), (x, y))
        y += 18
        surface.blit(f_tiny.render("Complexity: Enqueue O(1), Dequeue O(1). Enforces fair chronological processing.", True, TEXT_GOLD), (x, y))
        y += 28

        pygame.draw.line(surface, BG_BORDER, (x, y), (rect.right - 24, y), 1)
        y += 14

        # Section C: Max-Heap Priority Queue for Urgent Leads
        surface.blit(f_bold.render("3. Priority Queue (Max-Heap Urgent Lead Scheduling)", True, TEXT_WHITE), (x, y))
        y += 20

        for bx, blbl in [(x, "- Extract Highest Lead"), (x + 150, "+ Insert Urgent Lead")]:
            btn_r = pygame.Rect(bx, y, 140, 26)
            pygame.draw.rect(surface, BG_PANEL_ALT, btn_r, border_radius=4)
            pygame.draw.rect(surface, BG_BORDER, btn_r, width=1, border_radius=4)
            surface.blit(f_tiny.render(blbl, True, TEXT_LIGHT), (bx + 8, y + 6))
        y += 34

        h_items = self.state.case.urgent_leads_heap.to_list()[:4]
        h_str = " | ".join(f"{item.get('name', item.get('id', ''))} (Pri: {item.get('priority', 0)})" for item in h_items) if h_items else "[HEAP EMPTY]"
        surface.blit(f_tiny.render(f"Max-Heap Array Representation: {h_str}", True, TEXT_CYAN), (x, y))
        y += 18
        surface.blit(f_tiny.render("Complexity: Peek Max O(1), Extract Max O(log n), Insert O(log n).", True, TEXT_GOLD), (x, y))

    # --------------------------------------------------------------------------
    # TAB 2: CO2 - TIMELINE & SEARCH
    # --------------------------------------------------------------------------

    def _render_co2(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        f_h = FontManager.get(size=16, bold=True, serif=True)
        f_bold = FontManager.get(size=12, bold=True)
        f_tiny = FontManager.get(size=11, bold=False)

        x = rect.x + 24
        y = rect.y + 18

        surface.blit(f_h.render("CO2: DOUBLY LINKED LIST & TIMELINE STORAGE", True, TEXT_GOLD), (x, y))
        y += 24
        desc = (
            "PURPOSE: The Doubly Linked List ADT maintains bidirectional narrative continuity for the crime timeline. "
            "Each event node stores explicit prev and next pointers, enabling instant O(1) step navigation."
        )
        surface.blit(f_tiny.render(desc, True, TEXT_MUTED), (x, y))
        y += 32

        # Node Pointers Walk Controls
        events = self.state.case.timeline_dll.to_list()
        curr_ev = events[self.co2_current_idx] if events else {}

        surface.blit(f_bold.render("Bidirectional Node Navigation (Pointer Arithmetic)", True, TEXT_WHITE), (x, y))
        y += 20

        for bx, blbl in [(x, "< Step Prev Pointer"), (x + 130, "Step Next Pointer >")]:
            btn_r = pygame.Rect(bx, y, 120, 26)
            pygame.draw.rect(surface, BG_PANEL_ALT, btn_r, border_radius=4)
            pygame.draw.rect(surface, BG_BORDER, btn_r, width=1, border_radius=4)
            surface.blit(f_tiny.render(blbl, True, TEXT_LIGHT), (bx + 8, y + 6))
        y += 36

        # Node Card
        node_box = pygame.Rect(x, y, rect.width - 48, 100)
        pygame.draw.rect(surface, BG_DARKEST, node_box, border_radius=5)
        pygame.draw.rect(surface, BG_BORDER, node_box, width=1, border_radius=5)

        prev_id = events[self.co2_current_idx - 1]["id"] if self.co2_current_idx > 0 else "NULL"
        next_id = events[self.co2_current_idx + 1]["id"] if self.co2_current_idx < len(events) - 1 else "NULL"

        surface.blit(f_tiny.render(f"Pointers: prev_ptr -> [{prev_id}]  |  CURRENT NODE: [{curr_ev.get('id', '')}]  |  next_ptr -> [{next_id}]", True, TEXT_CYAN), (node_box.x + 14, node_box.y + 12))
        surface.blit(f_bold.render(f"{curr_ev.get('timestamp', '')} - {curr_ev.get('title', '')}", True, TEXT_WHITE), (node_box.x + 14, node_box.y + 34))
        surface.blit(f_tiny.render(f"Location: {curr_ev.get('location', '')} | Person: {curr_ev.get('related_person', '')}", True, TEXT_LIGHT), (node_box.x + 14, node_box.y + 56))
        surface.blit(f_tiny.render(curr_ev.get('description', ''), True, TEXT_MUTED), (node_box.x + 14, node_box.y + 76))
        y += 120

        # Complexity Analysis
        surface.blit(f_bold.render("Complexity & Storage Rationale for Course Defense:", True, TEXT_GOLD), (x, y))
        y += 20
        c1 = "- Append / Prepend / Insert After Node: O(1) time because head/tail and adjacent pointers are maintained."
        c2 = "- Forward and Backward Traversal: O(n) total time, O(1) per step."
        c3 = "- Storage Trade-off: Each node requires 2 pointers (prev and next) in exchange for bidirectional agility."
        surface.blit(f_tiny.render(c1, True, TEXT_LIGHT), (x, y))
        y += 18
        surface.blit(f_tiny.render(c2, True, TEXT_LIGHT), (x, y))
        y += 18
        surface.blit(f_tiny.render(c3, True, TEXT_LIGHT), (x, y))

    # --------------------------------------------------------------------------
    # TAB 3: CO3 - HASH & SORTING BENCHMARK
    # --------------------------------------------------------------------------

    def _render_co3(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        f_h = FontManager.get(size=16, bold=True, serif=True)
        f_bold = FontManager.get(size=12, bold=True)
        f_tiny = FontManager.get(size=11, bold=False)

        x = rect.x + 24
        y = rect.y + 18

        surface.blit(f_h.render("CO3: HASH TABLE INDEXING & SORTING BENCHMARKS", True, TEXT_GOLD), (x, y))
        y += 24

        # Part 1: Separate Chaining Hash Table
        ht_stats = self.state.case.evidence_hash_table.collision_stats()
        surface.blit(f_bold.render(f"1. Custom Hash Table (Capacity: {ht_stats['capacity']}, Items: {ht_stats['total_items']}, Load Factor: {ht_stats['load_factor']})", True, TEXT_WHITE), (x, y))
        y += 20

        # Key selector buttons
        surface.blit(f_tiny.render("Select Clue ID to probe hash bucket:", True, TEXT_MUTED), (x, y))
        y += 18
        keys = ["EV-01", "EV-02", "EV-04", "EV-06", "EV-09", "EV-99"]
        for i, k in enumerate(keys):
            bx = x + i * 78
            btn_r = pygame.Rect(bx, y, 70, 24)
            is_sel = (self.co3_search_key == k)
            bg = COLOR_VERIFIED if is_sel else BG_PANEL_ALT
            pygame.draw.rect(surface, bg, btn_r, border_radius=3)
            pygame.draw.rect(surface, BG_BORDER, btn_r, width=1, border_radius=3)
            surface.blit(f_tiny.render(k, True, TEXT_WHITE if is_sel else TEXT_LIGHT), (bx + 14, y + 4))
        y += 30

        # Hash Lookup Result
        if self.co3_search_res:
            r = self.co3_search_res
            status_txt = f"FOUND in Bucket #{r['bucket_index']}" if r["found"] else f"MISS (Bucket #{r['bucket_index']} empty)"
            col = COLOR_VERIFIED if r["found"] else COLOR_UNCONFIRMED
            val_name = r["value"]["name"] if r["found"] else "Non-existent key"
            surface.blit(f_tiny.render(f"Lookup '{r['key']}': {status_txt} -> {val_name}", True, col), (x, y))
        y += 20
        surface.blit(f_tiny.render("Complexity: Average O(1) search/insert. Worst case O(n) under heavy collision. Resolved by separate chaining.", True, TEXT_GOLD), (x, y))
        y += 28

        pygame.draw.line(surface, BG_BORDER, (x, y), (rect.right - 24, y), 1)
        y += 14

        # Part 2: Sorting Performance Benchmark
        surface.blit(f_bold.render("2. Real Execution Sorting Benchmark (Bubble vs Selection vs Insertion vs Merge)", True, TEXT_WHITE), (x, y))
        y += 18

        # Header Table
        table_hdr = f"{'Algorithm':<18} {'Size (N)':<10} {'Comparisons':<14} {'Swaps/Moves':<14} {'Time (us)':<12} {'Complexity'}"
        surface.blit(f_tiny.render(table_hdr, True, TEXT_GOLD), (x, y))
        y += 18

        # Display results for N=30
        subset = [r for r in self.sort_benchmark_results if r["size"] == 30]
        for row in subset:
            row_str = f"{row['algorithm']:<18} {row['size']:<10} {row['comparisons']:<14} {row['swaps']:<14} {row['time_us']:<12.1f} {row['time_complexity']}"
            surface.blit(f_tiny.render(row_str, True, TEXT_LIGHT), (x, y))
            y += 18

        y += 10
        # Re-run Benchmark Button
        re_btn = pygame.Rect(x, y, 160, 24)
        pygame.draw.rect(surface, BG_PANEL_ALT, re_btn, border_radius=4)
        pygame.draw.rect(surface, BG_BORDER, re_btn, width=1, border_radius=4)
        surface.blit(f_tiny.render("Re-run Benchmark Measurements", True, TEXT_CYAN), (x + 8, y + 4))

    # --------------------------------------------------------------------------
    # TAB 4: CO4 - TRIE & BST & HEAP
    # --------------------------------------------------------------------------

    def _render_co4(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        f_h = FontManager.get(size=16, bold=True, serif=True)
        f_bold = FontManager.get(size=12, bold=True)
        f_tiny = FontManager.get(size=11, bold=False)

        x = rect.x + 24
        y = rect.y + 18

        surface.blit(f_h.render("CO4: HIERARCHICAL TREES & TRIE AUTOCOMPLETE", True, TEXT_GOLD), (x, y))
        y += 24

        # 1. Custom Trie
        surface.blit(f_bold.render(f"1. Trie (Prefix Tree) Autocomplete for Suspect & Clue Search", True, TEXT_WHITE), (x, y))
        y += 18
        surface.blit(f_tiny.render(f"Active Query Prefix: '{self.co4_trie_prefix}' (Type letters to test Trie matching):", True, TEXT_MUTED), (x, y))
        y += 18

        matches_str = " | ".join(f"{m[0]} ({m[1]['type']})" for m in self.co4_trie_matches[:4]) if self.co4_trie_matches else "[NO MATCHES]"
        surface.blit(f_tiny.render(f"Trie Matches: {matches_str}", True, TEXT_CYAN), (x, y))
        y += 18
        surface.blit(f_tiny.render("Complexity: Insert & Search O(L) where L is string length, independent of tree item count N.", True, TEXT_GOLD), (x, y))
        y += 26

        pygame.draw.line(surface, BG_BORDER, (x, y), (rect.right - 24, y), 1)
        y += 14

        # 2. Binary Search Tree (BST)
        surface.blit(f_bold.render("2. Binary Search Tree (Evidence Index & Traversal Paths)", True, TEXT_WHITE), (x, y))
        y += 18

        # BST Probe buttons
        surface.blit(f_tiny.render("Probe BST Key to inspect visited search path:", True, TEXT_MUTED), (x, y))
        y += 18
        bst_keys = ["EV-02", "EV-04", "EV-06", "EV-07", "EV-12"]
        for i, k in enumerate(bst_keys):
            bx = x + i * 78
            btn_r = pygame.Rect(bx, y, 70, 24)
            is_sel = (self.co4_bst_search_key == k)
            bg = COLOR_VERIFIED if is_sel else BG_PANEL_ALT
            pygame.draw.rect(surface, bg, btn_r, border_radius=3)
            pygame.draw.rect(surface, BG_BORDER, btn_r, width=1, border_radius=3)
            surface.blit(f_tiny.render(k, True, TEXT_WHITE if is_sel else TEXT_LIGHT), (bx + 14, y + 4))
        y += 30

        if self.co4_bst_search_res:
            val, path = self.co4_bst_search_res
            path_str = " -> ".join(path)
            surface.blit(f_tiny.render(f"Search Path Visited: {path_str} (Hops: {len(path)})", True, TEXT_CYAN), (x, y))
        y += 20

        # Inorder Traversal
        inorder_keys = [k for k, _ in self.state.case.evidence_bst.inorder()[:8]]
        surface.blit(f_tiny.render(f"Inorder Traversal (L-Root-R Sorted): {' -> '.join(inorder_keys)}...", True, TEXT_LIGHT), (x, y))
        y += 20
        surface.blit(f_tiny.render("Complexity: Average O(log n) search/insert/delete. Worst case O(n) if unbalanced.", True, TEXT_GOLD), (x, y))

    # --------------------------------------------------------------------------
    # TAB 5: CO5 - GRAPH NETWORK & TRAVERSALS
    # --------------------------------------------------------------------------

    def _render_co5(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        f_h = FontManager.get(size=16, bold=True, serif=True)
        f_bold = FontManager.get(size=12, bold=True)
        f_tiny = FontManager.get(size=11, bold=False)

        x = rect.x + 24
        y = rect.y + 18

        surface.blit(f_h.render("CO5: ADJACENCY-LIST GRAPH, BFS SHORTEST PATH & DFS", True, TEXT_GOLD), (x, y))
        y += 24

        g = self.state.case.graph
        surface.blit(f_bold.render(f"Case Evidence Network ({g.node_count()} Nodes, {g.edge_count()} Bidirectional Edges)", True, TEXT_WHITE), (x, y))
        y += 20

        # Presets
        surface.blit(f_tiny.render("Select query lead to trace:", True, TEXT_MUTED), (x, y))
        y += 18
        presets = [
            ("SUS-01", "EV-01", "Oliver -> Compass"),
            ("SUS-01", "LOC-04", "Oliver -> Loading Bay"),
            ("SUS-02", "LOC-06", "Evelyn -> Tea Room"),
            ("SUS-03", "EV-03", "Marcus -> Glitch"),
        ]
        for i, (u, v, plabel) in enumerate(presets):
            bx = x + i * 145
            btn_r = pygame.Rect(bx, y, 138, 24)
            is_sel = (self.co5_start_node == u and self.co5_dest_node == v)
            bg = COLOR_VERIFIED if is_sel else BG_PANEL_ALT
            pygame.draw.rect(surface, bg, btn_r, border_radius=3)
            pygame.draw.rect(surface, BG_BORDER, btn_r, width=1, border_radius=3)
            surface.blit(f_tiny.render(plabel, True, TEXT_WHITE if is_sel else TEXT_LIGHT), (bx + 8, y + 4))
        y += 32

        # 1. BFS Shortest Path Results
        surface.blit(f_bold.render("1. Breadth-First Search (Shortest Relationship Chain)", True, TEXT_WHITE), (x, y))
        y += 18
        if self.co5_bfs_res["found"]:
            p_str = " -> ".join(self.co5_bfs_res["path"])
            surface.blit(f_tiny.render(f"Shortest Path ({self.co5_bfs_res['edge_count']} edges): {p_str}", True, TEXT_CYAN), (x, y))
            y += 18
            surface.blit(f_tiny.render(f"Nodes Explored by BFS: {', '.join(self.co5_bfs_res['nodes_explored'][:8])}...", True, TEXT_LIGHT), (x, y))
        y += 20
        surface.blit(f_tiny.render("BFS Complexity: O(V + E) time, O(V) space. Formally guarantees the fewest edges in unweighted graph.", True, TEXT_GOLD), (x, y))
        y += 26

        pygame.draw.line(surface, BG_BORDER, (x, y), (rect.right - 24, y), 1)
        y += 14

        # 2. DFS Exploration Results
        surface.blit(f_bold.render("2. Depth-First Search (Exhaustive Branch Exploration & Cycles)", True, TEXT_WHITE), (x, y))
        y += 18
        dfs_order = self.co5_dfs_res["traversal_order"][:10]
        surface.blit(f_tiny.render(f"DFS Traversal Order: {' -> '.join(dfs_order)}...", True, TEXT_CYAN), (x, y))
        y += 18
        cycle_count = len(self.co5_dfs_res["cycles_detected"])
        surface.blit(f_tiny.render(f"Back-edges (Cycles) Detected: {cycle_count} cycle connection(s)", True, COLOR_UNCONFIRMED), (x, y))
        y += 20
        surface.blit(f_tiny.render("DFS Complexity: O(V + E) time, O(V) recursion stack. Explores deep leads before backtracking.", True, TEXT_GOLD), (x, y))
