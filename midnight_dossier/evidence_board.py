"""
Main Evidence Board View for The Midnight Dossier.
Features draggable physical-style cards, pins, red connecting strings,
interactive sidebar inspection, filter buttons, undo/redo, and relationship tracing.
"""

import pygame
import math
from typing import Dict, List, Optional, Tuple, Any
from .theme import (
    BG_DARKEST, BG_DARK, BG_PANEL, BG_PANEL_ALT, BG_BORDER,
    CORK_FRAME, PARCHMENT_CARD, PARCHMENT_LIGHT, PARCHMENT_DARK,
    CARD_BORDER, CARD_HOVER_BORDER, CARD_TEXT_MAIN, CARD_TEXT_MUTED,
    PIN_BRASS, STRING_NORMAL, STRING_ACTIVE,
    COLOR_VERIFIED, COLOR_TESTIMONY, COLOR_UNCONFIRMED, COLOR_CONTRADICTORY,
    COLOR_SUSPECT, COLOR_LOCATION, COLOR_ARTIFACT,
    TEXT_WHITE, TEXT_LIGHT, TEXT_MUTED, TEXT_GOLD, TEXT_CYAN,
    FontManager, create_corkboard_surface, draw_pin, draw_curved_string, draw_suspect_silhouette
)
from .investigation import InvestigationState


