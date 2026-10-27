"""
The Detective's Toolkit (DSA Demonstration & Evaluation Center).
Provides comprehensive interactive demonstrations, visualizations, and complexity analyses
for all 5 Course Outcomes (CO1 - CO5).
All buttons use strictly synchronized UI components with immediate feedback banners.
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
from .ui_components import UIButton


class ToolkitView:
    """The Detective's Toolkit View."""

    def __init__(self, investigation_state: InvestigationState) -> None:
        self.state = investigation_state
        self.active_tab = 0  # 0: CO1, 1: CO2, 2: CO3, 3: CO4, 4: CO5
        self.feedback_banner: str = "Welcome to the Detective's Toolkit. Select any Course Outcome tab to test live algorithms."
        self.banner_color: Tuple[int, int, int] = COLOR_VERIFIED

        # Top Tabs
        self.tab_buttons: List[UIButton] = []
        self._init_tabs()

        # Dynamic tab action buttons
        self.tab_action_buttons: List[UIButton] = []

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
        val, path = self.state.case.evidence_bst.search("EV-06")
        self.co4_bst_search_res = (val, path)

        # CO5 State
        self.co5_start_node = "SUS-01"
        self.co5_dest_node = "EV-01"
        self.co5_bfs_res = self.state.case.graph.bfs_shortest_path("SUS-01", "EV-01")
        self.co5_dfs_res = self.state.case.graph.dfs_traversal("SUS-01")

    def _init_tabs(self) -> None:
        tab_names = [
            "CO1: Stacks & Queues",
            "CO2: Timeline & Search",
            "CO3: Hash & Sorting",
            "CO4: Trees & Priority",
            "CO5: Graphs & Traversals",
        ]
        self.tab_buttons = []
        for i, name in enumerate(tab_names):
            btn = UIButton(
                pygame.Rect(0, 0, 160, 32),
                name,
                callback=lambda idx=i: self._select_tab(idx),
                font_size=11,
                border_radius=4
            )
            self.tab_buttons.append(btn)

    def _select_tab(self, idx: int) -> None:
        self.active_tab = idx
        descriptions = [
            "CO1: Demonstrating LIFO Undo/Redo Stacks, FIFO Routine Lead Queue, and Max-Heap Priority Leads.",
            "CO2: Demonstrating Chronological Timeline Doubly Linked List and Sequential vs Binary Search.",
            "CO3: Demonstrating Separate Chaining Hash Table buckets and real Sorting & Searching Benchmarks.",
            "CO4: Demonstrating Trie Autocomplete, Binary Search Tree traversals/deletions, and Max-Heap.",
            "CO5: Demonstrating Adjacency List Graph, BFS Shortest Path, and DFS Exploration with Cycle Detection.",
        ]
        self.feedback_banner = descriptions[idx]
        self.banner_color = TEXT_GOLD

    def set_feedback(self, msg: str, color: Tuple[int, int, int] = COLOR_VERIFIED) -> None:
        self.feedback_banner = msg
        self.banner_color = color

    # --------------------------------------------------------------------------
    # EVENT HANDLING
    # --------------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event, rect: pygame.Rect) -> None:
        # Hover handling
        if event.type == pygame.MOUSEMOTION:
            for btn in self.tab_buttons:
                btn.check_hover(event.pos)
            for btn in self.tab_action_buttons:
                btn.check_hover(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.tab_buttons:
                if btn.handle_event(event):
                    return
            for btn in self.tab_action_buttons:
                if btn.handle_event(event):
                    return

        elif event.type == pygame.KEYDOWN:
            if self.active_tab == 3:
                # Typing in Trie prefix
                if event.key == pygame.K_BACKSPACE:
                    self.co4_trie_prefix = self.co4_trie_prefix[:-1]
                    self.co4_trie_matches = self.state.case.autocomplete_trie.autocomplete(self.co4_trie_prefix)
                    self.set_feedback(f"Trie Prefix updated to '{self.co4_trie_prefix}'. Matches: {len(self.co4_trie_matches)}")
                elif event.unicode and len(event.unicode) == 1 and event.unicode.isalnum():
                    self.co4_trie_prefix += event.unicode
                    self.co4_trie_matches = self.state.case.autocomplete_trie.autocomplete(self.co4_trie_prefix)
                    self.set_feedback(f"Trie Prefix updated to '{self.co4_trie_prefix}'. Matches: {len(self.co4_trie_matches)}")

    # --------------------------------------------------------------------------
    # RENDER DISPATCHER
    # --------------------------------------------------------------------------

    def render(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        pygame.draw.rect(surface, BG_DARKEST, rect)

        # Clear and rebuild dynamic action buttons for active tab
        self.tab_action_buttons.clear()

        # 1. Render Top Tabs
        tab_w = (rect.width - 40) // 5
        for i, btn in enumerate(self.tab_buttons):
            tx = rect.x + 20 + i * tab_w
            ty = rect.y + 12
            btn.update_pos(tx, ty, tab_w - 6, 30)
            btn.is_active = (self.active_tab == i)
            btn.render(surface)

        # 2. Feedback Status Banner
        banner_r = pygame.Rect(rect.x + 20, rect.y + 48, rect.width - 40, 26)
        pygame.draw.rect(surface, BG_PANEL_ALT, banner_r, border_radius=4)
        pygame.draw.rect(surface, self.banner_color, banner_r, width=1, border_radius=4)
        f_tiny = FontManager.get(size=11, bold=True)
        fb_s = f_tiny.render(f"ACTION STATUS: {self.feedback_banner}", True, self.banner_color)
        surface.blit(fb_s, (banner_r.x + 12, banner_r.y + 6))

        # 3. Tab Content Box
        content_rect = pygame.Rect(rect.x + 20, rect.y + 80, rect.width - 40, rect.height - 95)
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

    # --------------------------------------------------------------------------
    # TAB 1: CO1 - STACK & QUEUE
    # --------------------------------------------------------------------------

    def _render_co1(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        f_h = FontManager.get(size=15, bold=True, serif=True)
        f_bold = FontManager.get(size=12, bold=True)
        f_tiny = FontManager.get(size=11, bold=False)

        x = rect.x + 24
        y = rect.y + 14

        surface.blit(f_h.render("CO1: STACKS & QUEUES IN INVESTIGATION", True, TEXT_GOLD), (x, y))
        y += 22
        desc = (
            "PURPOSE: The Stack ADT (LIFO) manages undo/redo of board actions and theory notes. "
            "The Queue ADT (FIFO) processes routine witness interviews in order of arrival, "
            "and the Max-Heap Priority Queue prioritizes critical forensic leads."
        )
        surface.blit(f_tiny.render(desc, True, TEXT_MUTED), (x, y))
        y += 26

        # Section A: Stack Undo/Redo
        surface.blit(f_bold.render("1. Undo/Redo Dual-Stack Demonstration", True, TEXT_WHITE), (x, y))
        y += 18

        btn_push = UIButton(pygame.Rect(x, y, 115, 24), "+ Push Action", callback=self._co1_push_action, font_size=10)
        btn_undo = UIButton(pygame.Rect(x + 125, y, 110, 24), "<- Undo (Pop)", callback=self._co1_undo, font_size=10)
        btn_redo = UIButton(pygame.Rect(x + 245, y, 110, 24), "Redo ->", callback=self._co1_redo, font_size=10)

        for btn in [btn_push, btn_undo, btn_redo]:
            btn.render(surface)
            self.tab_action_buttons.append(btn)
        y += 30

        undo_items = self.state.undo_redo.undo_stack.to_list()[-4:]
        redo_items = self.state.undo_redo.redo_stack.to_list()[-4:]
        u_str = " | ".join(str(item.get("type", item)) for item in reversed(undo_items)) if undo_items else "[EMPTY]"
        r_str = " | ".join(str(item.get("type", item)) for item in reversed(redo_items)) if redo_items else "[EMPTY]"

        surface.blit(f_tiny.render(f"Undo Stack (Top -> Bottom): {u_str}", True, TEXT_CYAN), (x, y))
        y += 16
        surface.blit(f_tiny.render(f"Redo Stack (Top -> Bottom): {r_str}", True, TEXT_MUTED), (x, y))
        y += 16
        surface.blit(f_tiny.render("Complexity: Push O(1) amortized, Pop O(1), Peek O(1). Space: O(k) history.", True, TEXT_GOLD), (x, y))
        y += 24

        pygame.draw.line(surface, BG_BORDER, (x, y), (rect.right - 24, y), 1)
        y += 12

        # Section B: FIFO Queue for Routine Leads
        surface.blit(f_bold.render("2. FIFO Queue (Routine Investigation Leads)", True, TEXT_WHITE), (x, y))
        y += 18

        btn_enq = UIButton(pygame.Rect(x, y, 125, 24), "+ Enqueue Lead", callback=self._co1_enqueue, font_size=10)
        btn_deq = UIButton(pygame.Rect(x + 135, y, 140, 24), "Dequeue Front Lead ->", callback=self._co1_dequeue, font_size=10)

        for btn in [btn_enq, btn_deq]:
            btn.render(surface)
            self.tab_action_buttons.append(btn)
        y += 30

        q_items = self.state.case.routine_leads_queue.to_list()[:5]
        q_str = " -> ".join(item.get("name", item.get("id", str(item))) for item in q_items) if q_items else "[QUEUE EMPTY]"
        surface.blit(f_tiny.render(f"Queue Order (Front -> Rear): {q_str}", True, TEXT_CYAN), (x, y))
        y += 16
        surface.blit(f_tiny.render("Complexity: Enqueue O(1), Dequeue O(1). Enforces fair chronological lead triage.", True, TEXT_GOLD), (x, y))
        y += 24

        pygame.draw.line(surface, BG_BORDER, (x, y), (rect.right - 24, y), 1)
        y += 12

        # Section C: Priority Queue (Max-Heap)
        surface.blit(f_bold.render("3. Priority Queue (Max-Heap Urgent Lead Scheduling)", True, TEXT_WHITE), (x, y))
        y += 18

        btn_ext = UIButton(pygame.Rect(x, y, 145, 24), "- Extract Highest Lead", callback=self._co1_extract_max, font_size=10)
        btn_ins = UIButton(pygame.Rect(x + 155, y, 140, 24), "+ Insert Urgent Lead", callback=self._co1_insert_urgent, font_size=10)

        for btn in [btn_ext, btn_ins]:
            btn.render(surface)
            self.tab_action_buttons.append(btn)
        y += 30

        h_items = self.state.case.urgent_leads_heap.to_list()[:4]
        h_str = " | ".join(f"{item.get('name', item.get('id', ''))} (Pri: {item.get('priority', 0)})" for item in h_items) if h_items else "[HEAP EMPTY]"
        surface.blit(f_tiny.render(f"Max-Heap Array Representation: {h_str}", True, TEXT_CYAN), (x, y))
        y += 16
        surface.blit(f_tiny.render("Complexity: Peek Max O(1), Extract Max O(log n), Insert O(log n).", True, TEXT_GOLD), (x, y))

    def _co1_push_action(self) -> None:
        clue_id = f"EV-0{self.co1_action_counter % 9 + 1}"
        self.state.undo_redo.record_action({"type": "inspect_clue", "id": clue_id})
        self.co1_action_counter += 1
        self.set_feedback(f"Recorded action: inspect_clue [{clue_id}] to Undo Stack. Undo stack size: {self.state.undo_redo.undo_stack.size()}")

    def _co1_undo(self) -> None:
        action = self.state.undo_redo.undo()
        if action:
            self.set_feedback(f"Undone action: {action.get('type')}. Moved to Redo Stack.")
        else:
            self.set_feedback("Undo stack is empty! Nothing to undo.", COLOR_UNCONFIRMED)

    def _co1_redo(self) -> None:
        action = self.state.undo_redo.redo()
        if action:
            self.set_feedback(f"Redone action: {action.get('type')}. Restored to Undo Stack.")
        else:
            self.set_feedback("Redo stack is empty! Nothing to redo.", COLOR_UNCONFIRMED)

    def _co1_enqueue(self) -> None:
        lead = {"name": f"Routine Witness #{self.co1_action_counter}", "id": f"LD-{self.co1_action_counter}"}
        self.state.case.routine_leads_queue.enqueue(lead)
        self.co1_action_counter += 1
        self.set_feedback(f"Enqueued '{lead['name']}' to FIFO Queue. Total in queue: {self.state.case.routine_leads_queue.size()}")

    def _co1_dequeue(self) -> None:
        if not self.state.case.routine_leads_queue.is_empty():
            lead = self.state.case.routine_leads_queue.dequeue()
            self.set_feedback(f"Dequeued front lead: '{lead['name']}' from FIFO Queue.")
        else:
            self.set_feedback("Routine leads queue is empty!", COLOR_UNCONFIRMED)

    def _co1_extract_max(self) -> None:
        if not self.state.case.urgent_leads_heap.is_empty():
            top = self.state.case.urgent_leads_heap.extract_max()
            self.set_feedback(f"Extracted top urgent lead: '{top['name']}' (Priority: {top['priority']})")
        else:
            self.set_feedback("Urgent leads heap is empty!", COLOR_UNCONFIRMED)

    def _co1_insert_urgent(self) -> None:
        pri = 75 + (self.co1_action_counter * 5) % 25
        lead = {"name": f"Urgent Interrogation #{self.co1_action_counter}", "id": f"URG-{self.co1_action_counter}", "priority": pri}
        self.state.case.urgent_leads_heap.insert(lead)
        self.co1_action_counter += 1
        self.set_feedback(f"Inserted urgent lead '{lead['name']}' with Priority {pri} into Max-Heap.")

    # --------------------------------------------------------------------------
    # TAB 2: CO2 - TIMELINE & SEARCH
    # --------------------------------------------------------------------------

    def _render_co2(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        f_h = FontManager.get(size=15, bold=True, serif=True)
        f_bold = FontManager.get(size=12, bold=True)
        f_tiny = FontManager.get(size=11, bold=False)

        x = rect.x + 24
        y = rect.y + 14

        surface.blit(f_h.render("CO2: DOUBLY LINKED LIST & TIMELINE STORAGE", True, TEXT_GOLD), (x, y))
        y += 22
        desc = (
            "PURPOSE: The Doubly Linked List ADT maintains bidirectional narrative continuity for the crime timeline. "
            "Each event node stores explicit prev and next pointers, enabling instant O(1) step navigation."
        )
        surface.blit(f_tiny.render(desc, True, TEXT_MUTED), (x, y))
        y += 28

        events = self.state.case.timeline_dll.to_list()
        curr_ev = events[self.co2_current_idx] if events else {}

        surface.blit(f_bold.render("Bidirectional Node Navigation (Pointer Arithmetic)", True, TEXT_WHITE), (x, y))
        y += 18

        btn_p = UIButton(pygame.Rect(x, y, 120, 24), "< Step Prev Pointer", callback=self._co2_prev, font_size=10)
        btn_n = UIButton(pygame.Rect(x + 130, y, 120, 24), "Step Next Pointer >", callback=self._co2_next, font_size=10)

        for btn in [btn_p, btn_n]:
            btn.render(surface)
            self.tab_action_buttons.append(btn)
        y += 32

        node_box = pygame.Rect(x, y, rect.width - 48, 90)
        pygame.draw.rect(surface, BG_DARKEST, node_box, border_radius=5)
        pygame.draw.rect(surface, BG_BORDER, node_box, width=1, border_radius=5)

        prev_id = events[self.co2_current_idx - 1]["id"] if self.co2_current_idx > 0 else "NULL"
        next_id = events[self.co2_current_idx + 1]["id"] if self.co2_current_idx < len(events) - 1 else "NULL"

        surface.blit(f_tiny.render(f"Pointers: prev_ptr -> [{prev_id}]  |  CURRENT NODE: [{curr_ev.get('id', '')}]  |  next_ptr -> [{next_id}]", True, TEXT_CYAN), (node_box.x + 14, node_box.y + 10))
        surface.blit(f_bold.render(f"{curr_ev.get('timestamp', '')} - {curr_ev.get('title', '')}", True, TEXT_WHITE), (node_box.x + 14, node_box.y + 30))
        surface.blit(f_tiny.render(f"Location: {curr_ev.get('location', '')} | Person: {curr_ev.get('related_person', '')}", True, TEXT_LIGHT), (node_box.x + 14, node_box.y + 50))
        surface.blit(f_tiny.render(curr_ev.get('description', ''), True, TEXT_MUTED), (node_box.x + 14, node_box.y + 70))
        y += 105

        surface.blit(f_bold.render("Complexity & Storage Rationale for Course Defense:", True, TEXT_GOLD), (x, y))
        y += 18
        c1 = "- Append / Prepend / Insert After Node: O(1) time because head/tail and adjacent pointers are maintained."
        c2 = "- Forward and Backward Traversal: O(n) total time, O(1) per step navigation."
        c3 = "- Storage Trade-off: Each node requires 2 pointers (prev and next) in exchange for bidirectional agility."
        surface.blit(f_tiny.render(c1, True, TEXT_LIGHT), (x, y))
        y += 16
        surface.blit(f_tiny.render(c2, True, TEXT_LIGHT), (x, y))
        y += 16
        surface.blit(f_tiny.render(c3, True, TEXT_LIGHT), (x, y))

    def _co2_prev(self) -> None:
        if self.co2_current_idx > 0:
            self.co2_current_idx -= 1
            events = self.state.case.timeline_dll.to_list()
            self.set_feedback(f"Stepped to previous event: [{events[self.co2_current_idx]['timestamp']}] {events[self.co2_current_idx]['title']}")

    def _co2_next(self) -> None:
        events = self.state.case.timeline_dll.to_list()
        if self.co2_current_idx < len(events) - 1:
            self.co2_current_idx += 1
            self.set_feedback(f"Stepped to next event: [{events[self.co2_current_idx]['timestamp']}] {events[self.co2_current_idx]['title']}")

    # --------------------------------------------------------------------------
    # TAB 3: CO3 - HASH & SORTING BENCHMARK
    # --------------------------------------------------------------------------

    def _render_co3(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        f_h = FontManager.get(size=15, bold=True, serif=True)
        f_bold = FontManager.get(size=12, bold=True)
        f_tiny = FontManager.get(size=11, bold=False)

        x = rect.x + 24
        y = rect.y + 14

        surface.blit(f_h.render("CO3: HASH TABLE INDEXING & SORTING BENCHMARKS", True, TEXT_GOLD), (x, y))
        y += 22

        ht_stats = self.state.case.evidence_hash_table.collision_stats()
        surface.blit(f_bold.render(f"1. Custom Hash Table (Capacity: {ht_stats['capacity']}, Items: {ht_stats['total_items']}, Load Factor: {ht_stats['load_factor']})", True, TEXT_WHITE), (x, y))
        y += 18

        surface.blit(f_tiny.render("Select Clue ID to probe hash bucket:", True, TEXT_MUTED), (x, y))
        y += 16

        keys = ["EV-01", "EV-02", "EV-04", "EV-06", "EV-09", "EV-99"]
        for i, k in enumerate(keys):
            bx = x + i * 78
            btn_k = UIButton(
                pygame.Rect(bx, y, 70, 24),
                k,
                callback=lambda key=k: self._co3_probe_key(key),
                font_size=10,
                is_active=(self.co3_search_key == k)
            )
            btn_k.render(surface)
            self.tab_action_buttons.append(btn_k)
        y += 30

        if self.co3_search_res:
            r = self.co3_search_res
            status_txt = f"FOUND in Bucket #{r['bucket_index']}" if r["found"] else f"MISS (Bucket #{r['bucket_index']} empty)"
            col = COLOR_VERIFIED if r["found"] else COLOR_UNCONFIRMED
            val_name = r["value"]["name"] if r["found"] else "Non-existent key"
            surface.blit(f_tiny.render(f"Lookup '{r['key']}': {status_txt} -> {val_name}", True, col), (x, y))
        y += 18
        surface.blit(f_tiny.render("Complexity: Average O(1) search/insert. Worst case O(n) under heavy collision. Resolved by separate chaining.", True, TEXT_GOLD), (x, y))
        y += 24

        pygame.draw.line(surface, BG_BORDER, (x, y), (rect.right - 24, y), 1)
        y += 12

        surface.blit(f_bold.render("2. Real Execution Sorting Benchmark (Bubble vs Selection vs Insertion vs Merge)", True, TEXT_WHITE), (x, y))
        y += 16

        table_hdr = f"{'Algorithm':<18} {'Size (N)':<10} {'Comparisons':<14} {'Swaps/Moves':<14} {'Time (us)':<12} {'Complexity'}"
        surface.blit(f_tiny.render(table_hdr, True, TEXT_GOLD), (x, y))
        y += 16

        subset = [r for r in self.sort_benchmark_results if r["size"] == 30]
        for row in subset:
            row_str = f"{row['algorithm']:<18} {row['size']:<10} {row['comparisons']:<14} {row['swaps']:<14} {row['time_us']:<12.1f} {row['time_complexity']}"
            surface.blit(f_tiny.render(row_str, True, TEXT_LIGHT), (x, y))
            y += 16

        y += 8
        btn_re = UIButton(
            pygame.Rect(x, y, 180, 24),
            "Re-run Benchmark Measurements",
            callback=self._co3_rerun_benchmark,
            font_size=10,
            text_color=TEXT_CYAN
        )
        btn_re.render(surface)
        self.tab_action_buttons.append(btn_re)

    def _co3_probe_key(self, key: str) -> None:
        self.co3_search_key = key
        val = self.state.case.evidence_hash_table.search(key)
        bucket = self.state.case.evidence_hash_table.get_bucket_index(key)
        self.co3_search_res = {"key": key, "found": val is not None, "value": val, "bucket_index": bucket}
        status = "FOUND" if val else "NOT FOUND"
        self.set_feedback(f"HashTable lookup for '{key}': {status} in Bucket #{bucket}.")

    def _co3_rerun_benchmark(self) -> None:
        self.sort_benchmark_results = run_sorting_benchmark([15, 30, 60])
        self.search_benchmark_results = run_searching_benchmark(40)
        self.set_feedback("Re-measured execution times and comparison counts for all sorting algorithms.")

    # --------------------------------------------------------------------------
    # TAB 4: CO4 - TRIE & BST & HEAP
    # --------------------------------------------------------------------------

    def _render_co4(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        f_h = FontManager.get(size=15, bold=True, serif=True)
        f_bold = FontManager.get(size=12, bold=True)
        f_tiny = FontManager.get(size=11, bold=False)

        x = rect.x + 24
        y = rect.y + 14

        surface.blit(f_h.render("CO4: HIERARCHICAL TREES & TRIE AUTOCOMPLETE", True, TEXT_GOLD), (x, y))
        y += 22

        # 1. Custom Trie
        surface.blit(f_bold.render("1. Trie (Prefix Tree) Autocomplete for Suspect & Clue Search", True, TEXT_WHITE), (x, y))
        y += 16
        surface.blit(f_tiny.render(f"Active Query Prefix: '{self.co4_trie_prefix}' (Type letters to test Trie matching):", True, TEXT_MUTED), (x, y))
        y += 16

        matches_str = " | ".join(f"{m[0]} ({m[1]['type']})" for m in self.co4_trie_matches[:4]) if self.co4_trie_matches else "[NO MATCHES]"
        surface.blit(f_tiny.render(f"Trie Matches: {matches_str}", True, TEXT_CYAN), (x, y))
        y += 16
        surface.blit(f_tiny.render("Complexity: Insert & Search O(L) where L is string length, independent of total items N.", True, TEXT_GOLD), (x, y))
        y += 24

        pygame.draw.line(surface, BG_BORDER, (x, y), (rect.right - 24, y), 1)
        y += 12

        # 2. Binary Search Tree (BST)
        surface.blit(f_bold.render("2. Binary Search Tree (Evidence Index & Traversal Paths)", True, TEXT_WHITE), (x, y))
        y += 16

        surface.blit(f_tiny.render("Probe BST Key to inspect visited search path:", True, TEXT_MUTED), (x, y))
        y += 16
        bst_keys = ["EV-02", "EV-04", "EV-06", "EV-07", "EV-12"]
        for i, k in enumerate(bst_keys):
            bx = x + i * 78
            btn_k = UIButton(
                pygame.Rect(bx, y, 70, 24),
                k,
                callback=lambda key=k: self._co4_probe_bst(key),
                font_size=10,
                is_active=(self.co4_bst_search_key == k)
            )
            btn_k.render(surface)
            self.tab_action_buttons.append(btn_k)
        y += 30

        if self.co4_bst_search_res:
            val, path = self.co4_bst_search_res
            path_str = " -> ".join(path)
            surface.blit(f_tiny.render(f"Search Path Visited: {path_str} (Hops: {len(path)})", True, TEXT_CYAN), (x, y))
        y += 18

        inorder_keys = [k for k, _ in self.state.case.evidence_bst.inorder()[:8]]
        surface.blit(f_tiny.render(f"Inorder Traversal (L-Root-R Sorted): {' -> '.join(inorder_keys)}...", True, TEXT_LIGHT), (x, y))
        y += 18
        surface.blit(f_tiny.render("Complexity: Average O(log n) search/insert/delete. Worst case O(n) if unbalanced.", True, TEXT_GOLD), (x, y))

    def _co4_probe_bst(self, key: str) -> None:
        self.co4_bst_search_key = key
        val, path = self.state.case.evidence_bst.search(key)
        self.co4_bst_search_res = (val, path)
        self.set_feedback(f"Probed BST for '{key}': Visited {len(path)} node(s): {' -> '.join(path)}")

    # --------------------------------------------------------------------------
    # TAB 5: CO5 - GRAPH NETWORK & TRAVERSALS
    # --------------------------------------------------------------------------

    def _render_co5(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        f_h = FontManager.get(size=15, bold=True, serif=True)
        f_bold = FontManager.get(size=12, bold=True)
        f_tiny = FontManager.get(size=11, bold=False)

        x = rect.x + 24
        y = rect.y + 14

        surface.blit(f_h.render("CO5: ADJACENCY-LIST GRAPH, BFS SHORTEST PATH & DFS", True, TEXT_GOLD), (x, y))
        y += 22

        g = self.state.case.graph
        surface.blit(f_bold.render(f"Case Evidence Network ({g.node_count()} Nodes, {g.edge_count()} Bidirectional Edges)", True, TEXT_WHITE), (x, y))
        y += 18

        surface.blit(f_tiny.render("Select query lead to trace:", True, TEXT_MUTED), (x, y))
        y += 16
        presets = [
            ("SUS-01", "EV-01", "Oliver -> Compass"),
            ("SUS-01", "LOC-04", "Oliver -> Loading Bay"),
            ("SUS-02", "LOC-06", "Evelyn -> Tea Room"),
            ("SUS-03", "EV-03", "Marcus -> Glitch"),
        ]
        for i, (u, v, plabel) in enumerate(presets):
            bx = x + i * 145
            btn_p = UIButton(
                pygame.Rect(bx, y, 138, 24),
                plabel,
                callback=lambda s=u, d=v: self._co5_trace(s, d),
                font_size=10,
                is_active=(self.co5_start_node == u and self.co5_dest_node == v)
            )
            btn_p.render(surface)
            self.tab_action_buttons.append(btn_p)
        y += 30

        surface.blit(f_bold.render("1. Breadth-First Search (Shortest Relationship Chain)", True, TEXT_WHITE), (x, y))
        y += 16
        if self.co5_bfs_res["found"]:
            p_str = " -> ".join(self.co5_bfs_res["path"])
            surface.blit(f_tiny.render(f"Shortest Path ({self.co5_bfs_res['edge_count']} edges): {p_str}", True, TEXT_CYAN), (x, y))
            y += 16
            surface.blit(f_tiny.render(f"Nodes Explored by BFS: {', '.join(self.co5_bfs_res['nodes_explored'][:8])}...", True, TEXT_LIGHT), (x, y))
        y += 18
        surface.blit(f_tiny.render("BFS Complexity: O(V + E) time, O(V) space. Formally guarantees fewest edges in unweighted graph.", True, TEXT_GOLD), (x, y))
        y += 24

        pygame.draw.line(surface, BG_BORDER, (x, y), (rect.right - 24, y), 1)
        y += 12

        surface.blit(f_bold.render("2. Depth-First Search (Exhaustive Branch Exploration & Cycles)", True, TEXT_WHITE), (x, y))
        y += 16
        dfs_order = self.co5_dfs_res["traversal_order"][:10]
        surface.blit(f_tiny.render(f"DFS Traversal Order: {' -> '.join(dfs_order)}...", True, TEXT_CYAN), (x, y))
        y += 16
        cycle_count = len(self.co5_dfs_res["cycles_detected"])
        surface.blit(f_tiny.render(f"Back-edges (Cycles) Detected: {cycle_count} cycle connection(s)", True, COLOR_UNCONFIRMED), (x, y))
        y += 18
        surface.blit(f_tiny.render("DFS Complexity: O(V + E) time, O(V) recursion stack. Explores deep leads before backtracking.", True, TEXT_GOLD), (x, y))

    def _co5_trace(self, start: str, dest: str) -> None:
        self.co5_start_node = start
        self.co5_dest_node = dest
        self.co5_bfs_res = self.state.case.graph.bfs_shortest_path(start, dest)
        self.co5_dfs_res = self.state.case.graph.dfs_traversal(start)
        self.set_feedback(f"Traced lead from {start} to {dest}: BFS found path of {self.co5_bfs_res['edge_count']} edge(s).")
