"""
Main Evidence Board View for The Midnight Dossier.
Features draggable physical-style cards, pins, red connecting strings,
interactive Case File Dossier, Trie autocomplete search, and relationship tracing.
All interactive controls use strictly synchronized hitboxes with hover feedback.
"""

import pygame
import math
from typing import Dict, List, Optional, Tuple, Any
from .theme import (
    BG_DARKEST, BG_DARK, BG_PANEL, BG_PANEL_ALT, BG_BORDER,
    CORK_FRAME, PARCHMENT_CARD, PARCHMENT_LIGHT, PARCHMENT_DARK,
    CARD_BORDER, CARD_HOVER_BORDER, CARD_TEXT_MAIN, CARD_TEXT_MUTED,
    PIN_BRASS, STRING_NORMAL, STRING_ACTIVE, STRING_GLOW,
    COLOR_VERIFIED, COLOR_TESTIMONY, COLOR_UNCONFIRMED, COLOR_CONTRADICTORY,
    COLOR_SUSPECT, COLOR_LOCATION, COLOR_ARTIFACT,
    TEXT_WHITE, TEXT_LIGHT, TEXT_MUTED, TEXT_GOLD, TEXT_CYAN,
    FontManager, create_corkboard_surface, draw_pin, draw_curved_string, draw_suspect_silhouette
)
from .investigation import InvestigationState
from .ui_components import UIButton


