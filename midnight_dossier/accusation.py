"""
Final Accusation Screen for The Midnight Dossier.
Allows the detective to select a prime suspect, choose corroborating evidence,
submit the indictment to the District Attorney, and receive a complete debrief.
Uses strictly synchronized interactive UI buttons with hover and active states.
"""

import pygame
from typing import Optional, List, Dict, Set, Tuple, Callable
from .theme import (
    BG_DARKEST, BG_DARK, BG_PANEL, BG_PANEL_ALT, BG_BORDER,
    TEXT_WHITE, TEXT_LIGHT, TEXT_MUTED, TEXT_GOLD, TEXT_CYAN,
    COLOR_VERIFIED, COLOR_UNCONFIRMED, COLOR_CONTRADICTORY,
    COLOR_SUSPECT, STRING_NORMAL, STRING_ACTIVE,
    FontManager, draw_suspect_silhouette
)
from .investigation import InvestigationState
from .ui_components import UIButton


class AccusationView:
    """Accusation and Case Verdict view."""

    def __init__(self, investigation_state: InvestigationState, on_restart_case: Optional[Callable[[], None]] = None) -> None:
        self.state = investigation_state
        self.on_restart_case = on_restart_case
        self.selected_suspect_id: Optional[str] = "SUS-01"
        self.selected_evidence_ids: Set[str] = set(self.state.theory_evidence_ids)
        self.verdict_result: Optional[dict] = None

        # Interactive controls
        self.suspect_card_rects: List[Tuple[pygame.Rect, str]] = []
        self.evidence_row_rects: List[Tuple[pygame.Rect, str]] = []
        self.btn_import_theory = UIButton(pygame.Rect(0, 0, 190, 26), "Import Working Theory", callback=self._import_theory, font_size=11)
        self.btn_submit = UIButton(
            pygame.Rect(0, 0, 280, 38),
            "SUBMIT FORMAL INDICTMENT",
            callback=self._submit_accusation,
            font_size=12,
            bold=True,
            bg_color=STRING_NORMAL,
            hover_bg=STRING_ACTIVE,
            text_color=TEXT_WHITE
        )
        self.modal_buttons: List[UIButton] = []

    def _import_theory(self) -> None:
        self.selected_evidence_ids.update(self.state.theory_evidence_ids)

    def _submit_accusation(self) -> None:
        if self.selected_suspect_id:
            self.verdict_result = self.state.case.evaluate_accusation(
                self.selected_suspect_id,
                list(self.selected_evidence_ids)
            )

    def handle_event(self, event: pygame.event.Event, rect: pygame.Rect) -> None:
        # Hover handling
        if event.type == pygame.MOUSEMOTION:
            if self.verdict_result:
                for btn in self.modal_buttons:
                    btn.check_hover(event.pos)
                return

            self.btn_import_theory.check_hover(event.pos)
            self.btn_submit.check_hover(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 1. If verdict modal is currently displayed, handle modal buttons
            if self.verdict_result:
                for btn in self.modal_buttons:
                    if btn.handle_event(event):
                        return
                return

            # 2. Suspect Selection Cards
            for card_r, sid in self.suspect_card_rects:
                if card_r.collidepoint(event.pos):
                    self.selected_suspect_id = sid
                    self.state.mark_examined(sid)
                    return

            # 3. Evidence Checkbox Rows
            for row_r, eid in self.evidence_row_rects:
                if row_r.collidepoint(event.pos):
                    if eid in self.selected_evidence_ids:
                        self.selected_evidence_ids.remove(eid)
                    else:
                        self.selected_evidence_ids.add(eid)
                        self.state.mark_examined(eid)
                    return

            # 4. Import & Submit buttons
            if self.btn_import_theory.handle_event(event):
                return
            if self.btn_submit.handle_event(event):
                return

        elif event.type == pygame.KEYDOWN:
            if self.verdict_result and event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                self.verdict_result = None

    def render(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        pygame.draw.rect(surface, BG_DARKEST, rect)

        font_h = FontManager.get(size=18, bold=True, serif=True)
        font_sub = FontManager.get(size=13, bold=True)
        font_bold = FontManager.get(size=12, bold=True)
        font_b = FontManager.get(size=12, bold=False)
        font_tiny = FontManager.get(size=11, bold=False)

        # Header Title
        title_surf = font_h.render("FINAL ACCUSATION & PROSECUTION INDICTMENT", True, TEXT_GOLD)
        surface.blit(title_surf, (rect.x + 30, rect.y + 16))

        sub_desc = "Select the prime suspect and present corroborating physical and digital records to secure a formal warrant."
        surface.blit(font_b.render(sub_desc, True, TEXT_MUTED), (rect.x + 30, rect.y + 42))

        # 1. Suspect Selector Cards
        self.suspect_card_rects = []
        card_w = (rect.width - 80) // 4
        card_h = 150
        for i, s in enumerate(self.state.case.suspects):
            cx = rect.x + 30 + i * (card_w + 8)
            cy = rect.y + 68
            is_selected = (s["id"] == self.selected_suspect_id)

            card_r = pygame.Rect(cx, cy, card_w, card_h)
            self.suspect_card_rects.append((card_r, s["id"]))

            bg = BG_PANEL_ALT if is_selected else BG_PANEL
            border = TEXT_GOLD if is_selected else BG_BORDER
            pygame.draw.rect(surface, bg, card_r, border_radius=6)
            pygame.draw.rect(surface, border, card_r, width=2 if is_selected else 1, border_radius=6)

            # Avatar
            avatar_r = pygame.Rect(cx + (card_w - 46) // 2, cy + 10, 46, 55)
            draw_suspect_silhouette(surface, avatar_r, s.get("avatar_type", "contractor"))

            # Name and Role
            name_s = font_bold.render(s["name"], True, TEXT_WHITE if is_selected else TEXT_LIGHT)
            surface.blit(name_s, (cx + (card_w - name_s.get_width()) // 2, cy + 72))

            role_s = font_tiny.render(s["role"], True, TEXT_GOLD if is_selected else TEXT_MUTED)
            surface.blit(role_s, (cx + (card_w - role_s.get_width()) // 2, cy + 90))

            pill_txt = "[PRIME SUSPECT]" if is_selected else "Click to Accuse"
            pill_col = COLOR_CONTRADICTORY if is_selected else TEXT_MUTED
            pill_s = font_tiny.render(pill_txt, True, pill_col)
            surface.blit(pill_s, (cx + (card_w - pill_s.get_width()) // 2, cy + 122))

        # 2. Corroborating Clues Checklist
        sep_y = rect.y + 232
        pygame.draw.line(surface, BG_BORDER, (rect.x + 30, sep_y), (rect.right - 30, sep_y), 1)

        clues_hdr = font_sub.render(f"ATTACH CORROBORATING EVIDENCE ({len(self.selected_evidence_ids)} Selected)", True, TEXT_GOLD)
        surface.blit(clues_hdr, (rect.x + 30, sep_y + 10))

        # Import Theory Button
        self.btn_import_theory.update_pos(rect.right - 220, sep_y + 8)
        self.btn_import_theory.render(surface)

        # Clues Grid (2 columns)
        self.evidence_row_rects = []
        grid_start_y = sep_y + 38
        col_w = (rect.width - 80) // 2

        for i, ev in enumerate(self.state.case.evidence):
            col = i // 7
            row = i % 7
            ex = rect.x + 30 + col * (col_w + 10)
            ey = grid_start_y + row * 38

            is_checked = (ev["id"] in self.selected_evidence_ids)

            row_rect = pygame.Rect(ex, ey, col_w, 32)
            self.evidence_row_rects.append((row_rect, ev["id"]))

            # Row background on hover/check
            bg_col = BG_PANEL_ALT if is_checked else BG_DARK
            border_col = COLOR_VERIFIED if is_checked else BG_BORDER
            pygame.draw.rect(surface, bg_col, row_rect, border_radius=4)
            pygame.draw.rect(surface, border_col, row_rect, width=1, border_radius=4)

            # Checkbox
            cb_rect = pygame.Rect(ex + 8, ey + 8, 16, 16)
            pygame.draw.rect(surface, COLOR_VERIFIED if is_checked else BG_DARKEST, cb_rect, border_radius=3)
            pygame.draw.rect(surface, TEXT_GOLD if is_checked else BG_BORDER, cb_rect, width=1, border_radius=3)
            if is_checked:
                pygame.draw.line(surface, TEXT_WHITE, (cb_rect.x + 3, cb_rect.y + 8), (cb_rect.x + 7, cb_rect.y + 12), 2)
                pygame.draw.line(surface, TEXT_WHITE, (cb_rect.x + 7, cb_rect.y + 12), (cb_rect.x + 13, cb_rect.y + 4), 2)

            lbl_col = TEXT_WHITE if is_checked else TEXT_LIGHT
            lbl = font_tiny.render(f"[{ev['id']}] {ev['name']}", True, lbl_col)
            surface.blit(lbl, (ex + 32, ey + 8))

        # 3. Submit Indictment Button
        self.btn_submit.update_pos(rect.x + (rect.width - 280) // 2, rect.bottom - 52)
        self.btn_submit.render(surface)

        # 4. Modal Verdict Debrief
        if self.verdict_result:
            self._render_verdict_modal(surface, rect)

    def _render_verdict_modal(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render fullscreen overlay modal with complete forensic verdict debrief."""
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        surface.blit(overlay, rect.topleft)

        modal_w = min(820, rect.width - 80)
        modal_h = min(500, rect.height - 80)
        modal_r = pygame.Rect(rect.x + (rect.width - modal_w) // 2, rect.y + (rect.height - modal_h) // 2, modal_w, modal_h)

        pygame.draw.rect(surface, BG_PANEL, modal_r, border_radius=8)

        v = self.verdict_result
        is_solved = v.get("is_solved", False)
        border_col = COLOR_VERIFIED if is_solved else (COLOR_UNCONFIRMED if v["verdict"] == "INSUFFICIENT_EVIDENCE" else COLOR_CONTRADICTORY)
        pygame.draw.rect(surface, border_col, modal_r, width=2, border_radius=8)

        f_title = FontManager.get(size=18, bold=True, serif=True)
        f_sub = FontManager.get(size=13, bold=True)
        f_b = FontManager.get(size=12, bold=False)

        mx = modal_r.x + 30
        my = modal_r.y + 24

        t_s = f_title.render(v["title"], True, border_col)
        surface.blit(t_s, (mx, my))
        my += 28

        sub_s = f_sub.render(f"Accused: {v.get('suspect_name', 'Unknown')}  |  Corroborating Evidence Attached: {v.get('clue_count', 0)}", True, TEXT_GOLD)
        surface.blit(sub_s, (mx, my))
        my += 30
        pygame.draw.line(surface, BG_BORDER, (mx, my), (modal_r.right - 30, my), 1)
        my += 16

        # Message Body
        my = self._render_wrapped_text(surface, v["message"], mx, my, modal_w - 60, f_b, TEXT_LIGHT)
        my += 26

        # Modal action buttons
        self.modal_buttons = []
        btn_close = UIButton(
            pygame.Rect(modal_r.x + modal_w // 2 - 160, modal_r.bottom - 48, 140, 32),
            "Return to Case",
            callback=lambda: setattr(self, "verdict_result", None),
            font_size=11
        )
        self.modal_buttons.append(btn_close)

        if self.on_restart_case:
            btn_restart = UIButton(
                pygame.Rect(modal_r.x + modal_w // 2 + 10, modal_r.bottom - 48, 150, 32),
                "Restart Investigation",
                callback=self._handle_case_restart,
                font_size=11,
                bg_color=BG_DARK,
                text_color=COLOR_UNCONFIRMED
            )
            self.modal_buttons.append(btn_restart)

        for btn in self.modal_buttons:
            btn.render(surface)

    def _handle_case_restart(self) -> None:
        self.verdict_result = None
        if self.on_restart_case:
            self.on_restart_case()

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
