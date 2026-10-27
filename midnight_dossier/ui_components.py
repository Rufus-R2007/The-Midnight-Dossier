"""
Interactive UI Components for The Midnight Dossier.
Guarantees that rendered rectangles and clickable hitboxes are 100% synchronized,
with built-in hover feedback, active states, and sound/visual cue hooks.
"""

import pygame
from typing import Optional, Tuple, Callable, Any, List
from .theme import (
    BG_DARK, BG_PANEL, BG_PANEL_ALT, BG_BORDER,
    TEXT_WHITE, TEXT_LIGHT, TEXT_MUTED, TEXT_GOLD, TEXT_CYAN,
    COLOR_VERIFIED, COLOR_UNCONFIRMED, COLOR_CONTRADICTORY,
    FontManager
)


class UIButton:
    """A button whose visual bounds and click detection are strictly unified."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        callback: Optional[Callable[[], None]] = None,
        font_size: int = 12,
        bold: bool = True,
        bg_color: Tuple[int, int, int] = BG_PANEL,
        hover_bg: Tuple[int, int, int] = BG_PANEL_ALT,
        border_color: Tuple[int, int, int] = BG_BORDER,
        text_color: Tuple[int, int, int] = TEXT_LIGHT,
        hover_text_color: Tuple[int, int, int] = TEXT_GOLD,
        border_radius: int = 4,
        is_active: bool = False,
        active_bg: Tuple[int, int, int] = COLOR_VERIFIED,
        tooltip: Optional[str] = None
    ) -> None:
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font_size = font_size
        self.bold = bold
        self.bg_color = bg_color
        self.hover_bg = hover_bg
        self.border_color = border_color
        self.text_color = text_color
        self.hover_text_color = hover_text_color
        self.border_radius = border_radius
        self.is_active = is_active
        self.active_bg = active_bg
        self.tooltip = tooltip
        self.is_hovered = False

    def update_pos(self, x: int, y: int, w: Optional[int] = None, h: Optional[int] = None) -> None:
        """Update position dynamically while maintaining synchronized hitbox."""
        self.rect.x = x
        self.rect.y = y
        if w is not None:
            self.rect.width = w
        if h is not None:
            self.rect.height = h

    def check_hover(self, mouse_pos: Tuple[int, int]) -> bool:
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True if button was clicked."""
        if event.type == pygame.MOUSEMOTION:
            self.check_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False

    def render(self, surface: pygame.Surface) -> None:
        """Render button with hover and active states."""
        if self.is_active:
            bg = self.active_bg
            border = TEXT_GOLD
            txt_col = TEXT_WHITE
        elif self.is_hovered:
            bg = self.hover_bg
            border = TEXT_GOLD
            txt_col = self.hover_text_color
        else:
            bg = self.bg_color
            border = self.border_color
            txt_col = self.text_color

        pygame.draw.rect(surface, bg, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, border, self.rect, width=1, border_radius=self.border_radius)

        font = FontManager.get(size=self.font_size, bold=self.bold)
        lbl = font.render(self.text, True, txt_col)
        surface.blit(
            lbl,
            (
                self.rect.x + (self.rect.width - lbl.get_width()) // 2,
                self.rect.y + (self.rect.height - lbl.get_height()) // 2,
            )
        )
