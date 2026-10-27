"""
Main Application Controller for The Midnight Dossier.
Manages Pygame window initialization, title screen, navigation routing,
responsive layout, case restart, and the main 60 FPS game loop.
"""

import sys
import pygame
from typing import Optional, Tuple
from .theme import (
    BG_DARKEST, BG_DARK, BG_PANEL, BG_PANEL_ALT, BG_BORDER,
    TEXT_WHITE, TEXT_LIGHT, TEXT_MUTED, TEXT_GOLD, TEXT_CYAN,
    COLOR_VERIFIED, COLOR_UNCONFIRMED,
    FontManager
)
from .case_data import CaseData
from .investigation import InvestigationState
from .title_screen import TitleScreenView
from .evidence_board import EvidenceBoardView
from .timeline import CaseTimelineView
from .toolkit import ToolkitView
from .accusation import AccusationView
from .how_to_play import HowToPlayView
from .ui_components import UIButton


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
        # 0: Title Screen, 1: Board, 2: Timeline, 3: Toolkit, 4: Accusation
        self.title_screen = TitleScreenView(
            on_start_game=lambda: self.switch_screen(1),
            on_open_toolkit=lambda: self.switch_screen(3)
        )
        self.evidence_board = EvidenceBoardView(self.investigation_state)
        self.timeline_view = CaseTimelineView(
            self.investigation_state,
            on_locate_on_board=self.locate_entity_on_board
        )
        self.toolkit_view = ToolkitView(self.investigation_state)
        self.accusation_view = AccusationView(
            self.investigation_state,
            on_restart_case=self.restart_investigation
        )
        self.how_to_play_modal = HowToPlayView(
            on_close=lambda: self.toggle_how_to_play(False)
        )
        self.show_how_to_play = False

        self.active_screen_idx = 0
        self.nav_buttons: list[UIButton] = []
        self._init_nav_buttons()

    def _init_nav_buttons(self) -> None:
        items = [
            ("Main Menu", 0),
            ("Evidence Board", 1),
            ("Case Timeline", 2),
            ("Detective's Toolkit", 3),
            ("Final Accusation", 4),
            ("How to Play", 5),
        ]
        self.nav_buttons = []
        for name, idx in items:
            btn = UIButton(
                pygame.Rect(0, 0, 112, 32),
                name,
                callback=(lambda: self.toggle_how_to_play(True)) if idx == 5 else (lambda i=idx: self.switch_screen(i)),
                font_size=11,
                border_radius=4
            )
            btn.target_screen = idx
            self.nav_buttons.append(btn)

    def toggle_how_to_play(self, show: Optional[bool] = None) -> None:
        if show is None:
            self.show_how_to_play = not self.show_how_to_play
        else:
            self.show_how_to_play = show

    def switch_screen(self, screen_idx: int) -> None:
        if screen_idx == 4:
            # Sync active theory items directly into accusation view
            self.accusation_view.selected_evidence_ids.update(self.investigation_state.theory_evidence_ids)
        self.active_screen_idx = screen_idx

    def locate_entity_on_board(self, entity_id: str) -> None:
        """Switch to evidence board and focus the requested entity."""
        self.active_screen_idx = 1
        self.evidence_board.selected_card_id = entity_id
        self.investigation_state.mark_examined(entity_id)

    def restart_investigation(self) -> None:
        """Completely reset case data, timeline, working theory, and board positions."""
        self.investigation_state.reset()
        self.evidence_board.reset_layout()
        self.evidence_board.selected_card_id = "SUS-01"
        self.evidence_board.query_from_id = "SUS-01"
        self.evidence_board.query_to_id = "LOC-01"
        self.evidence_board.set_filter("ALL")
        self.timeline_view.current_node = self.investigation_state.case.timeline_dll.head
        self.timeline_view.current_index = 0
        self.accusation_view.selected_suspect_id = "SUS-01"
        self.accusation_view.selected_evidence_ids.clear()
        self.accusation_view.verdict_result = None
        self.active_screen_idx = 1

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
        full_rect = pygame.Rect(0, 0, self.width, self.height)
        content_rect = self._get_content_rect()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            elif event.type == pygame.VIDEORESIZE:
                self.width = max(1024, event.w)
                self.height = max(680, event.h)
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)

            # If How to Play modal is active, route all events directly to it
            if self.show_how_to_play:
                self.how_to_play_modal.handle_event(event, full_rect)
                continue

            elif event.type == pygame.KEYDOWN:
                # Top-level navigation shortcuts (0, 1, 2, 3, 4, H)
                if not getattr(self.evidence_board, "search_active", False):
                    if event.key == pygame.K_h:
                        self.toggle_how_to_play()
                        continue
                    elif event.key == pygame.K_0 or (event.key == pygame.K_ESCAPE and self.active_screen_idx != 0):
                        # On screens 1-4, ESC returns to title menu
                        if self.active_screen_idx == 4 and self.accusation_view.verdict_result:
                            pass  # Let accusation view handle closing its verdict modal
                        else:
                            self.active_screen_idx = 0
                    elif event.key == pygame.K_1:
                        self.switch_screen(1)
                    elif event.key == pygame.K_2:
                        self.switch_screen(2)
                    elif event.key == pygame.K_3:
                        self.switch_screen(3)
                    elif event.key == pygame.K_4:
                        self.switch_screen(4)

            # Route top navigation bar clicks on screens 1 - 4
            if self.active_screen_idx != 0:
                if event.type == pygame.MOUSEMOTION:
                    for btn in self.nav_buttons:
                        btn.check_hover(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    handled = False
                    for btn in self.nav_buttons:
                        if btn.handle_event(event):
                            handled = True
                            break
                    if handled:
                        continue

            # Route events to active view
            if self.active_screen_idx == 0:
                self.title_screen.handle_event(event, full_rect)
            elif self.active_screen_idx == 1:
                board_rect, sidebar_rect = self._get_board_rects()
                self.evidence_board.handle_event(event, board_rect, sidebar_rect)
            elif self.active_screen_idx == 2:
                self.timeline_view.handle_event(event, content_rect)
            elif self.active_screen_idx == 3:
                self.toolkit_view.handle_event(event, content_rect)
            elif self.active_screen_idx == 4:
                self.accusation_view.handle_event(event, content_rect)

    def _update(self, dt: float) -> None:
        if self.active_screen_idx == 0:
            self.title_screen.update(dt)
        elif self.active_screen_idx == 1:
            self.evidence_board.update(dt)

    def _render(self) -> None:
        self.screen.fill(BG_DARKEST)

        full_rect = pygame.Rect(0, 0, self.width, self.height)
        content_rect = self._get_content_rect()

        if self.active_screen_idx == 0:
            # Title Screen takes full window
            self.title_screen.render(self.screen, full_rect)
        else:
            # Render Top Header
            header_rect = pygame.Rect(0, 0, self.width, 54)
            self._render_case_header(header_rect)

            # Render Active Screen
            if self.active_screen_idx == 1:
                board_rect, sidebar_rect = self._get_board_rects()
                self.evidence_board.render(self.screen, board_rect, sidebar_rect)
            elif self.active_screen_idx == 2:
                self.timeline_view.render(self.screen, content_rect)
            elif self.active_screen_idx == 3:
                self.toolkit_view.render(self.screen, content_rect)
            elif self.active_screen_idx == 4:
                self.accusation_view.render(self.screen, content_rect)

        # If How to Play modal is active, render on top of current view as overlay
        if self.show_how_to_play:
            self.how_to_play_modal.render(self.screen, full_rect)

    def _get_content_rect(self) -> pygame.Rect:
        return pygame.Rect(0, 54, self.width, self.height - 54)

    def _get_board_rects(self) -> Tuple[pygame.Rect, pygame.Rect]:
        sidebar_w = min(360, max(300, int(self.width * 0.26)))
        board_rect = pygame.Rect(0, 54, self.width - sidebar_w, self.height - 54)
        sidebar_rect = pygame.Rect(self.width - sidebar_w, 54, sidebar_w, self.height - 54)
        return board_rect, sidebar_rect

    def _render_case_header(self, rect: pygame.Rect) -> None:
        pygame.draw.rect(self.screen, BG_DARK, rect)
        pygame.draw.line(self.screen, BG_BORDER, (0, rect.bottom - 1), (rect.width, rect.bottom - 1), 1)

        f_title = FontManager.get(size=16, bold=True, serif=True)
        f_sub = FontManager.get(size=11, bold=True)
        f_tiny = FontManager.get(size=11, bold=False)

        # Case Branding
        t_s = f_title.render("THE MIDNIGHT DOSSIER", True, TEXT_GOLD)
        self.screen.blit(t_s, (20, 9))

        sub_s = f_sub.render("CASE 001: THE BLACKWOOD HEIST", True, TEXT_LIGHT)
        self.screen.blit(sub_s, (20, 30))

        # Investigation Progress & Theory Counts
        metrics = self.investigation_state.get_progress_metrics()
        px = 300
        py = 13

        prog_txt = f"Progress: {metrics['progress_percent']}%  (Clues: {metrics['examined_evidence_count']}/{metrics['total_evidence_count']} | Theory: {metrics['theory_items_count']}/5)"
        self.screen.blit(f_tiny.render(prog_txt, True, TEXT_CYAN), (px, py))

        pbar_rect = pygame.Rect(px, py + 16, 140, 6)
        pygame.draw.rect(self.screen, BG_PANEL_ALT, pbar_rect, border_radius=3)
        fill_w = int(140 * (metrics["progress_percent"] / 100))
        if fill_w > 0:
            pygame.draw.rect(self.screen, COLOR_VERIFIED, (px, py + 16, fill_w, 6), border_radius=3)

        # Compact Navigation Buttons with Unified Hitboxes
        btn_w = 108
        nav_start_x = self.width - (len(self.nav_buttons) * (btn_w + 5) + 14)
        for i, btn in enumerate(self.nav_buttons):
            bx = nav_start_x + i * (btn_w + 5)
            btn.update_pos(bx, 11, btn_w, 32)
            if getattr(btn, "target_screen", -1) == 5:
                btn.is_active = self.show_how_to_play
            else:
                btn.is_active = (getattr(btn, "target_screen", -1) == self.active_screen_idx and not self.show_how_to_play)
            btn.render(self.screen)
