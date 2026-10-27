"""
Cinematic Title Screen and Case Briefing for The Midnight Dossier.
Features atmospheric noir title sequence, animated procedural thread weaving,
suspect silhouette previews, case dossier briefings, and controls guide.
"""

import pygame
import math
import sys
from typing import Optional, Callable, List, Tuple
from .theme import (
    BG_DARKEST, BG_DARK, BG_PANEL, BG_PANEL_ALT, BG_BORDER,
    TEXT_WHITE, TEXT_LIGHT, TEXT_MUTED, TEXT_GOLD, TEXT_CYAN,
    COLOR_VERIFIED, COLOR_UNCONFIRMED, COLOR_CONTRADICTORY,
    STRING_NORMAL, STRING_ACTIVE, STRING_GLOW,
    FontManager, create_corkboard_surface, draw_suspect_silhouette, draw_pin
)
from .ui_components import UIButton


class TitleScreenView:
    """Atmospheric Opening Screen and Main Menu."""

    def __init__(self, on_start_game: Callable[[], None], on_open_toolkit: Callable[[], None]) -> None:
        self.on_start_game = on_start_game
        self.on_open_toolkit = on_open_toolkit
        self.cork_surf: Optional[pygame.Surface] = None
        self.cork_size: Tuple[int, int] = (0, 0)
        self.anim_time = 0.0

        # Modal state: None, "BRIEFING", "CONTROLS"
        self.active_modal: Optional[str] = None

        # Menu buttons
        self.buttons: List[UIButton] = []
        self._init_buttons()

    def _init_buttons(self) -> None:
        self.btn_play = UIButton(
            pygame.Rect(0, 0, 240, 42),
            "INVESTIGATE CASE",
            callback=self.on_start_game,
            font_size=13,
            bold=True,
            bg_color=(140, 40, 45),
            hover_bg=(190, 50, 60),
            border_color=(235, 65, 75),
            text_color=TEXT_WHITE,
            hover_text_color=TEXT_WHITE,
            border_radius=5
        )
        self.btn_briefing = UIButton(
            pygame.Rect(0, 0, 240, 36),
            "CASE BRIEFING & DOSSIER",
            callback=lambda: self._set_modal("BRIEFING"),
            font_size=12,
            bold=True,
            border_radius=5
        )
        self.btn_toolkit = UIButton(
            pygame.Rect(0, 0, 240, 36),
            "DETECTIVE'S TOOLKIT (DSA)",
            callback=self.on_open_toolkit,
            font_size=12,
            bold=True,
            border_radius=5
        )
        self.btn_controls = UIButton(
            pygame.Rect(0, 0, 240, 36),
            "CONTROLS & SHORTCUTS",
            callback=lambda: self._set_modal("CONTROLS"),
            font_size=12,
            bold=True,
            border_radius=5
        )
        self.btn_quit = UIButton(
            pygame.Rect(0, 0, 240, 34),
            "QUIT APPLICATION",
            callback=lambda: sys.exit(0),
            font_size=11,
            bold=False,
            bg_color=BG_DARK,
            hover_bg=BG_PANEL,
            border_color=BG_BORDER,
            text_color=TEXT_MUTED,
            hover_text_color=COLOR_CONTRADICTORY,
            border_radius=5
        )
        self.buttons = [
            self.btn_play,
            self.btn_briefing,
            self.btn_toolkit,
            self.btn_controls,
            self.btn_quit,
        ]

    def _set_modal(self, modal_name: Optional[str]) -> None:
        self.active_modal = modal_name

    def update(self, dt: float) -> None:
        self.anim_time += dt

    def handle_event(self, event: pygame.event.Event, rect: pygame.Rect) -> None:
        # If modal is open, check modal close button or ESC key
        if self.active_modal:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                self.active_modal = None
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Modal close button
                modal_w = min(880, rect.width - 80)
                modal_h = min(560, rect.height - 80)
                modal_x = rect.x + (rect.width - modal_w) // 2
                modal_y = rect.y + (rect.height - modal_h) // 2
                close_r = pygame.Rect(modal_x + modal_w - 45, modal_y + 12, 32, 28)
                return_btn = pygame.Rect(modal_x + (modal_w - 180) // 2, modal_y + modal_h - 48, 180, 32)
                if close_r.collidepoint(mx, my) or return_btn.collidepoint(mx, my):
                    self.active_modal = None
                    return
                # Clicking outside modal
                modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
                if not modal_rect.collidepoint(mx, my):
                    self.active_modal = None
                    return
            return

        # Main menu button events
        for btn in self.buttons:
            btn.handle_event(event)

    def render(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        # Background corkboard surface
        if self.cork_surf is None or self.cork_size != (rect.width, rect.height):
            self.cork_surf = create_corkboard_surface(rect.width, rect.height)
            self.cork_size = (rect.width, rect.height)

        surface.blit(self.cork_surf, rect.topleft)

        # Draw atmospheric animated investigative threads weaving across title board
        self._render_animated_threads(surface, rect)

        # Draw suspect silhouette preview cards in background
        self._render_preview_cards(surface, rect)

        # Title Card Panel
        f_title = FontManager.get(size=32, bold=True, serif=True)
        f_tagline = FontManager.get(size=14, bold=False, serif=True)
        f_meta = FontManager.get(size=11, bold=True)

        center_x = rect.x + rect.width // 2
        card_w = min(480, rect.width - 60)
        card_h = 440
        card_y = rect.y + max(40, (rect.height - card_h) // 2 - 20)

        # Main Title Board Box
        title_box = pygame.Rect(center_x - card_w // 2, card_y, card_w, card_h)
        pygame.draw.rect(surface, (0, 0, 0, 150), (title_box.x + 6, title_box.y + 8, card_w, card_h), border_radius=8)
        pygame.draw.rect(surface, BG_PANEL, title_box, border_radius=8)
        pygame.draw.rect(surface, BG_BORDER, title_box, width=1, border_radius=8)
        pygame.draw.rect(surface, TEXT_GOLD, (title_box.x + 12, title_box.y + 12, card_w - 24, card_h - 24), width=1, border_radius=6)

        # Pins on title card corners
        draw_pin(surface, title_box.x + 18, title_box.y + 18, radius=5)
        draw_pin(surface, title_box.right - 18, title_box.y + 18, radius=5)

        # Top confidential label
        top_lbl = f_meta.render("BLACKWOOD MUSEUM POLICE DOSSIER — CONFIDENTIAL", True, COLOR_CONTRADICTORY)
        surface.blit(top_lbl, (center_x - top_lbl.get_width() // 2, card_y + 26))

        # Big Title
        t_surf = f_title.render("THE MIDNIGHT DOSSIER", True, TEXT_GOLD)
        surface.blit(t_surf, (center_x - t_surf.get_width() // 2, card_y + 48))

        # Tagline
        tag_surf = f_tagline.render('"Every clue leaves a thread."', True, TEXT_LIGHT)
        surface.blit(tag_surf, (center_x - tag_surf.get_width() // 2, card_y + 86))

        sub_desc = f_meta.render("CASE 001: THE BLACKWOOD HEIST | DSA INVESTIGATION ENGINE", True, TEXT_CYAN)
        surface.blit(sub_desc, (center_x - sub_desc.get_width() // 2, card_y + 112))

        pygame.draw.line(surface, BG_BORDER, (title_box.x + 30, card_y + 132), (title_box.right - 30, card_y + 132), 1)

        # Buttons positioning inside title card
        btn_start_y = card_y + 150
        btn_gap = 48
        for i, btn in enumerate(self.buttons):
            by = btn_start_y + i * btn_gap
            btn.update_pos(center_x - btn.rect.width // 2, by)
            btn.render(surface)

        # Footer credit
        f_foot = FontManager.get(size=10, bold=False)
        foot = f_foot.render("Powered by Custom Pure-Python ADTs (CO1 - CO5) | Built for CSE Evaluation", True, TEXT_MUTED)
        surface.blit(foot, (center_x - foot.get_width() // 2, card_y + card_h - 22))

        # Modals (Briefing / Controls)
        if self.active_modal == "BRIEFING":
            self._render_briefing_modal(surface, rect)
        elif self.active_modal == "CONTROLS":
            self._render_controls_modal(surface, rect)

    def _render_animated_threads(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Animate glowing red threads moving across background pins."""
        pts = [
            (rect.x + 100, rect.y + 140),
            (rect.x + rect.width - 120, rect.y + 180),
            (rect.x + rect.width - 160, rect.y + rect.height - 140),
            (rect.x + 140, rect.y + rect.height - 180),
            (rect.x + rect.width // 2, rect.y + 80),
        ]
        # Draw background pins
        for pt in pts:
            draw_pin(surface, pt[0], pt[1], radius=6)

        # Catenary glowing thread
        phase = self.anim_time * 2.0
        glow_alpha = int(120 + 60 * math.sin(phase))
        thread_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for i in range(len(pts) - 1):
            p1 = pts[i]
            p2 = pts[i + 1]
            pygame.draw.line(thread_surf, (*STRING_GLOW, glow_alpha), p1, p2, 4)
            pygame.draw.line(thread_surf, STRING_ACTIVE, p1, p2, 2)
        surface.blit(thread_surf, rect.topleft)

    def _render_preview_cards(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw 4 suspect silhouette preview cards in the background corners."""
        suspects_preview = [
            ("Oliver Reed", "Contractor", "contractor", rect.x + 40, rect.y + 60),
            ("Evelyn Shaw", "Archivist", "archivist", rect.right - 180, rect.y + 60),
            ("Marcus Vale", "Security Guard", "guard", rect.x + 40, rect.bottom - 170),
            ("Dr. Lena Hart", "Curator", "curator", rect.right - 180, rect.bottom - 170),
        ]
        f_name = FontManager.get(size=11, bold=True)
        f_role = FontManager.get(size=10, bold=False)

        for name, role, av_type, cx, cy in suspects_preview:
            c_rect = pygame.Rect(cx, cy, 140, 110)
            pygame.draw.rect(surface, (0, 0, 0, 90), (c_rect.x + 3, c_rect.y + 4, 140, 110), border_radius=4)
            pygame.draw.rect(surface, (238, 230, 212), c_rect, border_radius=4)
            pygame.draw.rect(surface, (120, 105, 88), c_rect, width=1, border_radius=4)

            # Avatar silhouette
            av_rect = pygame.Rect(cx + 45, cy + 10, 50, 55)
            draw_suspect_silhouette(surface, av_rect, av_type)

            ns = f_name.render(name, True, (24, 20, 16))
            surface.blit(ns, (cx + (140 - ns.get_width()) // 2, cy + 70))
            rs = f_role.render(role, True, (85, 75, 65))
            surface.blit(rs, (cx + (140 - rs.get_width()) // 2, cy + 86))

            draw_pin(surface, cx + 70, cy + 6, radius=4)

    def _render_briefing_modal(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render case briefing & incident report dossier modal."""
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        surface.blit(overlay, rect.topleft)

        modal_w = min(880, rect.width - 80)
        modal_h = min(560, rect.height - 80)
        modal_x = rect.x + (rect.width - modal_w) // 2
        modal_y = rect.y + (rect.height - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

        pygame.draw.rect(surface, BG_PANEL, modal_rect, border_radius=8)
        pygame.draw.rect(surface, TEXT_GOLD, modal_rect, width=2, border_radius=8)

        f_title = FontManager.get(size=18, bold=True, serif=True)
        f_sub = FontManager.get(size=13, bold=True)
        f_b = FontManager.get(size=12, bold=False)
        f_tiny = FontManager.get(size=11, bold=False)

        mx = modal_x + 30
        my = modal_y + 24

        surface.blit(f_title.render("INCIDENT REPORT: THE BLACKWOOD HEIST", True, TEXT_GOLD), (mx, my))
        # Close button [X]
        close_r = pygame.Rect(modal_x + modal_w - 45, modal_y + 14, 30, 26)
        pygame.draw.rect(surface, BG_PANEL_ALT, close_r, border_radius=3)
        pygame.draw.rect(surface, BG_BORDER, close_r, width=1, border_radius=3)
        surface.blit(f_sub.render("X", True, TEXT_LIGHT), (close_r.x + 9, close_r.y + 4))

        my += 30
        sub = "Time of Crime: 21:47 - 21:56 | Missing Relic: The Asterion Compass (EV-01)"
        surface.blit(f_sub.render(sub, True, TEXT_CYAN), (mx, my))
        my += 26
        pygame.draw.line(surface, BG_BORDER, (mx, my), (modal_x + modal_w - 30, my), 1)
        my += 14

        paragraphs = [
            "1. THE INCIDENT: At approximately 21:47, an abrupt circuit breaker trip blinded CCTV cameras covering Antiquities Gallery B and the adjacent Service Corridor for nine minutes. When power was restored at 21:56, the alarmed display pedestal had been breached and the 14th-century Asterion Compass was missing.",
            "2. THE CRIME SCENE: The vitrine alarm wiring was severed with precision micro-snips. Physical master keys remained untouched in the security vault safe. A contractor van departed through the loading dock gate shortly afterward.",
            "3. INVESTIGATIVE OBJECTIVE: Inspect cards on the Evidence Board, trace connections using the Graph BFS engine, cross-reference the chronological event timeline, and identify which suspect's alibi is shattered by corroborating digital and physical logs.",
            "4. RULES OF EVIDENCE: A formal warrant requires selecting the true culprit AND submitting corroborating evidence linking access credentials, tool analysis, and loading bay vehicle departures. Centrality alone does not prove guilt.",
        ]
        for p in paragraphs:
            my = self._render_wrapped_text(surface, p, mx, my, modal_w - 60, f_b, TEXT_LIGHT) + 8

        # Return button
        btn_r = pygame.Rect(modal_x + (modal_w - 180) // 2, modal_y + modal_h - 48, 180, 32)
        pygame.draw.rect(surface, BG_PANEL_ALT, btn_r, border_radius=4)
        pygame.draw.rect(surface, TEXT_GOLD, btn_r, width=1, border_radius=4)
        surface.blit(f_sub.render("Return to Menu", True, TEXT_WHITE), (btn_r.x + 36, btn_r.y + 7))

    def _render_controls_modal(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render controls, keyboard shortcuts, and viva guide modal."""
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        surface.blit(overlay, rect.topleft)

        modal_w = min(880, rect.width - 80)
        modal_h = min(540, rect.height - 80)
        modal_x = rect.x + (rect.width - modal_w) // 2
        modal_y = rect.y + (rect.height - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

        pygame.draw.rect(surface, BG_PANEL, modal_rect, border_radius=8)
        pygame.draw.rect(surface, TEXT_GOLD, modal_rect, width=2, border_radius=8)

        f_title = FontManager.get(size=18, bold=True, serif=True)
        f_sub = FontManager.get(size=13, bold=True)
        f_b = FontManager.get(size=12, bold=False)

        mx = modal_x + 30
        my = modal_y + 24

        surface.blit(f_title.render("INVESTIGATION CONTROLS & VIVA GUIDE", True, TEXT_GOLD), (mx, my))
        close_r = pygame.Rect(modal_x + modal_w - 45, modal_y + 14, 30, 26)
        pygame.draw.rect(surface, BG_PANEL_ALT, close_r, border_radius=3)
        pygame.draw.rect(surface, BG_BORDER, close_r, width=1, border_radius=3)
        surface.blit(f_sub.render("X", True, TEXT_LIGHT), (close_r.x + 9, close_r.y + 4))

        my += 36
        pygame.draw.line(surface, BG_BORDER, (mx, my), (modal_x + modal_w - 30, my), 1)
        my += 16

        shortcuts = [
            ("Left Click", "Select evidence card / click interactive button"),
            ("Click & Drag", "Reposition evidence card anywhere on the corkboard"),
            ("Filter Tabs", "Filter board cards by All, Suspects, Evidence, or Locations"),
            ("Reset Layout", "Restores all cards to clean, readable initial layout"),
            ("Key 1", "Switch to Main Evidence Board"),
            ("Key 2", "Switch to Chronological Timeline (Doubly Linked List)"),
            ("Key 3", "Switch to Detective's Toolkit (All 5 Course Outcomes)"),
            ("Key 4", "Switch to Final Accusation & Verdict Submission"),
            ("Ctrl + Z / Ctrl + Y", "Undo / Redo board actions and working theory modifications"),
            ("Query Search Bar", "Type suspect/evidence prefix to test real-time Trie autocomplete"),
        ]
        for key_name, desc in shortcuts:
            k_s = f_sub.render(f"{key_name:<20}", True, TEXT_CYAN)
            d_s = f_b.render(desc, True, TEXT_LIGHT)
            surface.blit(k_s, (mx, my))
            surface.blit(d_s, (mx + 180, my))
            my += 24

        btn_r = pygame.Rect(modal_x + (modal_w - 180) // 2, modal_y + modal_h - 48, 180, 32)
        pygame.draw.rect(surface, BG_PANEL_ALT, btn_r, border_radius=4)
        pygame.draw.rect(surface, TEXT_GOLD, btn_r, width=1, border_radius=4)
        surface.blit(f_sub.render("Return to Menu", True, TEXT_WHITE), (btn_r.x + 36, btn_r.y + 7))

    def _render_wrapped_text(
        self,
        surface: pygame.Surface,
        text: str,
        x: int,
        y: int,
        max_w: int,
        font: pygame.font.Font,
        color: Tuple[int, int, int]
    ) -> int:
        lines = text.split("\n")
        curr_y = y
        line_height = font.get_linesize() + 3
        for block in lines:
            words = block.split(" ")
            curr_line = ""
            for word in words:
                test_line = curr_line + (" " if curr_line else "") + word
                if font.size(test_line)[0] <= max_w:
                    curr_line = test_line
                else:
                    if curr_line:
                        surf = font.render(curr_line, True, color)
                        surface.blit(surf, (x, curr_y))
                        curr_y += line_height
                    curr_line = word
            if curr_line:
                surf = font.render(curr_line, True, color)
                surface.blit(surf, (x, curr_y))
                curr_y += line_height
        return curr_y
