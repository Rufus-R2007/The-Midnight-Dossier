"""
Case Timeline View for The Midnight Dossier.
Demonstrates CO2: Doubly Linked List bidirectional navigation and
Sequential vs. Binary Search comparisons on chronological case events.
Uses synchronized interactive buttons with visual hover states.
"""

import pygame
from typing import Optional, List, Dict, Any, Tuple, Callable
from .theme import (
    BG_DARKEST, BG_DARK, BG_PANEL, BG_PANEL_ALT, BG_BORDER,
    TEXT_WHITE, TEXT_LIGHT, TEXT_MUTED, TEXT_GOLD, TEXT_CYAN,
    COLOR_VERIFIED, COLOR_UNCONFIRMED, COLOR_CONTRADICTORY,
    PARCHMENT_CARD, CARD_BORDER, CARD_TEXT_MAIN, CARD_TEXT_MUTED,
    FontManager
)
from .investigation import InvestigationState
from .dsa.linked_list import DoublyLinkedListNode
from .dsa.searching import linear_search, binary_search
from .ui_components import UIButton


class CaseTimelineView:
    """Case Timeline Screen displaying chronological events and search comparisons."""

    def __init__(self, investigation_state: InvestigationState, on_locate_on_board: Optional[Callable[[str], None]] = None) -> None:
        self.state = investigation_state
        self.on_locate_on_board = on_locate_on_board
        self.dll = self.state.case.timeline_dll
        self.current_node: Optional[DoublyLinkedListNode[dict]] = self.dll.head
        self.current_index: int = 0

        # Search benchmark state
        self.selected_target_time: int = 1307  # 21:47 (Blackout)
        self.seq_search_result: Optional[dict] = None
        self.bin_search_result: Optional[dict] = None

        # Interactive buttons
        self.nav_buttons: List[UIButton] = []
        self.preset_buttons: List[UIButton] = []
        self.btn_locate: Optional[UIButton] = None

        self._init_buttons()
        self._run_search_comparison()

    def _init_buttons(self) -> None:
        self.btn_prev = UIButton(pygame.Rect(0, 0, 110, 32), "< Previous", callback=self._go_prev, font_size=11)
        self.btn_next = UIButton(pygame.Rect(0, 0, 110, 32), "Next >", callback=self._go_next, font_size=11)
        self.btn_first = UIButton(pygame.Rect(0, 0, 95, 32), "|< First", callback=self._go_first, font_size=11)
        self.btn_last = UIButton(pygame.Rect(0, 0, 95, 32), ">| Latest", callback=self._go_last, font_size=11)
        self.nav_buttons = [self.btn_prev, self.btn_next, self.btn_first, self.btn_last]

        presets = [
            (1307, "21:47 (Blackout)"),
            (1316, "21:56 (Theft)"),
            (1332, "22:12 (Van Exit)"),
            (1315, "21:55 (Miss)"),
        ]
        self.preset_buttons = []
        for time_val, plabel in presets:
            btn = UIButton(
                pygame.Rect(0, 0, 135, 26),
                plabel,
                callback=lambda tv=time_val: self._select_preset_time(tv),
                font_size=11
            )
            self.preset_buttons.append(btn)

    def _go_prev(self) -> None:
        if self.current_node and self.current_node.prev:
            self.current_node = self.current_node.prev
            self.current_index = max(0, self.current_index - 1)

    def _go_next(self) -> None:
        if self.current_node and self.current_node.next:
            self.current_node = self.current_node.next
            self.current_index += 1

    def _go_first(self) -> None:
        if self.dll.head:
            self.current_node = self.dll.head
            self.current_index = 0

    def _go_last(self) -> None:
        if self.dll.tail:
            self.current_node = self.dll.tail
            self.current_index = self.dll.size() - 1

    def _select_preset_time(self, time_val: int) -> None:
        self.selected_target_time = time_val
        self._run_search_comparison()

    def handle_event(self, event: pygame.event.Event, rect: pygame.Rect) -> None:
        # Hover tracking
        if event.type == pygame.MOUSEMOTION:
            for btn in self.nav_buttons:
                btn.check_hover(event.pos)
            for btn in self.preset_buttons:
                btn.check_hover(event.pos)
            if self.btn_locate:
                self.btn_locate.check_hover(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.nav_buttons:
                if btn.handle_event(event):
                    return
            for btn in self.preset_buttons:
                if btn.handle_event(event):
                    return
            if self.btn_locate and self.btn_locate.handle_event(event):
                return

    def _run_search_comparison(self) -> None:
        """Run sequential search on DLL vs binary search on indexed snapshot."""
        events_list = self.dll.to_list()
        comparisons_seq = 0
        found_seq = False
        idx_seq = -1

        curr = self.dll.head
        hop = 0
        while curr is not None:
            comparisons_seq += 1
            if curr.data["time_minutes"] == self.selected_target_time:
                found_seq = True
                idx_seq = hop
                break
            curr = curr.next
            hop += 1

        self.seq_search_result = {
            "algorithm": "Sequential Search (Doubly Linked List)",
            "comparisons": comparisons_seq,
            "found": found_seq,
            "index": idx_seq,
            "time_complexity": "O(n)",
            "explanation": f"Traversed {comparisons_seq} node pointer(s) sequentially from head.",
        }

        # 2. Binary search on sorted indexed snapshot
        sorted_snapshot = sorted(events_list, key=lambda x: x["time_minutes"])
        idx_bin, stats_bin = binary_search(
            sorted_snapshot,
            self.selected_target_time,
            key=lambda x: x["time_minutes"]
        )

        self.bin_search_result = {
            "algorithm": "Binary Search (Indexed Snapshot Array)",
            "comparisons": stats_bin["comparisons"],
            "found": idx_bin is not None,
            "index": idx_bin,
            "time_complexity": "O(log n)",
            "explanation": f"Bisected search space in {stats_bin['comparisons']} comparison(s) using random array indexing.",
        }

    def render(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render the complete timeline view."""
        pygame.draw.rect(surface, BG_DARKEST, rect)

        font_h = FontManager.get(size=18, bold=True, serif=True)
        font_sub = FontManager.get(size=13, bold=True)
        font_b = FontManager.get(size=12, bold=False)
        font_bold = FontManager.get(size=12, bold=True)
        font_tiny = FontManager.get(size=11, bold=False)

        # Header Title
        title_surf = font_h.render("CASE CHRONOLOGY — DOUBLY LINKED TIMELINE", True, TEXT_GOLD)
        surface.blit(title_surf, (rect.x + 30, rect.y + 20))

        sub_text = "Bidirectional chronological event traversal powered by custom DoublyLinkedList ADT (CO2)."
        sub_surf = font_b.render(sub_text, True, TEXT_MUTED)
        surface.blit(sub_surf, (rect.x + 30, rect.y + 46))

        # Main Event Display Card
        if self.current_node:
            data = self.current_node.data
            card_rect = pygame.Rect(rect.x + 50, rect.y + 78, rect.width - 100, 205)
            pygame.draw.rect(surface, BG_PANEL, card_rect, border_radius=6)
            pygame.draw.rect(surface, BG_BORDER, card_rect, width=1, border_radius=6)

            # Node Pointers Visualization Header
            prev_txt = f"prev: [{self.current_node.prev.data['timestamp']}]" if self.current_node.prev else "prev: NULL (HEAD)"
            next_txt = f"next: [{self.current_node.next.data['timestamp']}]" if self.current_node.next else "next: NULL (TAIL)"
            ptr_str = f"<- {prev_txt}  ====  [Node #{self.current_index + 1} of {self.dll.size()}]  ====  {next_txt} ->"
            ptr_surf = font_tiny.render(ptr_str, True, TEXT_CYAN)
            surface.blit(ptr_surf, (card_rect.x + 20, card_rect.y + 12))

            pygame.draw.line(surface, BG_BORDER, (card_rect.x + 20, card_rect.y + 32), (card_rect.right - 20, card_rect.y + 32), 1)

            # Event Title & Timestamp
            time_badge = pygame.Rect(card_rect.x + 20, card_rect.y + 44, 75, 26)
            pygame.draw.rect(surface, COLOR_VERIFIED, time_badge, border_radius=4)
            ts_surf = font_bold.render(data["timestamp"], True, TEXT_WHITE)
            surface.blit(ts_surf, (time_badge.x + 16, time_badge.y + 5))

            title_surf = font_sub.render(data["title"], True, TEXT_WHITE)
            surface.blit(title_surf, (card_rect.x + 110, card_rect.y + 48))

            # Details
            loc_surf = font_tiny.render(f"Location: {data['location']} | Associated Person: {data['related_person']}", True, TEXT_GOLD)
            surface.blit(loc_surf, (card_rect.x + 20, card_rect.y + 84))

            desc_surf = font_b.render(data["description"], True, TEXT_LIGHT)
            surface.blit(desc_surf, (card_rect.x + 20, card_rect.y + 110))

            ev_txt = f"Corroborating Evidence Attached: [{data['evidence_id']}]"
            ev_surf = font_tiny.render(ev_txt, True, TEXT_CYAN)
            surface.blit(ev_surf, (card_rect.x + 20, card_rect.y + 148))

            # "Locate on Evidence Board" Action Button
            linked_ev_id = data["evidence_id"]
            if self.on_locate_on_board:
                self.btn_locate = UIButton(
                    pygame.Rect(card_rect.right - 190, card_rect.y + 140, 170, 28),
                    f"Locate [{linked_ev_id}] on Board",
                    callback=lambda eid=linked_ev_id: self.on_locate_on_board(eid),
                    font_size=10,
                    bold=True,
                    bg_color=BG_PANEL_ALT,
                    text_color=TEXT_GOLD
                )
                self.btn_locate.render(surface)

        # Navigation Buttons
        btn_y = rect.y + 295
        self.btn_prev.update_pos(rect.x + 50, btn_y)
        self.btn_next.update_pos(rect.x + 170, btn_y)
        self.btn_first.update_pos(rect.x + 290, btn_y)
        self.btn_last.update_pos(rect.x + 395, btn_y)

        # Enable/Disable styling
        self.btn_prev.is_active = bool(self.current_node and self.current_node.prev)
        self.btn_next.is_active = bool(self.current_node and self.current_node.next)

        for btn in self.nav_buttons:
            btn.render(surface)

        # Search Comparison Section (CO2)
        sep_y = rect.y + 345
        pygame.draw.line(surface, BG_BORDER, (rect.x + 30, sep_y), (rect.right - 30, sep_y), 1)

        search_h = font_sub.render("TIMELINE SEARCH COMPARISON: SEQUENTIAL (DLL) VS. BINARY SEARCH (ARRAY)", True, TEXT_GOLD)
        surface.blit(search_h, (rect.x + 30, sep_y + 12))

        desc_cmp = (
            "Sequential search traverses the Doubly Linked List node-by-node (O(n)), "
            "whereas Binary Search operates on a sorted indexed snapshot array (O(log n))."
        )
        surface.blit(font_tiny.render(desc_cmp, True, TEXT_MUTED), (rect.x + 30, sep_y + 34))

        # Target Time Preset Buttons
        p_x = rect.x + 50
        p_y = sep_y + 56
        for i, btn in enumerate(self.preset_buttons):
            time_vals = [1307, 1316, 1332, 1315]
            btn.is_active = (self.selected_target_time == time_vals[i])
            btn.update_pos(p_x + i * 145, p_y)
            btn.render(surface)

        # Comparison Result Cards
        res_y = sep_y + 95
        w_box = (rect.width - 120) // 2

        # Sequential Search Card
        seq_box = pygame.Rect(rect.x + 50, res_y, w_box, 120)
        pygame.draw.rect(surface, BG_PANEL, seq_box, border_radius=5)
        pygame.draw.rect(surface, BG_BORDER, seq_box, width=1, border_radius=5)

        s_title = font_bold.render("1. Sequential Search (Doubly Linked List)", True, TEXT_WHITE)
        surface.blit(s_title, (seq_box.x + 14, seq_box.y + 10))

        if self.seq_search_result:
            r = self.seq_search_result
            status = "FOUND" if r["found"] else "NOT FOUND"
            status_col = COLOR_VERIFIED if r["found"] else COLOR_UNCONFIRMED
            surface.blit(font_tiny.render(f"Result: {status} (at index {r['index']})", True, status_col), (seq_box.x + 14, seq_box.y + 32))
            surface.blit(font_tiny.render(f"Pointers Checked: {r['comparisons']} node(s)", True, TEXT_CYAN), (seq_box.x + 14, seq_box.y + 52))
            surface.blit(font_tiny.render(f"Time Complexity: {r['time_complexity']}", True, TEXT_GOLD), (seq_box.x + 14, seq_box.y + 72))
            surface.blit(font_tiny.render(r["explanation"], True, TEXT_MUTED), (seq_box.x + 14, seq_box.y + 92))

        # Binary Search Card
        bin_box = pygame.Rect(rect.x + 70 + w_box, res_y, w_box, 120)
        pygame.draw.rect(surface, BG_PANEL, bin_box, border_radius=5)
        pygame.draw.rect(surface, BG_BORDER, bin_box, width=1, border_radius=5)

        b_title = font_bold.render("2. Binary Search (Indexed Array Snapshot)", True, TEXT_WHITE)
        surface.blit(b_title, (bin_box.x + 14, bin_box.y + 10))

        if self.bin_search_result:
            r = self.bin_search_result
            status = "FOUND" if r["found"] else "NOT FOUND"
            status_col = COLOR_VERIFIED if r["found"] else COLOR_UNCONFIRMED
            surface.blit(font_tiny.render(f"Result: {status} (at index {r['index']})", True, status_col), (bin_box.x + 14, bin_box.y + 32))
            surface.blit(font_tiny.render(f"Comparisons: {r['comparisons']} step(s)", True, TEXT_CYAN), (bin_box.x + 14, bin_box.y + 52))
            surface.blit(font_tiny.render(f"Time Complexity: {r['time_complexity']}", True, TEXT_GOLD), (bin_box.x + 14, bin_box.y + 72))
            surface.blit(font_tiny.render(r["explanation"], True, TEXT_MUTED), (bin_box.x + 14, bin_box.y + 92))
