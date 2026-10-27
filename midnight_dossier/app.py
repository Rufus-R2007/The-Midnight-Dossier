"""
Main Application Controller for The Midnight Dossier.
Manages Pygame window initialization, case header, navigation routing,
responsive layout, and the main game loop.
"""

import sys
import pygame
from typing import Optional
from .theme import (
    BG_DARKEST, BG_DARK, BG_PANEL, BG_PANEL_ALT, BG_BORDER,
    TEXT_WHITE, TEXT_LIGHT, TEXT_MUTED, TEXT_GOLD, TEXT_CYAN,
    COLOR_VERIFIED, COLOR_UNCONFIRMED,
    FontManager
)
from .case_data import CaseData
from .investigation import InvestigationState
from .evidence_board import EvidenceBoardView
from .timeline import CaseTimelineView
from .toolkit import ToolkitView
from .accusation import AccusationView


class MidnightDossierApp:
    """The Midnight Dossier desktop application."""

    def __init__(self, width: int = 1366, height: int = 768) -> None:
        pygame.init()
        pygame.display.set_caption("THE MIDNIGHT DOSSIER — The Blackwood Heist")

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Core State
        self.case_data = CaseData()
        self.investigation_state = InvestigationState(self.case_data)

        # Screens / Views
        self.evidence_board = EvidenceBoardView(self.investigation_state)
        self.timeline_view = CaseTimelineView(self.investigation_state)
        self.toolkit_view = ToolkitView(self.investigation_state)
        self.accusation_view = AccusationView(self.investigation_state)

        # Navigation: 0 = Board, 1 = Timeline, 2 = Toolkit, 3 = Accusation
        self.active_screen_idx = 0

    def run(self) -> None:
        """Main game loop running at target 60 FPS."""
        while self.running:
            dt = self.clock.tick(60) / 1000.0

            # 1. Event Handling
            self._handle_events()

            # 2. Update logic
            self._update(dt)

            # 3. Render screen
            self._render()

            pygame.display.flip()

        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.VIDEORESIZE:
                self.width = max(1024, event.w)
                self.height = max(680, event.h)
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)

            elif event.type == pygame.KEYDOWN:
                # Top-level navigation shortcuts (1, 2, 3, 4)
                if not getattr(self.evidence_board, "search_active", False):
                    if event.key == pygame.K_1:
                        self.active_screen_idx = 0
                    elif event.key == pygame.K_2:
                        self.active_screen_idx = 1
                    elif event.key == pygame.K_3:
                        self.active_screen_idx = 2
                    elif event.key == pygame.K_4:
                        self.active_screen_idx = 3

            # Check navigation bar click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if 8 <= my <= 48 and mx >= self.width - 560:
                    nav_rel_x = mx - (self.width - 560)
                    btn_idx = nav_rel_x // 135
                    if 0 <= btn_idx < 4:
                        self.active_screen_idx = btn_idx
                        continue

            # Route events to active view
            content_rect = self._get_content_rect()
            if self.active_screen_idx == 0:
                board_rect, sidebar_rect = self._get_board_rects()
                self.evidence_board.handle_event(event, board_rect, sidebar_rect)
            elif self.active_screen_idx == 1:
                self.timeline_view.handle_event(event, content_rect)
            elif self.active_screen_idx == 2:
                self.toolkit_view.handle_event(event, content_rect)
            elif self.active_screen_idx == 3:
                self.accusation_view.handle_event(event, content_rect)

    def _update(self, dt: float) -> None:
        if self.active_screen_idx == 0:
            self.evidence_board.update(dt)

    def _render(self) -> None:
        self.screen.fill(BG_DARKEST)

        # 1. Render Top Header
        header_rect = pygame.Rect(0, 0, self.width, 58)
        self._render_case_header(header_rect)

        # 2. Render Active Screen
        content_rect = self._get_content_rect()
        if self.active_screen_idx == 0:
            board_rect, sidebar_rect = self._get_board_rects()
            self.evidence_board.render(self.screen, board_rect, sidebar_rect)
        elif self.active_screen_idx == 1:
            self.timeline_view.render(self.screen, content_rect)
        elif self.active_screen_idx == 2:
            self.toolkit_view.render(self.screen, content_rect)
        elif self.active_screen_idx == 3:
            self.accusation_view.render(self.screen, content_rect)

    def _get_content_rect(self) -> pygame.Rect:
        return pygame.Rect(0, 58, self.width, self.height - 58)

    def _get_board_rects(self) -> Tuple[pygame.Rect, pygame.Rect]:
        sidebar_w = min(360, max(300, int(self.width * 0.27)))
        board_rect = pygame.Rect(0, 58, self.width - sidebar_w, self.height - 58)
        sidebar_rect = pygame.Rect(self.width - sidebar_w, 58, sidebar_w, self.height - 58)
        return board_rect, sidebar_rect

    def _render_case_header(self, rect: pygame.Rect) -> None:
        pygame.draw.rect(self.screen, BG_DARK, rect)
        pygame.draw.line(self.screen, BG_BORDER, (0, rect.bottom - 1), (rect.width, rect.bottom - 1), 1)

        f_title = FontManager.get(size=17, bold=True, serif=True)
        f_sub = FontManager.get(size=11, bold=True)
        f_tiny = FontManager.get(size=11, bold=False)

        # Case Branding
        t_s = f_title.render("THE MIDNIGHT DOSSIER", True, TEXT_GOLD)
        self.screen.blit(t_s, (20, 10))

        sub_s = f_sub.render("CASE 001: THE BLACKWOOD HEIST | ASTERION COMPASS THEFT", True, TEXT_LIGHT)
        self.screen.blit(sub_s, (20, 32))

        # Investigation Progress
        metrics = self.investigation_state.get_progress_metrics()
        px = 440
        py = 18

        prog_txt = f"Progress: {metrics['progress_percent']}%  (Clues: {metrics['examined_evidence_count']}/{metrics['total_evidence_count']})"
        self.screen.blit(f_tiny.render(prog_txt, True, TEXT_CYAN), (px, py))

        # Progress bar
        pbar_rect = pygame.Rect(px, py + 18, 160, 6)
        pygame.draw.rect(self.screen, BG_PANEL_ALT, pbar_rect, border_radius=3)
        fill_w = int(160 * (metrics["progress_percent"] / 100))
        if fill_w > 0:
            pygame.draw.rect(self.screen, COLOR_VERIFIED, (px, py + 18, fill_w, 6), border_radius=3)

        # Compact Navigation Tabs
        nav_buttons = [
            ("Evidence Board", 0),
            ("Case Timeline", 1),
            ("Detective's Toolkit", 2),
            ("Final Accusation", 3),
        ]
        nav_start_x = self.width - 550
        for i, (name, idx) in enumerate(nav_buttons):
            bx = nav_start_x + i * 135
            by = 12
            btn_r = pygame.Rect(bx, by, 128, 34)
            is_active = (self.active_screen_idx == idx)

            bg = BG_PANEL_ALT if is_active else BG_PANEL
            border = TEXT_GOLD if is_active else BG_BORDER
            pygame.draw.rect(self.screen, bg, btn_r, border_radius=4)
            pygame.draw.rect(self.screen, border, btn_r, width=1, border_radius=4)

            txt_col = TEXT_GOLD if is_active else TEXT_LIGHT
            lbl = f_sub.render(name, True, txt_col)
            self.screen.blit(lbl, (bx + (128 - lbl.get_width()) // 2, by + 10))