class BoardCard:
    """Represents a physical card pinned to the evidence corkboard."""

    def __init__(
        self,
        entity_id: str,
        name: str,
        category: str,
        x: int,
        y: int,
        width: int = 150,
        height: int = 100,
        metadata: Optional[dict] = None
    ) -> None:
        self.entity_id = entity_id
        self.name = name
        self.category = category  # suspect, clue, location
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.metadata = metadata or {}
        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.initial_pos = (x, y)

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def pin_pos(self) -> Tuple[int, int]:
        """Position of the brass push-pin at top center of the card."""
        return (self.x + self.width // 2, self.y + 8)

    @property
    def center_pos(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)


class EvidenceBoardView:
    """Interactive evidence board interface."""

    def __init__(self, investigation_state: InvestigationState) -> None:
        self.state = investigation_state
        self.cards: Dict[str, BoardCard] = {}
        self.corkboard_surf: Optional[pygame.Surface] = None
        self.corkboard_size = (0, 0)
        self.filter_mode = "ALL"  # ALL, SUSPECTS, EVIDENCE, LOCATIONS
        self.selected_card_id: Optional[str] = "SUS-01"
        self.dragged_card_id: Optional[str] = None
        self.pulse_phase = 0.0

        # Query panel controls
        self.query_from_id: str = "SUS-01"
        self.query_to_id: str = "LOC-01"
        self.query_use_bfs: bool = True
        self.search_text: str = ""
        self.search_active: bool = False
        self.autocomplete_results: List[Tuple[str, Any]] = []

        self._init_card_layout()

    def _init_card_layout(self) -> None:
        """Create initial organized layout of cards on the board."""
        # 1. Suspects (Top row)
        suspect_positions = [
            ("SUS-01", 60, 45),
            ("SUS-02", 240, 45),
            ("SUS-03", 420, 45),
            ("SUS-04", 600, 45),
        ]
        for sid, sx, sy in suspect_positions:
            s_data = self.state.case.get_entity_by_id(sid)
            if s_data:
                self.cards[sid] = BoardCard(
                    sid, s_data["name"], "suspect", sx, sy, width=155, height=110, metadata=s_data
                )

        # 2. Key Evidence (Middle rows)
        evidence_positions = [
            ("EV-01", 240, 190),  # Stolen Compass (Center)
            ("EV-02", 60, 190),   # Maintenance Request
            ("EV-03", 420, 190),  # CCTV Glitch
            ("EV-04", 60, 335),   # Keycard Scan
            ("EV-05", 240, 335),  # Missing Case
            ("EV-06", 420, 335),  # Van Departure
            ("EV-07", 600, 190),  # Wire Snips
            ("EV-08", 600, 335),  # Sync Script
            ("EV-09", 60, 480),   # Tea Room Statement
            ("EV-10", 240, 480),  # Radio Audio
            ("EV-11", 420, 480),  # Guard Permit
            ("EV-12", 600, 480),  # Dinner Toll
        ]
        for eid, ex, ey in evidence_positions:
            e_data = self.state.case.get_entity_by_id(eid)
            if e_data:
                self.cards[eid] = BoardCard(
                    eid, e_data["name"], "clue", ex, ey, width=155, height=95, metadata=e_data
                )

        # 3. Locations (Bottom row / flanks)
        location_positions = [
            ("LOC-01", 60, 620),
            ("LOC-02", 215, 620),
            ("LOC-03", 370, 620),
            ("LOC-04", 525, 620),
            ("LOC-05", 680, 620),
        ]
        for lid, lx, ly in location_positions:
            loc_data = self.state.case.get_entity_by_id(lid)
            if loc_data:
                self.cards[lid] = BoardCard(
                    lid, loc_data["name"], "location", lx, ly, width=140, height=85, metadata=loc_data
                )

    def reset_layout(self) -> None:
        """Reset all cards to default non-overlapping positions."""
        for card in self.cards.values():
            card.x, card.y = card.initial_pos

    def update(self, dt: float) -> None:
        self.pulse_phase += dt

    def handle_event(self, event: pygame.event.Event, board_rect: pygame.Rect, sidebar_rect: pygame.Rect) -> None:
        """Handle mouse clicks, drags, typing, and keyboard shortcuts."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Check if clicked inside board area
            if board_rect.collidepoint(mx, my):
                rel_x = mx - board_rect.x
                rel_y = my - board_rect.y

                # Check cards in reverse (top-most card first)
                clicked_card = None
                for card in reversed(list(self.cards.values())):
                    if not self._is_card_visible(card):
                        continue
                    if card.rect.collidepoint(rel_x, rel_y):
                        clicked_card = card
                        break

                if clicked_card:
                    self.selected_card_id = clicked_card.entity_id
                    self.state.mark_examined(clicked_card.entity_id)
                    self.dragged_card_id = clicked_card.entity_id
                    clicked_card.is_dragging = True
                    clicked_card.drag_offset_x = rel_x - clicked_card.x
                    clicked_card.drag_offset_y = rel_y - clicked_card.y
                else:
                    self.search_active = False

            # Check sidebar / query panel clicks
            elif sidebar_rect.collidepoint(mx, my):
                self._handle_sidebar_click(mx - sidebar_rect.x, my - sidebar_rect.y, sidebar_rect)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragged_card_id and self.dragged_card_id in self.cards:
                card = self.cards[self.dragged_card_id]
                card.is_dragging = False
                # Record undo action for repositioning
                self.state.undo_redo.record_action({
                    "type": "move_card",
                    "entity_id": card.entity_id,
                    "pos": (card.x, card.y),
                })
            self.dragged_card_id = None

        elif event.type == pygame.MOUSEMOTION:
            if self.dragged_card_id and self.dragged_card_id in self.cards:
                mx, my = event.pos
                rel_x = mx - board_rect.x
                rel_y = my - board_rect.y
                card = self.cards[self.dragged_card_id]
                new_x = rel_x - card.drag_offset_x
                new_y = rel_y - card.drag_offset_y

                # Clamp within board
                card.x = max(10, min(board_rect.width - card.width - 10, new_x))
                card.y = max(10, min(board_rect.height - card.height - 10, new_y))

        elif event.type == pygame.KEYDOWN:
            # Undo / Redo shortcuts
            if event.mod & pygame.KMOD_CTRL:
                if event.key == pygame.K_z:
                    self._perform_undo()
                elif event.key == pygame.K_y:
                    self._perform_redo()

            # Autocomplete typing
            if self.search_active:
                if event.key == pygame.K_BACKSPACE:
                    self.search_text = self.search_text[:-1]
                    self._update_autocomplete()
                elif event.key == pygame.K_RETURN:
                    if self.autocomplete_results:
                        name, meta = self.autocomplete_results[0]
                        self.selected_card_id = meta["id"]
                        self.state.mark_examined(meta["id"])
                    self.search_active = False
                elif event.key == pygame.K_ESCAPE:
                    self.search_active = False
                elif event.unicode and len(event.unicode) == 1:
                    self.search_text += event.unicode
                    self._update_autocomplete()

    def _update_autocomplete(self) -> None:
        if self.search_text.strip():
            self.autocomplete_results = self.state.autocomplete(self.search_text.strip())
        else:
            self.autocomplete_results = []

    def _perform_undo(self) -> None:
        action = self.state.undo_redo.undo()
        if action:
            if action["type"] == "add_theory":
                if action["evidence_id"] in self.state.theory_evidence_ids:
                    self.state.theory_evidence_ids.remove(action["evidence_id"])
            elif action["type"] == "remove_theory":
                self.state.theory_evidence_ids.append(action["evidence_id"])

    def _perform_redo(self) -> None:
        action = self.state.undo_redo.redo()
        if action:
            if action["type"] == "add_theory":
                if action["evidence_id"] not in self.state.theory_evidence_ids:
                    self.state.theory_evidence_ids.append(action["evidence_id"])
            elif action["type"] == "remove_theory":
                if action["evidence_id"] in self.state.theory_evidence_ids:
                    self.state.theory_evidence_ids.remove(action["evidence_id"])

    def _is_card_visible(self, card: BoardCard) -> bool:
        if self.filter_mode == "ALL":
            return True
        elif self.filter_mode == "SUSPECTS":
            return card.category == "suspect"
        elif self.filter_mode == "EVIDENCE":
            return card.category == "clue"
        elif self.filter_mode == "LOCATIONS":
            return card.category == "location"
        return True

    def _handle_sidebar_click(self, lx: int, ly: int, rect: pygame.Rect) -> None:
        """Handle clicks on buttons within the right inspection & query panel."""
        # 1. "Add/Remove Theory" button
        if 20 <= lx <= rect.width - 20 and 315 <= ly <= 350:
            if self.selected_card_id and self.selected_card_id.startswith("EV-"):
                self.state.toggle_theory_evidence(self.selected_card_id)

        # 2. "Set as Source" button
        elif 20 <= lx <= rect.width // 2 - 10 and 560 <= ly <= 590:
            if self.selected_card_id:
                self.query_from_id = self.selected_card_id

        # 3. "Set as Target" button
        elif rect.width // 2 + 10 <= lx <= rect.width - 20 and 560 <= ly <= 590:
            if self.selected_card_id:
                self.query_to_id = self.selected_card_id

        # 4. "Toggle Algorithm: BFS vs DFS"
        elif 20 <= lx <= rect.width - 20 and 600 <= ly <= 630:
            self.query_use_bfs = not self.query_use_bfs

        # 5. "Trace Connection (BFS/DFS)"
        elif 20 <= lx <= rect.width - 20 and 640 <= ly <= 675:
            if self.query_from_id and self.query_to_id:
                self.state.query_relationship(self.query_from_id, self.query_to_id, use_bfs=self.query_use_bfs)

        # 6. "Clear Trace"
        elif 20 <= lx <= rect.width - 20 and 685 <= ly <= 710:
            self.state.clear_active_path()

        # 7. Search box activation
        elif 20 <= lx <= rect.width - 20 and 445 <= ly <= 475:
            self.search_active = True

        # 8. Autocomplete item click
        elif self.search_active and self.autocomplete_results and 480 <= ly <= 480 + len(self.autocomplete_results) * 26:
            item_idx = (ly - 480) // 26
            if 0 <= item_idx < len(self.autocomplete_results):
                name, meta = self.autocomplete_results[item_idx]
                self.selected_card_id = meta["id"]
                self.state.mark_examined(meta["id"])
                self.search_active = False

    def render(self, surface: pygame.Surface, board_rect: pygame.Rect, sidebar_rect: pygame.Rect) -> None:
        """Render board, corkboard texture, connecting strings, cards, and sidebar."""
        # 1. Corkboard background surface
        if self.corkboard_surf is None or self.corkboard_size != (board_rect.width, board_rect.height):
            self.corkboard_surf = create_corkboard_surface(board_rect.width, board_rect.height)
            self.corkboard_size = (board_rect.width, board_rect.height)

        board_surface = pygame.Surface((board_rect.width, board_rect.height))
        board_surface.blit(self.corkboard_surf, (0, 0))

        # 2. Render strings (BEHIND cards)
        self._render_strings(board_surface)

        # 3. Render cards
        for card in self.cards.values():
            if self._is_card_visible(card):
                self._render_card(board_surface, card)

        # 4. Render filter buttons and controls on board
        self._render_board_controls(board_surface)

        # Blit board to screen
        surface.blit(board_surface, board_rect.topleft)

        # 5. Render Sidebar / Investigation Inspector
        self._render_sidebar(surface, sidebar_rect)

    def _render_strings(self, surface: pygame.Surface) -> None:
        """Draw investigation threads connecting related pinned cards."""
        active_path = self.state.active_path
        active_edge_pairs = set()
        if len(active_path) >= 2:
            for i in range(len(active_path) - 1):
                u, v = active_path[i], active_path[i + 1]
                active_edge_pairs.add((u, v))
                active_edge_pairs.add((v, u))

        # Draw inactive strings first
        for u, v, rel_type, explanation, ev_id, reliability in self.state.case.relationships:
            if u not in self.cards or v not in self.cards:
                continue
            card_u = self.cards[u]
            card_v = self.cards[v]
            if not self._is_card_visible(card_u) or not self._is_card_visible(card_v):
                continue

            is_active = (u, v) in active_edge_pairs
            if not is_active:
                draw_curved_string(surface, card_u.pin_pos, card_v.pin_pos, is_active=False)

        # Draw active highlighted strings on top with glowing pulse
        for u, v, rel_type, explanation, ev_id, reliability in self.state.case.relationships:
            if u not in self.cards or v not in self.cards:
                continue
            card_u = self.cards[u]
            card_v = self.cards[v]
            if not self._is_card_visible(card_u) or not self._is_card_visible(card_v):
                continue

            if (u, v) in active_edge_pairs:
                draw_curved_string(surface, card_u.pin_pos, card_v.pin_pos, is_active=True, pulse_phase=self.pulse_phase)

    def _render_card(self, surface: pygame.Surface, card: BoardCard) -> None:
        """Render an individual physical case document card."""
        is_selected = (card.entity_id == self.selected_card_id)
        is_in_path = card.entity_id in self.state.active_path

        # Drop shadow
        shadow_rect = pygame.Rect(card.x + 3, card.y + 4, card.width, card.height)
        shadow_surf = pygame.Surface((card.width, card.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 110), (0, 0, card.width, card.height), border_radius=5)
        surface.blit(shadow_surf, shadow_rect.topleft)

        # Card body
        card_rect = card.rect
        pygame.draw.rect(surface, PARCHMENT_CARD, card_rect, border_radius=5)

        # Border (gold if selected/in active path)
        border_color = CARD_HOVER_BORDER if (is_selected or is_in_path) else CARD_BORDER
        border_width = 2 if (is_selected or is_in_path) else 1
        pygame.draw.rect(surface, border_color, card_rect, width=border_width, border_radius=5)

        # Category header banner
        header_color = COLOR_SUSPECT if card.category == "suspect" else (
            COLOR_LOCATION if card.category == "location" else (
                COLOR_ARTIFACT if card.entity_id == "EV-01" else COLOR_VERIFIED
            )
        )
        banner_rect = pygame.Rect(card.x + 1, card.y + 1, card.width - 2, 18)
        pygame.draw.rect(surface, header_color, banner_rect, border_top_left_radius=4, border_top_right_radius=4)

        # Category label in banner
        font_tiny = FontManager.get(size=11, bold=True)
        cat_text = card.category.upper()
        if card.category == "clue" and card.metadata.get("importance") == "CRITICAL":
            cat_text = "KEY EVIDENCE"
        lbl_surf = font_tiny.render(cat_text, True, (255, 255, 255))
        surface.blit(lbl_surf, (card.x + 8, card.y + 3))

        # Card Title
        font_name = FontManager.get(size=13, bold=True, serif=True)
        words = card.name.split()
        if len(words) <= 2:
            line1 = card.name
            line2 = ""
        else:
            line1 = " ".join(words[:2])
            line2 = " ".join(words[2:])

        t1_surf = font_name.render(line1, True, CARD_TEXT_MAIN)
        surface.blit(t1_surf, (card.x + 8, card.y + 24))
        if line2:
            t2_surf = font_name.render(line2, True, CARD_TEXT_MAIN)
            surface.blit(t2_surf, (card.x + 8, card.y + 38))

        # If suspect, draw small portrait avatar silhouette
        if card.category == "suspect":
            avatar_rect = pygame.Rect(card.x + card.width - 48, card.y + 22, 40, 48)
            draw_suspect_silhouette(surface, avatar_rect, card.metadata.get("avatar_type", "contractor"))

        # Metadata / ID tag at bottom
        font_meta = FontManager.get(size=11, bold=False)
        id_surf = font_meta.render(f"[{card.entity_id}]", True, CARD_TEXT_MUTED)
        surface.blit(id_surf, (card.x + 8, card.y + card.height - 18))

        # Verification tag pill
        if card.category == "clue":
            rel = card.metadata.get("reliability", "VERIFIED")
            rel_color = COLOR_VERIFIED if rel == "VERIFIED" else (
                COLOR_TESTIMONY if rel == "TESTIMONY" else COLOR_UNCONFIRMED
            )
            rel_pill = pygame.Rect(card.x + card.width - 64, card.y + card.height - 18, 56, 14)
            pygame.draw.rect(surface, rel_color, rel_pill, border_radius=3)
            rel_lbl = font_tiny.render(rel[:6], True, (255, 255, 255))
            surface.blit(rel_lbl, (rel_pill.x + 4, rel_pill.y + 1))

        # Push-pin at top center
        draw_pin(surface, card.pin_pos[0], card.pin_pos[1], radius=5)

    def _render_board_controls(self, surface: pygame.Surface) -> None:
        """Render filter tabs and reset buttons at the top of the corkboard."""
        font = FontManager.get(size=12, bold=True)
        tabs = [
            ("ALL", "All Entities (24)"),
            ("SUSPECTS", "Suspects (4)"),
            ("EVIDENCE", "Evidence (14)"),
            ("LOCATIONS", "Locations (6)"),
        ]

        tx = 15
        ty = 12
        for mode, title in tabs:
            is_active = (self.filter_mode == mode)
            bg = BG_PANEL_ALT if is_active else BG_DARK
            border = TEXT_GOLD if is_active else BG_BORDER
            text_col = TEXT_GOLD if is_active else TEXT_LIGHT

            btn_rect = pygame.Rect(tx, ty, 115, 26)
            pygame.draw.rect(surface, bg, btn_rect, border_radius=4)
            pygame.draw.rect(surface, border, btn_rect, width=1, border_radius=4)

            text_surf = font.render(title, True, text_col)
            surface.blit(text_surf, (tx + 8, ty + 6))
            tx += 122

        # Reset Layout button
        reset_rect = pygame.Rect(surface.get_width() - 110, ty, 95, 26)
        pygame.draw.rect(surface, BG_DARK, reset_rect, border_radius=4)
        pygame.draw.rect(surface, BG_BORDER, reset_rect, width=1, border_radius=4)
        r_text = font.render("Reset Layout", True, TEXT_LIGHT)
        surface.blit(r_text, (reset_rect.x + 10, ty + 6))

    def _render_sidebar(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render the right investigation inspector and query controls."""
        # Panel background
        pygame.draw.rect(surface, BG_PANEL, rect)
        pygame.draw.line(surface, BG_BORDER, (rect.x, rect.y), (rect.x, rect.bottom), 2)

        font_h = FontManager.get(size=16, bold=True, serif=True)
        font_b = FontManager.get(size=13, bold=False)
        font_bold = FontManager.get(size=13, bold=True)
        font_tiny = FontManager.get(size=11, bold=False)

        x_pad = rect.x + 16
        w_inner = rect.width - 32
        curr_y = rect.y + 16

        # Header: Dossier Inspector
        hdr = font_h.render("CASE FILE DOSSIER", True, TEXT_GOLD)
        surface.blit(hdr, (x_pad, curr_y))
        curr_y += 26
        pygame.draw.line(surface, BG_BORDER, (x_pad, curr_y), (x_pad + w_inner, curr_y), 1)
        curr_y += 12

        # Selected Entity Details
        if self.selected_card_id:
            entity = self.state.case.get_entity_by_id(self.selected_card_id)
            if entity:
                name = entity["name"]
                cat = entity.get("category", entity.get("role", "Suspect"))

                # Entity Name & ID
                name_surf = font_bold.render(name, True, TEXT_WHITE)
                surface.blit(name_surf, (x_pad, curr_y))
                curr_y += 20

                sub_surf = font_tiny.render(f"Category: {cat.upper()} | ID: [{self.selected_card_id}]", True, TEXT_MUTED)
                surface.blit(sub_surf, (x_pad, curr_y))
                curr_y += 24

                # Details / Alibi
                desc = entity.get("description", "")
                if "alibi" in entity:
                    desc += f"\nAlibi: {entity['alibi']}"

                # Render multiline text
                curr_y = self._render_wrapped_text(surface, desc, x_pad, curr_y, w_inner, font_b, TEXT_LIGHT)
                curr_y += 8

                # Source & Timestamp
                if "source" in entity:
                    src_surf = font_tiny.render(f"Source: {entity['source']}", True, TEXT_GOLD)
                    surface.blit(src_surf, (x_pad, curr_y))
                    curr_y += 18
                if "timestamp" in entity:
                    ts_surf = font_tiny.render(f"Timestamp: {entity['timestamp']}", True, TEXT_CYAN)
                    surface.blit(ts_surf, (x_pad, curr_y))
                    curr_y += 20

                # "Add to Working Theory" Button (for evidence)
                if self.selected_card_id.startswith("EV-"):
                    in_theory = self.state.is_in_theory(self.selected_card_id)
                    btn_rect = pygame.Rect(x_pad, curr_y, w_inner, 32)
                    btn_color = COLOR_VERIFIED if in_theory else BG_PANEL_ALT
                    pygame.draw.rect(surface, btn_color, btn_rect, border_radius=4)
                    pygame.draw.rect(surface, TEXT_GOLD if in_theory else BG_BORDER, btn_rect, width=1, border_radius=4)
                    btn_txt = "Pinned to Theory [Active]" if in_theory else "+ Add to Theory Hypothesis"
                    t_surf = font_bold.render(btn_txt, True, TEXT_WHITE if in_theory else TEXT_LIGHT)
                    surface.blit(t_surf, (btn_rect.x + (w_inner - t_surf.get_width()) // 2, btn_rect.y + 8))
                    curr_y += 42
        else:
            none_surf = font_b.render("Select an evidence card on the board to view its dossier.", True, TEXT_MUTED)
            surface.blit(none_surf, (x_pad, curr_y))
            curr_y += 40

        # Query & Relationship Tracing Section
        curr_y = max(curr_y, rect.y + 360)
        pygame.draw.line(surface, BG_BORDER, (x_pad, curr_y), (x_pad + w_inner, curr_y), 1)
        curr_y += 10

        q_hdr = font_h.render("RELATIONSHIP QUERY", True, TEXT_GOLD)
        surface.blit(q_hdr, (x_pad, curr_y))
        curr_y += 24

        # Search Autocomplete field
        search_box = pygame.Rect(x_pad, curr_y, w_inner, 28)
        pygame.draw.rect(surface, BG_DARKEST, search_box, border_radius=4)
        border_col = TEXT_GOLD if self.search_active else BG_BORDER
        pygame.draw.rect(surface, border_col, search_box, width=1, border_radius=4)
        txt = self.search_text if self.search_text else "Type to search entities (Trie)..."
        txt_col = TEXT_WHITE if self.search_text else TEXT_MUTED
        s_surf = font_tiny.render(txt, True, txt_col)
        surface.blit(s_surf, (search_box.x + 8, search_box.y + 7))
        curr_y += 34

        # Autocomplete dropdown
        if self.search_active and self.autocomplete_results:
            for name, meta in self.autocomplete_results[:4]:
                item_rect = pygame.Rect(x_pad, curr_y, w_inner, 24)
                pygame.draw.rect(surface, BG_PANEL_ALT, item_rect)
                pygame.draw.rect(surface, BG_BORDER, item_rect, width=1)
                item_surf = font_tiny.render(f"{name} ({meta['type']})", True, TEXT_LIGHT)
                surface.blit(item_surf, (item_rect.x + 6, item_rect.y + 4))
                curr_y += 25
            curr_y += 5

        # From / To endpoints display & selector buttons
        from_name = self.state.case.graph.nodes[self.query_from_id].name if self.query_from_id in self.state.case.graph.nodes else self.query_from_id
        to_name = self.state.case.graph.nodes[self.query_to_id].name if self.query_to_id in self.state.case.graph.nodes else self.query_to_id

        lbl_f = font_tiny.render(f"From: {from_name[:24]}", True, TEXT_LIGHT)
        surface.blit(lbl_f, (x_pad, curr_y))
        curr_y += 16

        lbl_t = font_tiny.render(f"To:   {to_name[:24]}", True, TEXT_LIGHT)
        surface.blit(lbl_t, (x_pad, curr_y))
        curr_y += 20

        # Endpoint Buttons
        btn_w = (w_inner - 10) // 2
        btn_from = pygame.Rect(x_pad, curr_y, btn_w, 26)
        btn_to = pygame.Rect(x_pad + btn_w + 10, curr_y, btn_w, 26)
        pygame.draw.rect(surface, BG_PANEL_ALT, btn_from, border_radius=4)
        pygame.draw.rect(surface, BG_PANEL_ALT, btn_to, border_radius=4)
        pygame.draw.rect(surface, BG_BORDER, btn_from, width=1, border_radius=4)
        pygame.draw.rect(surface, BG_BORDER, btn_to, width=1, border_radius=4)

        t_f = font_tiny.render("Set Selected as From", True, TEXT_LIGHT)
        t_t = font_tiny.render("Set Selected as To", True, TEXT_LIGHT)
        surface.blit(t_f, (btn_from.x + 6, btn_from.y + 6))
        surface.blit(t_t, (btn_to.x + 12, btn_to.y + 6))
        curr_y += 34

        # Algorithm switch: BFS vs DFS
        algo_btn = pygame.Rect(x_pad, curr_y, w_inner, 26)
        pygame.draw.rect(surface, BG_DARKEST, algo_btn, border_radius=4)
        pygame.draw.rect(surface, BG_BORDER, algo_btn, width=1, border_radius=4)
        algo_title = "Algorithm: BFS (Shortest Path)" if self.query_use_bfs else "Algorithm: DFS (Depth-First Route)"
        algo_surf = font_tiny.render(algo_title, True, TEXT_GOLD)
        surface.blit(algo_surf, (algo_btn.x + 10, algo_btn.y + 6))
        curr_y += 32

        # "Trace Connection" Button
        trace_btn = pygame.Rect(x_pad, curr_y, w_inner, 32)
        pygame.draw.rect(surface, STRING_NORMAL, trace_btn, border_radius=4)
        pygame.draw.rect(surface, STRING_ACTIVE, trace_btn, width=1, border_radius=4)
        trace_surf = font_bold.render("Trace Connection Path", True, TEXT_WHITE)
        surface.blit(trace_surf, (trace_btn.x + (w_inner - trace_surf.get_width()) // 2, trace_btn.y + 8))
        curr_y += 40

        # Query Result Box
        if self.state.last_query_result:
            q_res = self.state.last_query_result
            res_box = pygame.Rect(x_pad, curr_y, w_inner, 100)
            pygame.draw.rect(surface, BG_DARKEST, res_box, border_radius=4)
            pygame.draw.rect(surface, BG_BORDER, res_box, width=1, border_radius=4)

            status_col = COLOR_VERIFIED if q_res["found"] else COLOR_CONTRADICTORY
            status_txt = f"{q_res['algorithm']} Result: {'CONNECTED' if q_res['found'] else 'NO PATH'}"
            s_s = font_tiny.render(status_txt, True, status_col)
            surface.blit(s_s, (res_box.x + 8, res_box.y + 6))

            if q_res["found"]:
                path_str = " -> ".join(q_res["path"][:5])
                if len(q_res["path"]) > 5:
                    path_str += "..."
                p_s = font_tiny.render(f"Path ({q_res['edge_count']} leads): {path_str}", True, TEXT_WHITE)
                surface.blit(p_s, (res_box.x + 8, res_box.y + 24))

                # Render explanation
                self._render_wrapped_text(surface, q_res.get("explanation", ""), res_box.x + 8, res_box.y + 44, w_inner - 16, font_tiny, TEXT_LIGHT)

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
        """Helper to render word-wrapped text, returning bottom y coordinate."""
        lines = text.split("\n")
        curr_y = y
        line_height = font.get_linesize()

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
