"""
How to Play Guide and Controls Reference for The Midnight Dossier.
Accessible from the Main Menu and via the top navigation bar at any point in the investigation.
Provides a concise, 6-step detective walkthrough and complete controls reference.
"""

import pygame
from typing import Optional, Callable, List, Tuple
from .theme import (
    BG_DARKEST, BG_DARK, BG_PANEL, BG_PANEL_ALT, BG_BORDER,
    TEXT_WHITE, TEXT_LIGHT, TEXT_MUTED, TEXT_GOLD, TEXT_CYAN,
    COLOR_VERIFIED, COLOR_UNCONFIRMED, COLOR_CONTRADICTORY,
    COLOR_SUSPECT, STRING_NORMAL, STRING_ACTIVE,
    FontManager, draw_pin
)
from .ui_components import UIButton


class HowToPlayView:
    """Modal or standalone view explaining case investigation steps and controls."""

    def __init__(self, on_close: Callable[[], None]) -> None:
        self.on_close = on_close
        self.btn_close = UIButton(
            pygame.Rect(0, 0, 32, 28),
            "X",
            callback=self.on_close,
            font_size=13,
            bold=True,
            bg_color=(120, 35, 40),
            hover_bg=(180, 45, 55),
            text_color=TEXT_WHITE
        )
        self.btn_return = UIButton(
            pygame.Rect(0, 0, 240, 36),
            "CLOSE & RESUME CASE",
            callback=self.on_close,
            font_size=12,
            bold=True,
            bg_color=STRING_NORMAL,
            hover_bg=STRING_ACTIVE,
            text_color=TEXT_WHITE
        )

        self.steps = [
            (
                "Step 1 — Examine the Evidence",
                "Click on any suspect card, physical clue, location, or official record on the corkboard. "
                "Read its verified facts, timestamps, sources, and witness statements in the Case File Dossier."
            ),
            (
                "Step 2 — Follow the Red Strings (CO5: Graphs)",
                "Select two entities in the Relationship Query panel (or use 'Set as From' / 'Set as To'). "
                "Run BFS (Shortest Path) to calculate the minimum-lead connection chain (O(V+E)), or DFS to explore connected routes."
            ),
            (
                "Step 3 — Build Your Theory (CO1: Stacks)",
                "Click '+ Add to Theory Hypothesis' to pin corroborating evidence to your official dossier. "
                "Differentiate verified forensic proof from unconfirmed testimony. Use Undo (Ctrl+Z) if you change your mind."
            ),
            (
                "Step 4 — Investigate the Timeline (CO2: Doubly Linked Lists)",
                "Navigate the chronological timeline with '< Previous' and 'Next >'. Compare sequential pointer traversal (O(n)) "
                "against binary search (O(log n)) on the indexed event snapshot to uncover contradictory alibis."
            ),
            (
                "Step 5 — Use the Detective's Toolkit (CO1 - CO5)",
                "Inspect live data structures: LIFO undo/redo stacks, FIFO lead queue, separate-chaining hash table, "
                "sorting algorithms (Bubble, Selection, Insertion, Merge), searching benchmarks, Trie autocomplete, and BST traversals."
            ),
            (
                "Step 6 — Submit the Final Accusation",
                "Open Final Accusation (Key 4), select your prime suspect, select your corroborating evidence records, "
                "and submit the formal indictment to the District Attorney to resolve the mystery."
            ),
        ]

        self.controls = [
            ("0 / Esc", "Return to Main Menu / Title Screen"),
            ("1", "Investigation Board & Dossier"),
            ("2", "Case Timeline & Search Analysis"),
            ("3", "Detective's Toolkit (All 5 COs)"),
            ("4", "Final Accusation & Case Verdict"),
            ("H / F1", "Open / Close this How to Play Guide"),
            ("Ctrl + Z", "Undo card movement or theory change"),
            ("Ctrl + Y", "Redo previously undone action"),
            ("Drag Cards", "Reposition evidence cards on corkboard"),
            ("Type in Search", "Live suspect / clue autocomplete via Trie"),
        ]

    def handle_event(self, event: pygame.event.Event, rect: pygame.Rect) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.btn_close.check_hover(event.pos)
            self.btn_return.check_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_close.handle_event(event):
                return
            if self.btn_return.handle_event(event):
                return
            # Clicking outside modal
            modal_w = min(960, rect.width - 60)
            modal_h = min(620, rect.height - 60)
            modal_x = rect.x + (rect.width - modal_w) // 2
            modal_y = rect.y + (rect.height - modal_h) // 2
            modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
            if not modal_rect.collidepoint(event.pos):
                self.on_close()
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_h, pygame.K_RETURN, pygame.K_SPACE):
                self.on_close()

    def render(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        # Dim overlay backdrop
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, rect.topleft)

        modal_w = min(960, rect.width - 60)
        modal_h = min(620, rect.height - 60)
        modal_x = rect.x + (rect.width - modal_w) // 2
        modal_y = rect.y + (rect.height - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

        pygame.draw.rect(surface, BG_DARK, modal_rect, border_radius=8)
        pygame.draw.rect(surface, TEXT_GOLD, modal_rect, width=2, border_radius=8)

        # Header
        f_title = FontManager.get(size=18, bold=True, serif=True)
        f_sub = FontManager.get(size=12, bold=False)
        f_step_h = FontManager.get(size=12, bold=True)
        f_b = FontManager.get(size=11, bold=False)
        f_tiny_bold = FontManager.get(size=10, bold=True)

        t_surf = f_title.render("HOW TO PLAY — THE DETECTIVE'S FIELD MANUAL", True, TEXT_GOLD)
        surface.blit(t_surf, (modal_x + 28, modal_y + 18))

        sub_txt = "Investigate the Blackwood Heist: Examine physical records, follow red strings, build your theory, and indict the culprit."
        surface.blit(f_sub.render(sub_txt, True, TEXT_LIGHT), (modal_x + 28, modal_y + 44))

        # Close button [X]
        self.btn_close.update_pos(modal_x + modal_w - 44, modal_y + 14)
        self.btn_close.render(surface)

        # Content split: Left column (6 Investigation Steps), Right column (Controls Reference)
        col_w_left = int(modal_w * 0.60)
        col_w_right = modal_w - col_w_left - 56

        # Left Column: Investigation Progression Steps
        curr_y = modal_y + 74
        for title, desc in self.steps:
            # Step header badge
            badge_r = pygame.Rect(modal_x + 28, curr_y, col_w_left, 18)
            pygame.draw.rect(surface, BG_PANEL_ALT, badge_r, border_radius=3)
            surface.blit(f_step_h.render(title, True, TEXT_CYAN), (modal_x + 34, curr_y + 1))
            curr_y += 22

            # Description wrapped
            words = desc.split(" ")
            line = ""
            for w in words:
                test_line = line + (" " if line else "") + w
                if f_b.size(test_line)[0] <= col_w_left - 8:
                    line = test_line
                else:
                    if line:
                        surface.blit(f_b.render(line, True, TEXT_LIGHT), (modal_x + 34, curr_y))
                        curr_y += 15
                    line = w
            if line:
                surface.blit(f_b.render(line, True, TEXT_LIGHT), (modal_x + 34, curr_y))
                curr_y += 18
            curr_y += 4

        # Right Column: Controls & Keyboard Reference
        rx = modal_x + col_w_left + 40
        ry = modal_y + 74

        pygame.draw.rect(surface, BG_PANEL, (rx, ry, col_w_right, modal_h - 145), border_radius=6)
        pygame.draw.rect(surface, BG_BORDER, (rx, ry, col_w_right, modal_h - 145), width=1, border_radius=6)

        ctrl_hdr = f_step_h.render("KEYBOARD & MOUSE CONTROLS", True, TEXT_GOLD)
        surface.blit(ctrl_hdr, (rx + 14, ry + 12))
        ry += 32

        for key, act in self.controls:
            k_pill = pygame.Rect(rx + 14, ry, 70, 18)
            pygame.draw.rect(surface, BG_DARKEST, k_pill, border_radius=3)
            pygame.draw.rect(surface, BG_BORDER, k_pill, width=1, border_radius=3)
            surface.blit(f_tiny_bold.render(key, True, TEXT_CYAN), (k_pill.x + 4, k_pill.y + 2))

            surface.blit(f_b.render(act, True, TEXT_LIGHT), (rx + 92, ry + 1))
            ry += 24

        # Bottom Return Button
        self.btn_return.update_pos(modal_x + (modal_w - 240) // 2, modal_y + modal_h - 48)
        self.btn_return.render(surface)
