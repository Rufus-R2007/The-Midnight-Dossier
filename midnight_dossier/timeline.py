"""
Case Timeline View for The Midnight Dossier.
Demonstrates CO2: Doubly Linked List bidirectional navigation and
Sequential vs. Binary Search comparisons on chronological case events.
"""

import pygame
from typing import Optional, List, Dict, Any, Tuple
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


class CaseTimelineView:
    """Case Timeline Screen displaying chronological events and search comparisons."""

    def __init__(self, investigation_state: InvestigationState) -> None:
        self.state = investigation_state
        self.dll = self.state.case.timeline_dll
        self.current_node: Optional[DoublyLinkedListNode[dict]] = self.dll.head
        self.current_index: int = 0

        # Search benchmark state
        self.selected_target_time: int = 1307  # 21:47 (Blackout)
        self.seq_search_result: Optional[dict] = None
        self.bin_search_result: Optional[dict] = None
        self._run_search_comparison()

    def handle_event(self, event: pygame.event.Event, rect: pygame.Rect) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            rel_x = mx - rect.x
            rel_y = my - rect.y

            # 1. Navigation buttons: [< Prev], [Next >], [First], [Last]
            if 340 <= rel_y <= 380:
                if 80 <= rel_x <= 180 and self.current_node and self.current_node.prev:
                    self.current_node = self.current_node.prev
                    self.current_index = max(0, self.current_index - 1)
                elif 200 <= rel_x <= 300 and self.current_node and self.current_node.next:
                    self.current_node = self.current_node.next
                    self.current_index += 1
                elif 320 <= rel_x <= 410 and self.dll.head:
                    self.current_node = self.dll.head
                    self.current_index = 0
                elif 430 <= rel_x <= 520 and self.dll.tail:
                    self.current_node = self.dll.tail
                    self.current_index = self.dll.size() - 1

            # 2. Timeline search presets
            if 480 <= rel_y <= 515:
                presets = [
                    (80, 1307, "21:47 (Blackout)"),
                    (230, 1316, "21:56 (Theft)"),
                    (380, 1332, "22:12 (Van Exit)"),
                    (530, 1315, "21:55 (Miss)"),
                ]
                for px, time_val, _ in presets:
                    if px <= rel_x <= px + 130:
                        self.selected_target_time = time_val
                        self._run_search_comparison()
                        break

    def _run_search_comparison(self) -> None:
        """Run sequential search on DLL vs binary search on indexed snapshot."""
        # 1. Sequential search on Doubly Linked List
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
        # Background
        pygame.draw.rect(surface, BG_DARKEST, rect)

        font_h = FontManager.get(size=20, bold=True, serif=True)
        font_sub = FontManager.get(size=14, bold=True)
        font_b = FontManager.get(size=13, bold=False)
        font_bold = FontManager.get(size=13, bold=True)
        font_tiny = FontManager.get(size=11, bold=False)

        # Header Title
        title_surf = font_h.render("CASE CHRONOLOGY — DOUBLY LINKED TIMELINE", True, TEXT_GOLD)
        surface.blit(title_surf, (rect.x + 30, rect.y + 24))

        sub_text = "Bidirectional chronological event traversal powered by custom DoublyLinkedList ADT (CO2)."
        sub_surf = font_b.render(sub_text, True, TEXT_MUTED)
        surface.blit(sub_surf, (rect.x + 30, rect.y + 52))

        # Main Event Display Card
        if self.current_node:
            data = self.current_node.data
            card_rect = pygame.Rect(rect.x + 80, rect.y + 100, rect.width - 160, 220)
            pygame.draw.rect(surface, BG_PANEL, card_rect, border_radius=6)
            pygame.draw.rect(surface, BG_BORDER, card_rect, width=1, border_radius=6)

            # Node Pointers Visualization Header
            prev_txt = f"prev: [{self.current_node.prev.data['timestamp']}]" if self.current_node.prev else "prev: NULL (HEAD)"
            next_txt = f"next: [{self.current_node.next.data['timestamp']}]" if self.current_node.next else "next: NULL (TAIL)"
            ptr_str = f"<- {prev_txt}  ====  [Node #{self.current_index + 1} of {self.dll.size()}]  ====  {next_txt} ->"
            ptr_surf = font_tiny.render(ptr_str, True, TEXT_CYAN)
            surface.blit(ptr_surf, (card_rect.x + 20, card_rect.y + 14))

            pygame.draw.line(surface, BG_BORDER, (card_rect.x + 20, card_rect.y + 36), (card_rect.right - 20, card_rect.y + 36), 1)

            # Event Title & Timestamp
            time_badge = pygame.Rect(card_rect.x + 20, card_rect.y + 48, 80, 28)
            pygame.draw.rect(surface, COLOR_VERIFIED, time_badge, border_radius=4)
            ts_surf = font_bold.render(data["timestamp"], True, TEXT_WHITE)
            surface.blit(ts_surf, (time_badge.x + 18, time_badge.y + 6))

            title_surf = font_sub.render(data["title"], True, TEXT_WHITE)
            surface.blit(title_surf, (card_rect.x + 115, card_rect.y + 52))

            # Details
            loc_surf = font_tiny.render(f"Location: {data['location']} | Associated Person: {data['related_person']}", True, TEXT_GOLD)
            surface.blit(loc_surf, (card_rect.x + 20, card_rect.y + 92))

            desc_surf = font_b.render(data["description"], True, TEXT_LIGHT)
            surface.blit(desc_surf, (card_rect.x + 20, card_rect.y + 120))

            ev_txt = f"Linked Corroborating Clue: [{data['evidence_id']}]"
            ev_surf = font_tiny.render(ev_txt, True, TEXT_CYAN)
            surface.blit(ev_surf, (card_rect.x + 20, card_rect.y + 160))

        # Navigation Buttons
        btn_y = rect.y + 340
        btn_prev = pygame.Rect(rect.x + 80, btn_y, 100, 36)
        btn_next = pygame.Rect(rect.x + 200, btn_y, 100, 36)
        btn_first = pygame.Rect(rect.x + 320, btn_y, 90, 36)
        btn_last = pygame.Rect(rect.x + 430, btn_y, 90, 36)

        can_prev = self.current_node and self.current_node.prev is not None
        can_next = self.current_node and self.current_node.next is not None

        for btn, label, active in [(btn_prev, "< Previous", can_prev),
                                   (btn_next, "Next >", can_next),
                                   (btn_first, "|< First", True),
                                   (btn_last, ">| Latest", True)]:
            bg = BG_PANEL_ALT if active else BG_DARK
            txt_col = TEXT_WHITE if active else TEXT_MUTED
            pygame.draw.rect(surface, bg, btn, border_radius=4)
            pygame.draw.rect(surface, BG_BORDER, btn, width=1, border_radius=4)
            lbl = font_bold.render(label, True, txt_col)
            surface.blit(lbl, (btn.x + (btn.width - lbl.get_width()) // 2, btn.y + 10))

        # Search Comparison Section (CO2)
        sep_y = rect.y + 400
        pygame.draw.line(surface, BG_BORDER, (rect.x + 30, sep_y), (rect.right - 30, sep_y), 1)

        search_h = font_sub.render("TIMELINE SEARCH COMPARISON: SEQUENTIAL VS. BINARY SEARCH", True, TEXT_GOLD)
        surface.blit(search_h, (rect.x + 30, sep_y + 16))

        desc_cmp = (
            "Compare searching for a specific timeline event by timestamp: "
            "Sequential search traverses the Doubly Linked List node-by-node (O(n)), "
            "while Binary Search operates on a sorted indexed snapshot array (O(log n))."
        )
        surface.blit(font_tiny.render(desc_cmp, True, TEXT_MUTED), (rect.x + 30, sep_y + 42))

        # Target Time Preset Buttons
        presets = [
            (80, 1307, "21:47 (Blackout)"),
            (230, 1316, "21:56 (Theft)"),
            (380, 1332, "22:12 (Van Exit)"),
            (530, 1315, "21:55 (Miss)"),
        ]
        for px, time_val, plabel in presets:
            btn_r = pygame.Rect(rect.x + px, sep_y + 70, 130, 28)
            is_sel = (self.selected_target_time == time_val)
            bg = COLOR_VERIFIED if is_sel else BG_PANEL
            border = TEXT_GOLD if is_sel else BG_BORDER
            pygame.draw.rect(surface, bg, btn_r, border_radius=4)
            pygame.draw.rect(surface, border, btn_r, width=1, border_radius=4)
            lbl_s = font_tiny.render(plabel, True, TEXT_WHITE if is_sel else TEXT_LIGHT)
            surface.blit(lbl_s, (btn_r.x + 10, btn_r.y + 7))

        # Comparison Result Cards
        res_y = sep_y + 115
        w_box = (rect.width - 180) // 2

        # Sequential Search Card
        seq_box = pygame.Rect(rect.x + 80, res_y, w_box, 130)
        pygame.draw.rect(surface, BG_PANEL, seq_box, border_radius=5)
        pygame.draw.rect(surface, BG_BORDER, seq_box, width=1, border_radius=5)

        s_title = font_bold.render("1. Sequential Search (Linked List)", True, TEXT_WHITE)
        surface.blit(s_title, (seq_box.x + 14, seq_box.y + 12))

        if self.seq_search_result:
            r = self.seq_search_result
            status = "FOUND" if r["found"] else "NOT FOUND"
            status_col = COLOR_VERIFIED if r["found"] else COLOR_UNCONFIRMED
            surface.blit(font_tiny.render(f"Result: {status} (at index {r['index']})", True, status_col), (seq_box.x + 14, seq_box.y + 36))
            surface.blit(font_tiny.render(f"Pointers Checked: {r['comparisons']} node(s)", True, TEXT_CYAN), (seq_box.x + 14, seq_box.y + 58))
            surface.blit(font_tiny.render(f"Time Complexity: {r['time_complexity']}", True, TEXT_GOLD), (seq_box.x + 14, seq_box.y + 80))
            surface.blit(font_tiny.render(r["explanation"], True, TEXT_MUTED), (seq_box.x + 14, seq_box.y + 102))

        # Binary Search Card
        bin_box = pygame.Rect(rect.x + 100 + w_box, res_y, w_box, 130)
        pygame.draw.rect(surface, BG_PANEL, bin_box, border_radius=5)
        pygame.draw.rect(surface, BG_BORDER, bin_box, width=1, border_radius=5)

        b_title = font_bold.render("2. Binary Search (Indexed Array)", True, TEXT_WHITE)
        surface.blit(b_title, (bin_box.x + 14, bin_box.y + 12))

        if self.bin_search_result:
            r = self.bin_search_result
            status = "FOUND" if r["found"] else "NOT FOUND"
            status_col = COLOR_VERIFIED if r["found"] else COLOR_UNCONFIRMED
            surface.blit(font_tiny.render(f"Result: {status} (at index {r['index']})", True, status_col), (bin_box.x + 14, bin_box.y + 36))
            surface.blit(font_tiny.render(f"Comparisons: {r['comparisons']} step(s)", True, TEXT_CYAN), (bin_box.x + 14, bin_box.y + 58))
            surface.blit(font_tiny.render(f"Time Complexity: {r['time_complexity']}", True, TEXT_GOLD), (bin_box.x + 14, bin_box.y + 80))
            surface.blit(font_tiny.render(r["explanation"], True, TEXT_MUTED), (bin_box.x + 14, bin_box.y + 102))