class BoardCard:
    """Represents a physical card pinned to the evidence corkboard."""

    def __init__(
        self,
        entity_id: str,
        name: str,
        category: str,
        x: int,
        y: int,
        width: int = 155,
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
        self.is_hovered = False

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
        self.search_box_rect: Optional[pygame.Rect] = None
        self.autocomplete_item_rects: List[Tuple[pygame.Rect, str, str]] = []

        # Dossier action feedback
        self.dossier_status_msg: Optional[str] = None
        self.dossier_status_timer: float = 0.0

        # Interactive UI buttons
        self.filter_buttons: List[UIButton] = []
        self.board_action_buttons: List[UIButton] = []
        self.sidebar_buttons: List[UIButton] = []
        self.neighbor_buttons: List[Tuple[UIButton, str]] = []

        self._init_card_layout()
        self._init_board_buttons()

    def _init_card_layout(self) -> None:
        """Create initial organized layout of cards on the board."""
        # 1. Suspects (Top row)
        suspect_positions = [
            ("SUS-01", 60, 52),
            ("SUS-02", 240, 52),
            ("SUS-03", 420, 52),
            ("SUS-04", 600, 52),
        ]
        for sid, sx, sy in suspect_positions:
            s_data = self.state.case.get_entity_by_id(sid)
            if s_data:
                self.cards[sid] = BoardCard(
                    sid, s_data["name"], "suspect", sx, sy, width=155, height=110, metadata=s_data
                )

        # 2. Key Evidence (Middle rows)
        evidence_positions = [
            ("EV-01", 240, 195),  # Stolen Compass (Center)
            ("EV-02", 60, 195),   # Maintenance Request
            ("EV-03", 420, 195),  # CCTV Glitch
            ("EV-04", 60, 335),   # Keycard Scan
            ("EV-05", 240, 335),  # Missing Case
            ("EV-06", 420, 335),  # Van Departure
            ("EV-07", 600, 195),  # Wire Snips
            ("EV-08", 600, 335),  # Sync Script
            ("EV-09", 60, 475),   # Tea Room Statement
            ("EV-10", 240, 475),  # Radio Audio
            ("EV-11", 420, 475),  # Guard Permit
            ("EV-12", 600, 475),  # Dinner Toll
        ]
        for eid, ex, ey in evidence_positions:
            e_data = self.state.case.get_entity_by_id(eid)
            if e_data:
                self.cards[eid] = BoardCard(
                    eid, e_data["name"], "clue", ex, ey, width=155, height=95, metadata=e_data
                )

        # 3. Locations (Bottom row / flanks)
        location_positions = [
            ("LOC-01", 60, 610),
            ("LOC-02", 215, 610),
            ("LOC-03", 370, 610),
            ("LOC-04", 525, 610),
            ("LOC-05", 680, 610),
        ]
        for lid, lx, ly in location_positions:
            loc_data = self.state.case.get_entity_by_id(lid)
            if loc_data:
                self.cards[lid] = BoardCard(
                    lid, loc_data["name"], "location", lx, ly, width=140, height=85, metadata=loc_data
                )

    def _init_board_buttons(self) -> None:
        """Initialize filter and action buttons with unified hitboxes."""
        self.filter_buttons = [
            UIButton(pygame.Rect(15, 12, 105, 26), "All (24)", callback=lambda: self.set_filter("ALL"), font_size=11),
            UIButton(pygame.Rect(125, 12, 105, 26), "Suspects (4)", callback=lambda: self.set_filter("SUSPECTS"), font_size=11),
            UIButton(pygame.Rect(235, 12, 105, 26), "Evidence (14)", callback=lambda: self.set_filter("EVIDENCE"), font_size=11),
            UIButton(pygame.Rect(345, 12, 105, 26), "Locations (6)", callback=lambda: self.set_filter("LOCATIONS"), font_size=11),
        ]
        self.btn_reset = UIButton(pygame.Rect(0, 12, 95, 26), "Reset Layout", callback=self.reset_layout, font_size=11)
        self.btn_undo = UIButton(pygame.Rect(0, 12, 60, 26), "Undo", callback=self._perform_undo, font_size=11)
        self.btn_redo = UIButton(pygame.Rect(0, 12, 60, 26), "Redo", callback=self._perform_redo, font_size=11)
        self.board_action_buttons = [self.btn_undo, self.btn_redo, self.btn_reset]

    def set_filter(self, mode: str) -> None:
        self.filter_mode = mode
        for btn in self.filter_buttons:
            btn.is_active = (mode in btn.text.upper())

    def reset_layout(self) -> None:
        """Reset all cards to default non-overlapping positions."""
        for card in self.cards.values():
            card.x, card.y = card.initial_pos

    def update(self, dt: float) -> None:
        self.pulse_phase += dt
        if self.dossier_status_timer > 0:
            self.dossier_status_timer -= dt
            if self.dossier_status_timer <= 0:
                self.dossier_status_msg = None

    def show_dossier_feedback(self, msg: str, duration: float = 3.0) -> None:
        self.dossier_status_msg = msg
        self.dossier_status_timer = duration

    # --------------------------------------------------------------------------
    # EVENT HANDLING
    # --------------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event, board_rect: pygame.Rect, sidebar_rect: pygame.Rect) -> None:
        """Handle mouse clicks, drags, typing, and keyboard shortcuts."""
        # 1. Mouse Motion & Hover Tracking
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            if board_rect.collidepoint(mx, my):
                rel_x = mx - board_rect.x
                rel_y = my - board_rect.y
                for btn in self.filter_buttons:
                    btn.check_hover((rel_x, rel_y))
                for btn in self.board_action_buttons:
                    btn.check_hover((rel_x, rel_y))

                for card in self.cards.values():
                    card.is_hovered = card.rect.collidepoint((rel_x, rel_y))

            elif sidebar_rect.collidepoint(mx, my):
                # Sidebar controls are in SCREEN coordinates (mx, my)
                for btn in self.sidebar_buttons:
                    btn.check_hover((mx, my))
                for btn, _ in self.neighbor_buttons:
                    btn.check_hover((mx, my))

        # 2. Mouse Click Handling
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # A. Clicks inside Board area
            if board_rect.collidepoint(mx, my):
                rel_x = mx - board_rect.x
                rel_y = my - board_rect.y

                # Deactivate search focus if clicking the board
                if self.search_active:
                    self.search_active = False

                # Check top filter buttons
                for btn in self.filter_buttons:
                    if btn.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (rel_x, rel_y), "button": 1})):
                        return

                # Check board action buttons (Reset, Undo, Redo)
                for btn in self.board_action_buttons:
                    if btn.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (rel_x, rel_y), "button": 1})):
                        return

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

            # B. Clicks inside Sidebar area (using absolute screen coordinates mx, my)
            elif sidebar_rect.collidepoint(mx, my):
                self._handle_sidebar_click(mx, my, sidebar_rect, event)

        # 3. Mouse Up (Drag End)
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

        # 4. Mouse Drag Movement
        elif event.type == pygame.MOUSEMOTION:
            if self.dragged_card_id and self.dragged_card_id in self.cards:
                mx, my = event.pos
                rel_x = mx - board_rect.x
                rel_y = my - board_rect.y
                card = self.cards[self.dragged_card_id]
                new_x = rel_x - card.drag_offset_x
                new_y = rel_y - card.drag_offset_y

                # Clamp within board surface
                card.x = max(10, min(board_rect.width - card.width - 10, new_x))
                card.y = max(45, min(board_rect.height - card.height - 10, new_y))

        # 5. Text Input Event (Pygame 2 / Pygame-CE)
        elif event.type == pygame.TEXTINPUT and self.search_active:
            self.search_text += event.text
            self._update_autocomplete()

        # 6. Keydown Events
        elif event.type == pygame.KEYDOWN:
            # Undo / Redo shortcuts (Ctrl+Z / Ctrl+Y)
            if event.mod & pygame.KMOD_CTRL:
                if event.key == pygame.K_z:
                    self._perform_undo()
                    return
                elif event.key == pygame.K_y:
                    self._perform_redo()
                    return

            # Active Search Text Entry & Navigation
            if self.search_active:
                if event.key == pygame.K_BACKSPACE:
                    self.search_text = self.search_text[:-1]
                    self._update_autocomplete()
                elif event.key == pygame.K_RETURN:
                    if self.autocomplete_results:
                        name, meta = self.autocomplete_results[0]
                        self._select_autocomplete_entity(meta["id"], name)
                    elif self.search_text.strip():
                        # Direct ID or name match
                        target_id = self.search_text.strip().upper()
                        e = self.state.case.get_entity_by_id(target_id)
                        if e:
                            self._select_autocomplete_entity(e["id"], e["name"])
                    self.search_active = False
                elif event.key == pygame.K_ESCAPE:
                    self.search_active = False
                elif event.unicode and len(event.unicode) == 1 and event.unicode.isprintable() and not (event.mod & pygame.KMOD_CTRL):
                    # Fallback for environments where TEXTINPUT is inactive
                    # Guard against double append if TEXTINPUT was already processed
                    self.search_text += event.unicode
                    self._update_autocomplete()

    def _handle_sidebar_click(self, mx: int, my: int, rect: pygame.Rect, event: pygame.event.Event) -> None:
        """Handle clicks on sidebar buttons, search input, and autocomplete items in screen coordinates."""
        # 1. Search Box Activation
        if self.search_box_rect and self.search_box_rect.collidepoint(mx, my):
            self.search_active = True
            try:
                pygame.key.start_text_input()
            except Exception:
                pass
            self._update_autocomplete()
            return

        # 2. Autocomplete Dropdown Selection
        if self.search_active and self.autocomplete_item_rects:
            for item_rect, meta_id, meta_name in self.autocomplete_item_rects:
                if item_rect.collidepoint(mx, my):
                    self._select_autocomplete_entity(meta_id, meta_name)
                    return

        # If clicking outside search box and suggestions, deactivate search
        if self.search_active:
            self.search_active = False
            try:
                pygame.key.stop_text_input()
            except Exception:
                pass

        # 3. Dynamic Sidebar Action Buttons (Theory, From, To, Swap, Algo, Trace, Clear)
        for btn in self.sidebar_buttons:
            if btn.handle_event(event):
                return

        # 4. Connected Leads / Neighbor Pills
        for btn, neighbor_id in self.neighbor_buttons:
            if btn.handle_event(event):
                self.selected_card_id = neighbor_id
                self.state.mark_examined(neighbor_id)
                n_node = self.state.case.graph.get_node(neighbor_id)
                n_name = n_node.name if n_node else neighbor_id
                self.show_dossier_feedback(f"Focused lead: {n_name}")
                return

    def _select_autocomplete_entity(self, entity_id: str, name: str) -> None:
        """Select entity from autocomplete and update board state."""
        self.selected_card_id = entity_id
        self.state.mark_examined(entity_id)
        self.search_text = name
        self.search_active = False
        try:
            pygame.key.stop_text_input()
        except Exception:
            pass
        self.show_dossier_feedback(f"Found & focused: {name} [{entity_id}]")

    def _update_autocomplete(self) -> None:
        query = self.search_text.strip()
        if query:
            self.autocomplete_results = self.state.autocomplete(query)
        else:
            self.autocomplete_results = []

    def _perform_undo(self) -> None:
        action = self.state.undo_redo.undo()
        if action:
            if action["type"] == "add_theory":
                if action["evidence_id"] in self.state.theory_evidence_ids:
                    self.state.theory_evidence_ids.remove(action["evidence_id"])
                    self.show_dossier_feedback(f"Undo: Removed [{action['evidence_id']}] from theory.")
            elif action["type"] == "remove_theory":
                self.state.theory_evidence_ids.append(action["evidence_id"])
                self.show_dossier_feedback(f"Undo: Restored [{action['evidence_id']}] to theory.")
            elif action["type"] == "move_card":
                cid = action["entity_id"]
                if cid in self.cards:
                    self.cards[cid].x, self.cards[cid].y = self.cards[cid].initial_pos
                    self.show_dossier_feedback(f"Undo: Reset position of [{cid}].")

    def _perform_redo(self) -> None:
        action = self.state.undo_redo.redo()
        if action:
            if action["type"] == "add_theory":
                if action["evidence_id"] not in self.state.theory_evidence_ids:
                    self.state.theory_evidence_ids.append(action["evidence_id"])
                    self.show_dossier_feedback(f"Redo: Pinned [{action['evidence_id']}] to theory.")
            elif action["type"] == "remove_theory":
                if action["evidence_id"] in self.state.theory_evidence_ids:
                    self.state.theory_evidence_ids.remove(action["evidence_id"])
                    self.show_dossier_feedback(f"Redo: Removed [{action['evidence_id']}] from theory.")
            elif action["type"] == "move_card":
                cid = action["entity_id"]
                if cid in self.cards:
                    self.cards[cid].x, self.cards[cid].y = action["pos"]
                    self.show_dossier_feedback(f"Redo: Restored position of [{cid}].")

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

    # --------------------------------------------------------------------------
    # RENDERING
    # --------------------------------------------------------------------------

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

        # 5. Render Sidebar / Investigation Inspector (drawn in screen coordinates)
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

        # Border (gold if selected/in active path, bright if hovered)
        if is_selected or is_in_path:
            border_color = CARD_HOVER_BORDER
            border_width = 2
        elif card.is_hovered:
            border_color = (180, 150, 80)
            border_width = 2
        else:
            border_color = CARD_BORDER
            border_width = 1

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
        font_name = FontManager.get(size=12, bold=True, serif=True)
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
        """Render filter tabs and reset buttons with unified interactive buttons."""
        for btn in self.filter_buttons:
            btn.is_active = (self.filter_mode in btn.text.upper())
            btn.render(surface)

        # Position and render board action buttons on the right
        right_x = surface.get_width() - 105
        self.btn_reset.update_pos(right_x, 12)
        self.btn_reset.render(surface)

        self.btn_redo.update_pos(right_x - 70, 12)
        self.btn_redo.render(surface)

        self.btn_undo.update_pos(right_x - 140, 12)
        self.btn_undo.render(surface)

    def _render_sidebar(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render the right investigation inspector and query controls in screen coordinates."""
        # Panel background
        pygame.draw.rect(surface, BG_PANEL, rect)
        pygame.draw.line(surface, BG_BORDER, (rect.x, rect.y), (rect.x, rect.bottom), 2)

        font_h = FontManager.get(size=14, bold=True, serif=True)
        font_b = FontManager.get(size=11, bold=False)
        font_bold = FontManager.get(size=11, bold=True)
        font_tiny = FontManager.get(size=10, bold=False)
        font_tiny_b = FontManager.get(size=10, bold=True)

        x_pad = rect.x + 14
        w_inner = rect.width - 28
        curr_y = rect.y + 10

        self.sidebar_buttons.clear()
        self.neighbor_buttons.clear()

        # Header: Dossier Inspector
        hdr = font_h.render("CASE FILE DOSSIER", True, TEXT_GOLD)
        surface.blit(hdr, (x_pad, curr_y))
        curr_y += 20
        pygame.draw.line(surface, BG_BORDER, (x_pad, curr_y), (x_pad + w_inner, curr_y), 1)
        curr_y += 8

        # Status feedback banner if active
        if self.dossier_status_msg:
            stat_rect = pygame.Rect(x_pad, curr_y, w_inner, 20)
            pygame.draw.rect(surface, BG_DARKEST, stat_rect, border_radius=3)
            pygame.draw.rect(surface, TEXT_GOLD, stat_rect, width=1, border_radius=3)
            surface.blit(font_tiny_b.render(self.dossier_status_msg, True, TEXT_GOLD), (stat_rect.x + 6, stat_rect.y + 3))
            curr_y += 24

        # Selected Entity Details
        if self.selected_card_id:
            entity = self.state.case.get_entity_by_id(self.selected_card_id)
            if entity:
                name = entity["name"]
                cat = entity.get("category", entity.get("role", "Suspect"))

                # Entity Name & ID
                name_surf = font_bold.render(name[:30], True, TEXT_WHITE)
                surface.blit(name_surf, (x_pad, curr_y))
                curr_y += 16

                sub_surf = font_tiny.render(f"Category: {cat.upper()} | ID: [{self.selected_card_id}]", True, TEXT_MUTED)
                surface.blit(sub_surf, (x_pad, curr_y))
                curr_y += 18

                # Details / Alibi
                desc = entity.get("description", "")
                if "alibi" in entity:
                    desc += f"\nAlibi: {entity['alibi']}"

                curr_y = self._render_wrapped_text(surface, desc, x_pad, curr_y, w_inner, font_b, TEXT_LIGHT)
                curr_y += 6

                # Source & Timestamp
                if "source" in entity:
                    src_surf = font_tiny.render(f"Source: {entity['source'][:32]}", True, TEXT_GOLD)
                    surface.blit(src_surf, (x_pad, curr_y))
                    curr_y += 15
                if "timestamp" in entity:
                    ts_surf = font_tiny.render(f"Timestamp: {entity['timestamp']}", True, TEXT_CYAN)
                    surface.blit(ts_surf, (x_pad, curr_y))
                    curr_y += 15

                # Reliability Badge
                rel = entity.get("reliability", "TESTIMONY" if "alibi" in entity else "VERIFIED")
                rel_color = COLOR_VERIFIED if rel == "VERIFIED" else (
                    COLOR_TESTIMONY if rel == "TESTIMONY" else (
                        COLOR_CONTRADICTORY if rel == "DISPUTED" else COLOR_UNCONFIRMED
                    )
                )
                rel_text = "Verified Record" if rel == "VERIFIED" else (
                    "Witness Statement" if rel == "TESTIMONY" else (
                        "Disputed Claim" if rel == "DISPUTED" else "Unconfirmed Lead"
                    )
                )
                rel_pill = pygame.Rect(x_pad, curr_y, 140, 16)
                pygame.draw.rect(surface, rel_color, rel_pill, border_radius=3)
                surface.blit(font_tiny_b.render(rel_text, True, TEXT_WHITE), (rel_pill.x + 6, rel_pill.y + 1))
                curr_y += 20

                # Direct Connected Neighbors in Graph (Connected Leads)
                neighbors = self.state.case.graph.get_neighbors(self.selected_card_id)
                if neighbors:
                    surface.blit(font_tiny.render("Connected Leads (Click to Inspect):", True, TEXT_MUTED), (x_pad, curr_y))
                    curr_y += 15
                    col_x = 0
                    for edge in neighbors[:4]:
                        n_node = self.state.case.graph.get_node(edge.target)
                        n_title = n_node.name[:14] if n_node else edge.target
                        btn_n = UIButton(
                            pygame.Rect(x_pad + col_x, curr_y, (w_inner - 6) // 2, 22),
                            f"-> {n_title}",
                            font_size=10,
                            bold=False,
                            bg_color=BG_DARKEST
                        )
                        btn_n.render(surface)
                        self.neighbor_buttons.append((btn_n, edge.target))
                        if col_x == 0:
                            col_x = (w_inner - 6) // 2 + 6
                        else:
                            col_x = 0
                            curr_y += 24
                    if col_x != 0:
                        curr_y += 24
                    curr_y += 4

                # "Add to Working Theory" Button (for evidence)
                if self.selected_card_id.startswith("EV-"):
                    in_theory = self.state.is_in_theory(self.selected_card_id)
                    btn_theory = UIButton(
                        pygame.Rect(x_pad, curr_y, w_inner, 26),
                        "Pinned to Theory [Click to Remove]" if in_theory else "+ Add to Theory Hypothesis",
                        callback=self._toggle_current_theory,
                        font_size=11,
                        bold=True,
                        bg_color=COLOR_VERIFIED if in_theory else BG_PANEL_ALT,
                        active_bg=COLOR_VERIFIED,
                        is_active=in_theory
                    )
                    btn_theory.render(surface)
                    self.sidebar_buttons.append(btn_theory)
                    curr_y += 30

                # "Trace from Here" shortcut button
                btn_trace_here = UIButton(
                    pygame.Rect(x_pad, curr_y, w_inner, 22),
                    "Set as Query Source [From]",
                    callback=self._set_current_as_from,
                    font_size=10,
                    bold=False,
                    bg_color=BG_DARKEST
                )
                btn_trace_here.render(surface)
                self.sidebar_buttons.append(btn_trace_here)
                curr_y += 26
        else:
            none_surf = font_b.render("Select an evidence card on the board to view its dossier.", True, TEXT_MUTED)
            surface.blit(none_surf, (x_pad, curr_y))
            curr_y += 26

        # Query & Relationship Tracing Section
        curr_y = max(curr_y, rect.y + 360)
        pygame.draw.line(surface, BG_BORDER, (x_pad, curr_y), (x_pad + w_inner, curr_y), 1)
        curr_y += 8

        q_hdr = font_h.render("RELATIONSHIP QUERY", True, TEXT_GOLD)
        surface.blit(q_hdr, (x_pad, curr_y))
        curr_y += 20

        # Search Autocomplete Input field with Active Focus
        self.search_box_rect = pygame.Rect(x_pad, curr_y, w_inner, 26)
        bg_input = (22, 28, 40) if self.search_active else BG_DARKEST
        pygame.draw.rect(surface, bg_input, self.search_box_rect, border_radius=4)
        border_col = TEXT_GOLD if self.search_active else BG_BORDER
        pygame.draw.rect(surface, border_col, self.search_box_rect, width=1, border_radius=4)

        # Blinking cursor when focused
        cursor_str = "|" if (self.search_active and int(self.pulse_phase * 2) % 2 == 0) else ""
        if self.search_text:
            display_txt = self.search_text + cursor_str
            txt_col = TEXT_WHITE
        else:
            display_txt = "Type to search entities (Trie)..." if not self.search_active else cursor_str
            txt_col = TEXT_MUTED if not self.search_active else TEXT_WHITE

        s_surf = font_tiny.render(display_txt[:34], True, txt_col)
        surface.blit(s_surf, (self.search_box_rect.x + 8, self.search_box_rect.y + 6))
        curr_y += 29

        # Autocomplete dropdown
        self.autocomplete_item_rects.clear()
        if self.search_active and self.autocomplete_results:
            for name, meta in self.autocomplete_results[:4]:
                item_rect = pygame.Rect(x_pad, curr_y, w_inner, 22)
                pygame.draw.rect(surface, BG_PANEL_ALT, item_rect)
                pygame.draw.rect(surface, BG_BORDER, item_rect, width=1)
                item_surf = font_tiny.render(f"{name[:22]} ({meta['type'][:8]})", True, TEXT_LIGHT)
                surface.blit(item_surf, (item_rect.x + 6, item_rect.y + 3))
                self.autocomplete_item_rects.append((item_rect, meta["id"], name))
                curr_y += 23
            curr_y += 3

        # From / To endpoints display
        from_name = self.state.case.graph.nodes[self.query_from_id].name if self.query_from_id in self.state.case.graph.nodes else self.query_from_id
        to_name = self.state.case.graph.nodes[self.query_to_id].name if self.query_to_id in self.state.case.graph.nodes else self.query_to_id

        lbl_f = font_tiny.render(f"From: {from_name[:26]}", True, TEXT_CYAN)
        surface.blit(lbl_f, (x_pad, curr_y))
        curr_y += 15

        lbl_t = font_tiny.render(f"To:   {to_name[:26]}", True, TEXT_CYAN)
        surface.blit(lbl_t, (x_pad, curr_y))
        curr_y += 17

        # Endpoint Buttons & Swap
        btn_w = (w_inner - 36) // 2
        btn_from = UIButton(
            pygame.Rect(x_pad, curr_y, btn_w, 24),
            "Set as From",
            callback=self._set_current_as_from,
            font_size=10
        )
        btn_swap = UIButton(
            pygame.Rect(x_pad + btn_w + 4, curr_y, 28, 24),
            "<->",
            callback=self._swap_endpoints,
            font_size=11,
            bold=True
        )
        btn_to = UIButton(
            pygame.Rect(x_pad + btn_w + 36, curr_y, btn_w, 24),
            "Set as To",
            callback=self._set_current_as_to,
            font_size=10
        )
        btn_from.render(surface)
        btn_swap.render(surface)
        btn_to.render(surface)
        self.sidebar_buttons.extend([btn_from, btn_swap, btn_to])
        curr_y += 27

        # Algorithm switch: BFS vs DFS
        algo_title = "Algorithm: BFS (Shortest Path)" if self.query_use_bfs else "Algorithm: DFS (Depth-First Route)"
        btn_algo = UIButton(
            pygame.Rect(x_pad, curr_y, w_inner, 23),
            algo_title,
            callback=self._toggle_algorithm,
            font_size=10,
            text_color=TEXT_GOLD
        )
        btn_algo.render(surface)
        self.sidebar_buttons.append(btn_algo)
        curr_y += 26

        # "Trace Connection" Button & "Clear"
        btn_trace = UIButton(
            pygame.Rect(x_pad, curr_y, w_inner - 52, 26),
            "Trace Connection Path",
            callback=self._run_trace_query,
            font_size=11,
            bold=True,
            bg_color=STRING_NORMAL,
            hover_bg=STRING_ACTIVE,
            text_color=TEXT_WHITE
        )
        btn_clear = UIButton(
            pygame.Rect(x_pad + w_inner - 48, curr_y, 48, 26),
            "Clear",
            callback=self._clear_trace_query,
            font_size=10
        )
        btn_trace.render(surface)
        btn_clear.render(surface)
        self.sidebar_buttons.extend([btn_trace, btn_clear])
        curr_y += 30

        # Query Result Box
        if self.state.last_query_result:
            q_res = self.state.last_query_result
            res_box = pygame.Rect(x_pad, curr_y, w_inner, 80)
            pygame.draw.rect(surface, BG_DARKEST, res_box, border_radius=4)
            pygame.draw.rect(surface, BG_BORDER, res_box, width=1, border_radius=4)

            status_col = COLOR_VERIFIED if q_res["found"] else COLOR_CONTRADICTORY
            status_txt = f"{q_res['algorithm']}: {'CONNECTED' if q_res['found'] else 'NO PATH'}"
            s_s = font_tiny_b.render(status_txt, True, status_col)
            surface.blit(s_s, (res_box.x + 8, res_box.y + 5))

            if q_res["found"]:
                path_str = " -> ".join(q_res["path"][:5])
                if len(q_res["path"]) > 5:
                    path_str += "..."
                p_s = font_tiny.render(f"Chain ({q_res['edge_count']} leads): {path_str}", True, TEXT_WHITE)
                surface.blit(p_s, (res_box.x + 8, res_box.y + 19))

                # Render explanation
                self._render_wrapped_text(surface, q_res.get("explanation", ""), res_box.x + 8, res_box.y + 34, w_inner - 16, font_tiny, TEXT_LIGHT)

    def _toggle_current_theory(self) -> None:
        if self.selected_card_id:
            added = self.state.toggle_theory_evidence(self.selected_card_id)
            if added:
                self.show_dossier_feedback(f"Pinned [{self.selected_card_id}] to working theory!")
            else:
                self.show_dossier_feedback(f"Removed [{self.selected_card_id}] from working theory.")

    def _set_current_as_from(self) -> None:
        if self.selected_card_id:
            self.query_from_id = self.selected_card_id
            name = self.state.case.graph.nodes[self.selected_card_id].name if self.selected_card_id in self.state.case.graph.nodes else self.selected_card_id
            self.show_dossier_feedback(f"Source set to: {name}")

    def _set_current_as_to(self) -> None:
        if self.selected_card_id:
            self.query_to_id = self.selected_card_id
            name = self.state.case.graph.nodes[self.selected_card_id].name if self.selected_card_id in self.state.case.graph.nodes else self.selected_card_id
            self.show_dossier_feedback(f"Destination set to: {name}")

    def _swap_endpoints(self) -> None:
        self.query_from_id, self.query_to_id = self.query_to_id, self.query_from_id
        self.show_dossier_feedback("Swapped source and destination endpoints.")

    def _toggle_algorithm(self) -> None:
        self.query_use_bfs = not self.query_use_bfs
        algo_name = "BFS (Shortest Path)" if self.query_use_bfs else "DFS (Depth-First Route)"
        self.show_dossier_feedback(f"Active algorithm: {algo_name}")

    def _run_trace_query(self) -> None:
        if self.query_from_id == self.query_to_id:
            self.state.last_query_result = {
                "found": True,
                "path": [self.query_from_id],
                "edges": [],
                "edge_count": 0,
                "algorithm": "BFS" if self.query_use_bfs else "DFS",
                "explanation": "Start and destination entities are identical (0 leads distance)."
            }
            self.state.active_path = [self.query_from_id]
            self.show_dossier_feedback("Endpoints are identical (0 leads).")
            return

        res = self.state.query_relationship(self.query_from_id, self.query_to_id, use_bfs=self.query_use_bfs)
        if res["found"]:
            self.show_dossier_feedback(f"Trace complete: Connected via {res['edge_count']} lead(s)!")
        else:
            self.show_dossier_feedback("No connection exists between these entities in the graph.")

    def _clear_trace_query(self) -> None:
        self.state.clear_active_path()
        self.show_dossier_feedback("Active path and query cleared.")

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
        line_height = font.get_linesize() + 1
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
