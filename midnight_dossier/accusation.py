"""
Final Accusation Screen for The Midnight Dossier.
Allows the detective to select a prime suspect, choose corroborating evidence,
submit the indictment to the District Attorney, and receive a complete debrief.
"""

import pygame
from typing import Optional, List, Dict, Set, Tuple
from .theme import (
    BG_DARKEST, BG_DARK, BG_PANEL, BG_PANEL_ALT, BG_BORDER,
    TEXT_WHITE, TEXT_LIGHT, TEXT_MUTED, TEXT_GOLD, TEXT_CYAN,
    COLOR_VERIFIED, COLOR_UNCONFIRMED, COLOR_CONTRADICTORY,
    COLOR_SUSPECT, STRING_NORMAL, STRING_ACTIVE,
    FontManager, draw_suspect_silhouette
)
from .investigation import InvestigationState


class AccusationView:
    """Accusation and Case Verdict view."""

    def __init__(self, investigation_state: InvestigationState) -> None:
        self.state = investigation_state
        self.selected_suspect_id: Optional[str] = "SUS-01"
        self.selected_evidence_ids: Set[str] = set(self.state.theory_evidence_ids)
        self.verdict_result: Optional[dict] = None

    def handle_event(self, event: pygame.event.Event, rect: pygame.Rect) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            rel_x = mx - rect.x
            rel_y = my - rect.y

            # If verdict modal is currently displayed, handle modal close/reset
            if self.verdict_result:
                # Close button or Re-investigate button
                if rect.width // 2 - 100 <= rel_x <= rect.width // 2 + 100 and rect.height - 100 <= rel_y <= rect.height - 60:
                    self.verdict_result = None
                return

            # 1. Suspect Selection Cards (Top half)
            if 80 <= rel_y <= 240:
                card_w = (rect.width - 80) // 4
                for i, s in enumerate(self.state.case.suspects):
                    cx = 30 + i * (card_w + 10)
                    if cx <= rel_x <= cx + card_w:
                        self.selected_suspect_id = s["id"]
                        self.state.mark_examined(s["id"])
                        break

            # 2. Corroborating Evidence Checkboxes (Bottom-left grid)
            if 280 <= rel_y <= 580 and 30 <= rel_x <= rect.width - 260:
                grid_y = rel_y - 300
                row = grid_y // 34
                col = (rel_x - 30) // 280
                ev_idx = row + col * 8
                if 0 <= ev_idx < len(self.state.case.evidence):
                    ev_id = self.state.case.evidence[ev_idx]["id"]
                    if ev_id in self.selected_evidence_ids:
                        self.selected_evidence_ids.remove(ev_id)
                    else:
                        self.selected_evidence_ids.add(ev_id)
                        self.state.mark_examined(ev_id)

            # 3. Quick-Action: "Import Pinned Theory Clues"
            if 265 <= rel_y <= 295 and rect.width - 240 <= rel_x <= rect.width - 30:
                self.selected_evidence_ids.update(self.state.theory_evidence_ids)

            # 4. "Submit Indictment" Button
            if 610 <= rel_y <= 655 and rect.width // 2 - 150 <= rel_x <= rect.width // 2 + 150:
                if self.selected_suspect_id:
                    self.verdict_result = self.state.case.evaluate_accusation(
                        self.selected_suspect_id,
                        list(self.selected_evidence_ids)
                    )

    def render(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        pygame.draw.rect(surface, BG_DARKEST, rect)

        font_h = FontManager.get(size=20, bold=True, serif=True)
        font_sub = FontManager.get(size=14, bold=True)
        font_bold = FontManager.get(size=12, bold=True)
        font_b = FontManager.get(size=12, bold=False)
        font_tiny = FontManager.get(size=11, bold=False)

        # Header Title
        title_surf = font_h.render("FINAL ACCUSATION & PROSECUTION INDICTMENT", True, TEXT_GOLD)
        surface.blit(title_surf, (rect.x + 30, rect.y + 20))

        sub_desc = "Select the prime suspect and present corroborating physical and digital records to secure a formal warrant."
        surface.blit(font_b.render(sub_desc, True, TEXT_MUTED), (rect.x + 30, rect.y + 48))

        # 1. Suspect Selector Cards
        card_w = (rect.width - 80) // 4
        card_h = 160
        for i, s in enumerate(self.state.case.suspects):
            cx = rect.x + 30 + i * (card_w + 10)
            cy = rect.y + 75
            is_selected = (s["id"] == self.selected_suspect_id)

            card_r = pygame.Rect(cx, cy, card_w, card_h)
            bg = BG_PANEL_ALT if is_selected else BG_PANEL
            border = TEXT_GOLD if is_selected else BG_BORDER
            pygame.draw.rect(surface, bg, card_r, border_radius=6)
            pygame.draw.rect(surface, border, card_r, width=2 if is_selected else 1, border_radius=6)

            # Silhouette avatar
            avatar_r = pygame.Rect(cx + (card_w - 50) // 2, cy + 12, 50, 60)
            draw_suspect_silhouette(surface, avatar_r, s.get("avatar_type", "contractor"))

            # Name and Role
            name_s = font_bold.render(s["name"], True, TEXT_WHITE if is_selected else TEXT_LIGHT)
            surface.blit(name_s, (cx + (card_w - name_s.get_width()) // 2, cy + 78))

            role_s = font_tiny.render(s["role"], True, TEXT_GOLD if is_selected else TEXT_MUTED)
            surface.blit(role_s, (cx + (card_w - role_s.get_width()) // 2, cy + 96))

            # Status pill
            pill_txt = "[ACCUSED PRIME SUSPECT]" if is_selected else "Click to Accuse"
            pill_col = COLOR_CONTRADICTORY if is_selected else TEXT_MUTED
            pill_s = font_tiny.render(pill_txt, True, pill_col)
            surface.blit(pill_s, (cx + (card_w - pill_s.get_width()) // 2, cy + 130))

        # 2. Corroborating Clues Checklist
        sep_y = rect.y + 250
        pygame.draw.line(surface, BG_BORDER, (rect.x + 30, sep_y), (rect.right - 30, sep_y), 1)

        clues_hdr = font_sub.render(f"ATTACH CORROBORATING EVIDENCE ({len(self.selected_evidence_ids)} Selected)", True, TEXT_GOLD)
        surface.blit(clues_hdr, (rect.x + 30, sep_y + 14))

        # Import Theory Button
        imp_btn = pygame.Rect(rect.right - 230, sep_y + 10, 200, 26)
        pygame.draw.rect(surface, BG_PANEL_ALT, imp_btn, border_radius=4)
        pygame.draw.rect(surface, BG_BORDER, imp_btn, width=1, border_radius=4)
        imp_s = font_tiny.render("Import Working Theory Clues", True, TEXT_CYAN)
        surface.blit(imp_s, (imp_btn.x + 14, imp_btn.y + 6))

        # Clues Grid (2 columns)
        grid_start_y = sep_y + 45
        for i, ev in enumerate(self.state.case.evidence):
            col = i // 7
            row = i % 7
            ex = rect.x + 30 + col * ((rect.width - 80) // 2)
            ey = grid_start_y + row * 40

            is_checked = (ev["id"] in self.selected_evidence_ids)

            # Checkbox
            cb_rect = pygame.Rect(ex, ey + 2, 16, 16)
            pygame.draw.rect(surface, COLOR_VERIFIED if is_checked else BG_DARK, cb_rect, border_radius=3)
            pygame.draw.rect(surface, TEXT_GOLD if is_checked else BG_BORDER, cb_rect, width=1, border_radius=3)
            if is_checked:
                pygame.draw.line(surface, TEXT_WHITE, (cb_rect.x + 3, cb_rect.y + 8), (cb_rect.x + 7, cb_rect.y + 12), 2)
                pygame.draw.line(surface, TEXT_WHITE, (cb_rect.x + 7, cb_rect.y + 12), (cb_rect.x + 13, cb_rect.y + 4), 2)

            # Clue label
            lbl_col = TEXT_WHITE if is_checked else TEXT_LIGHT
            lbl = font_tiny.render(f"[{ev['id']}] {ev['name']}", True, lbl_col)
            surface.blit(lbl, (ex + 24, ey + 2))

        # 3. Submit Indictment Button
        btn_submit = pygame.Rect(rect.x + (rect.width - 300) // 2, rect.bottom - 65, 300, 42)
        pygame.draw.rect(surface, STRING_NORMAL, btn_submit, border_radius=6)
        pygame.draw.rect(surface, STRING_ACTIVE, btn_submit, width=2, border_radius=6)
        sub_s = font_bold.render("SUBMIT FORMAL INDICTMENT", True, TEXT_WHITE)
        surface.blit(sub_s, (btn_submit.x + (btn_submit.width - sub_s.get_width()) // 2, btn_submit.y + 12))

        # 4. Modal Verdict Debrief (if submitted)
        if self.verdict_result:
            self._render_verdict_modal(surface, rect)

    def _render_verdict_modal(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render fullscreen overlay modal with complete forensic verdict debrief."""
        # Dimming overlay
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, rect.topleft)

        modal_w = min(820, rect.width - 100)
        modal_h = min(520, rect.height - 80)
        modal_r = pygame.Rect(rect.x + (rect.width - modal_w) // 2, rect.y + (rect.height - modal_h) // 2, modal_w, modal_h)

        pygame.draw.rect(surface, BG_PANEL, modal_r, border_radius=8)

        v = self.verdict_result
        is_solved = v.get("is_solved", False)
        border_col = COLOR_VERIFIED if is_solved else (COLOR_UNCONFIRMED if v["verdict"] == "INSUFFICIENT_EVIDENCE" else COLOR_CONTRADICTORY)
        pygame.draw.rect(surface, border_col, modal_r, width=2, border_radius=8)

        f_title = FontManager.get(size=18, bold=True, serif=True)
        f_sub = FontManager.get(size=14, bold=True)
        f_b = FontManager.get(size=13, bold=False)
        f_bold = FontManager.get(size=13, bold=True)

        mx = modal_r.x + 30
        my = modal_r.y + 25

        # Title
        t_s = f_title.render(v["title"], True, border_col)
        surface.blit(t_s, (mx, my))
        my += 30

        # Subtitle
        sub_s = f_sub.render(f"Accused: {v.get('suspect_name', 'Unknown')}  |  Corroborating Clues Attached: {v.get('clue_count', 0)}", True, TEXT_GOLD)
        surface.blit(sub_s, (mx, my))
        my += 35
        pygame.draw.line(surface, BG_BORDER, (mx, my), (modal_r.right - 30, my), 1)
        my += 18

        # Message Body (wrapped)
        my = self._render_wrapped_text(surface, v["message"], mx, my, modal_w - 60, f_b, TEXT_LIGHT)
        my += 30

        # Close / Re-investigate Button
        btn_close = pygame.Rect(modal_r.x + (modal_w - 220) // 2, modal_r.bottom - 55, 220, 36)
        pygame.draw.rect(surface, BG_PANEL_ALT, btn_close, border_radius=5)
        pygame.draw.rect(surface, border_col, btn_close, width=1, border_radius=5)
        c_lbl = f_bold.render("Return to Case Board", True, TEXT_WHITE)
        surface.blit(c_lbl, (btn_close.x + (btn_close.width - c_lbl.get_width()) // 2, btn_close.y + 10))

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
        line_height = font.get_linesize() + 4

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
