"""
Theme, Color Palette, Typography, and Procedural Art for The Midnight Dossier.
Implements a cinematic noir thriller aesthetic with procedural graphics.
"""

import pygame
import math
from typing import Tuple, Dict, Optional, List

# ==============================================================================
# COLOR PALETTE
# ==============================================================================

BG_DARKEST = (14, 18, 25)        # Midnight charcoal
BG_DARK = (20, 25, 36)           # Deep midnight navy
BG_PANEL = (27, 34, 48)          # Workstation card panel
BG_PANEL_ALT = (32, 40, 56)      # Elevated panel surface
BG_BORDER = (45, 56, 76)         # Subtle dividing borders

# Corkboard Surface Colors
CORK_BASE = (34, 30, 26)         # Dark aged slate-cork
CORK_DARK = (26, 23, 20)         # Cork texture shadow
CORK_SPECK = (48, 42, 36)        # Cork texture grain speckles
CORK_FRAME = (20, 16, 12)        # Dark wood border frame

# Card & Document Colors
PARCHMENT_LIGHT = (245, 239, 225)# Warm aged ivory paper
PARCHMENT_CARD = (238, 230, 212) # Aged manila folder / case card
PARCHMENT_DARK = (215, 203, 180) # Card shadow / inner edge
CARD_BORDER = (120, 105, 88)     # Manila card border line
CARD_HOVER_BORDER = (212, 175, 55)# Golden focus highlight
CARD_TEXT_MAIN = (24, 20, 16)    # Dark typewriter ink
CARD_TEXT_MUTED = (85, 75, 65)   # Faded secondary ink

# String & Investigation Indicators
STRING_NORMAL = (140, 40, 45)    # Blood red / burgundy evidence string
STRING_MUTED = (90, 32, 36)      # Faded background string
STRING_ACTIVE = (235, 65, 75)    # Glowing active connection string
STRING_GLOW = (255, 105, 115)    # Core illumination highlight

# Pins & Metallic Accents
PIN_BRASS = (212, 175, 55)       # Antique brass push-pin
PIN_HIGHLIGHT = (250, 235, 170)  # Pin specular reflection
PIN_SHADOW = (60, 48, 20)        # Pin drop shadow

# Semantic Badges & Categorization
COLOR_VERIFIED = (42, 157, 143)  # Desaturated teal
COLOR_TESTIMONY = (69, 123, 157) # Slate blue
COLOR_UNCONFIRMED = (231, 111, 81)# Muted amber
COLOR_CONTRADICTORY = (214, 40, 40)# Danger crimson
COLOR_SUSPECT = (212, 175, 55)   # Brass gold
COLOR_LOCATION = (142, 120, 180) # Muted violet
COLOR_ARTIFACT = (230, 180, 60)  # Golden relic

# UI Text Colors
TEXT_WHITE = (240, 244, 250)
TEXT_LIGHT = (210, 218, 230)
TEXT_MUTED = (140, 152, 172)
TEXT_DARK = (70, 80, 98)
TEXT_GOLD = (225, 190, 85)
TEXT_CYAN = (80, 210, 215)


# ==============================================================================
# TYPOGRAPHY SYSTEM
# ==============================================================================

class FontManager:
    """Manages cached fonts with graceful system fallbacks."""
    _fonts: Dict[Tuple[str, int, bool], pygame.font.Font] = {}

    @classmethod
    def get(cls, size: int = 14, bold: bool = False, serif: bool = False) -> pygame.font.Font:
        key = ("serif" if serif else "sans", size, bold)
        if key in cls._fonts:
            return cls._fonts[key]

        font_names = (
            ["georgia", "times new roman", "garamond", "palatino"]
            if serif
            else ["trebuchet ms", "segoe ui", "helvetica", "dejavu sans", "arial"]
        )

        font_obj = None
        for name in font_names:
            try:
                font_obj = pygame.font.SysFont(name, size, bold=bold)
                if font_obj:
                    break
            except Exception:
                continue

        if not font_obj:
            font_obj = pygame.font.Font(None, size)

        cls._fonts[key] = font_obj
        return font_obj


# ==============================================================================
# PROCEDURAL GRAPHICS HELPERS
# ==============================================================================

def create_corkboard_surface(width: int, height: int) -> pygame.Surface:
    """
    Generate a lightweight procedural dark corkboard texture with frame.
    Uses seeded pseudo-random noise for deterministic, flicker-free rendering.
    """
    surf = pygame.Surface((width, height))
    surf.fill(CORK_BASE)

    # Procedural grain specks
    import random
    rng = random.Random(1337)

    speck_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for _ in range((width * height) // 250):
        x = rng.randint(0, width - 1)
        y = rng.randint(0, height - 1)
        radius = rng.choice([1, 1, 2])
        color = rng.choice([CORK_DARK, CORK_SPECK])
        alpha = rng.randint(40, 110)
        pygame.draw.circle(speck_surf, (*color, alpha), (x, y), radius)

    surf.blit(speck_surf, (0, 0))

    # Inner vignette / shadow around board
    shadow_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 90), (0, 0, width, height), width=10)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 50), (10, 10, width - 20, height - 20), width=10)
    surf.blit(shadow_surf, (0, 0))

    # Wood outer border
    pygame.draw.rect(surf, CORK_FRAME, (0, 0, width, height), width=6)
    pygame.draw.rect(surf, (55, 45, 35), (2, 2, width - 4, height - 4), width=1)

    return surf


def draw_pin(surface: pygame.Surface, x: int, y: int, radius: int = 6) -> None:
    """Draw an antique brass push-pin with shadow and specular highlight."""
    # Drop shadow
    shadow_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    pygame.draw.circle(shadow_surf, (0, 0, 0, 110), (radius * 2 + 1, radius * 2 + 2), radius)
    surface.blit(shadow_surf, (x - radius * 2, y - radius * 2))

    # Outer brass rim
    pygame.draw.circle(surface, PIN_SHADOW, (x, y), radius)
    pygame.draw.circle(surface, PIN_BRASS, (x, y), radius - 1)

    # Core head
    pygame.draw.circle(surface, (180, 145, 40), (x, y), radius - 2)

    # Specular shine
    pygame.draw.circle(surface, PIN_HIGHLIGHT, (x - 2, y - 2), max(1, radius // 3))


def draw_curved_string(
    surface: pygame.Surface,
    start_pos: Tuple[int, int],
    end_pos: Tuple[int, int],
    is_active: bool = False,
    pulse_phase: float = 0.0
) -> None:
    """
    Draw a taut or slightly sagging investigation string connecting two evidence pins.
    If active, draws with an illuminated pulsating glow effect.
    """
    x1, y1 = start_pos
    x2, y2 = end_pos

    # Midpoint with subtle gravity sag
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    dx = x2 - x1
    dy = y2 - y1
    dist = math.hypot(dx, dy)
    sag = min(22.0, max(6.0, dist * 0.035))
    ctrl_y = mid_y + sag

    # Sample quadratic Bezier curve
    steps = max(10, int(dist // 18))
    points: List[Tuple[float, float]] = []
    for step in range(steps + 1):
        t = step / steps
        # B(t) = (1-t)^2 P0 + 2(1-t)t P1 + t^2 P2
        bx = (1 - t) * (1 - t) * x1 + 2 * (1 - t) * t * mid_x + t * t * x2
        by = (1 - t) * (1 - t) * y1 + 2 * (1 - t) * t * ctrl_y + t * t * y2
        points.append((int(bx), int(by)))

    if len(points) < 2:
        return

    if is_active:
        # Pulsing illumination
        glow_alpha = int(140 + 70 * math.sin(pulse_phase * 4))
        glow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.lines(glow_surf, (*STRING_GLOW, glow_alpha), False, points, 5)
        surface.blit(glow_surf, (0, 0))
        # Inner active line
        pygame.draw.lines(surface, STRING_ACTIVE, False, points, 2)
    else:
        # Subtle shadow underneath string
        shadow_points = [(p[0] + 1, p[1] + 2) for p in points]
        shadow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.lines(shadow_surf, (0, 0, 0, 75), False, shadow_points, 2)
        surface.blit(shadow_surf, (0, 0))

        # Main string line
        pygame.draw.lines(surface, STRING_NORMAL, False, points, 2)


def draw_suspect_silhouette(
    surface: pygame.Surface,
    rect: pygame.Rect,
    avatar_type: str,
    color: Tuple[int, int, int] = CARD_TEXT_MAIN
) -> None:
    """
    Procedurally draws distinct noir suspect silhouettes using geometric Pygame shapes.
    - contractor (Oliver Reed): flat cap, wide jaw, work collar
    - archivist (Evelyn Shaw): neat hair bun, glasses, collared blouse
    - guard (Marcus Vale): peaked security officer visor cap, broad shoulders, badge
    - curator (Dr. Lena Hart): wavy coiffed hair, blazer lapels, pendant
    """
    cx, cy = rect.centerx, rect.centery
    w, h = rect.width, rect.height

    # Background oval vignette
    bg_color = (220, 212, 195)
    pygame.draw.ellipse(surface, bg_color, rect)
    pygame.draw.ellipse(surface, (170, 160, 145), rect, width=1)

    if avatar_type == "contractor":
        # Flat workman cap
        cap_rect = pygame.Rect(cx - w * 0.28, cy - h * 0.38, w * 0.56, h * 0.22)
        pygame.draw.ellipse(surface, color, cap_rect)
        # Cap brim visor
        pygame.draw.line(surface, color, (cx - w * 0.32, cy - h * 0.20), (cx + w * 0.34, cy - h * 0.20), 3)
        # Face / jaw
        pygame.draw.circle(surface, color, (cx, cy - int(h * 0.10)), int(w * 0.18))
        # Broad workman shoulders & collar
        shoulder_pts = [
            (cx - w * 0.38, cy + h * 0.45),
            (cx - w * 0.25, cy + h * 0.12),
            (cx, cy + h * 0.18),
            (cx + w * 0.25, cy + h * 0.12),
            (cx + w * 0.38, cy + h * 0.45),
        ]
        pygame.draw.polygon(surface, color, shoulder_pts)

    elif avatar_type == "archivist":
        # Neat bun on top
        pygame.draw.circle(surface, color, (cx, cy - int(h * 0.34)), int(w * 0.12))
        # Head
        pygame.draw.circle(surface, color, (cx, cy - int(h * 0.15)), int(w * 0.18))
        # Eyeglasses (subtle light circles)
        eye_y = cy - int(h * 0.16)
        pygame.draw.circle(surface, (245, 239, 225), (cx - 7, eye_y), 4, width=1)
        pygame.draw.circle(surface, (245, 239, 225), (cx + 7, eye_y), 4, width=1)
        pygame.draw.line(surface, (245, 239, 225), (cx - 3, eye_y), (cx + 3, eye_y), 1)
        # Shoulders
        shoulder_pts = [
            (cx - w * 0.32, cy + h * 0.45),
            (cx - w * 0.18, cy + h * 0.14),
            (cx, cy + h * 0.18),
            (cx + w * 0.18, cy + h * 0.14),
            (cx + w * 0.32, cy + h * 0.45),
        ]
        pygame.draw.polygon(surface, color, shoulder_pts)

    elif avatar_type == "guard":
        # Peaked security guard cap
        cap_pts = [
            (cx - int(w * 0.26), cy - int(h * 0.24)),
            (cx - int(w * 0.22), cy - int(h * 0.40)),
            (cx + int(w * 0.22), cy - int(h * 0.40)),
            (cx + int(w * 0.26), cy - int(h * 0.24)),
        ]
        pygame.draw.polygon(surface, color, cap_pts)
        # Visor
        pygame.draw.arc(surface, color, (cx - w * 0.28, cy - h * 0.26, w * 0.56, h * 0.14), 0, math.pi, 3)
        # Head
        pygame.draw.circle(surface, color, (cx, cy - int(h * 0.10)), int(w * 0.18))
        # Guard uniform shoulders & star badge
        shoulder_pts = [
            (cx - w * 0.40, cy + h * 0.45),
            (cx - w * 0.28, cy + h * 0.10),
            (cx, cy + h * 0.16),
            (cx + w * 0.28, cy + h * 0.10),
            (cx + w * 0.40, cy + h * 0.45),
        ]
        pygame.draw.polygon(surface, color, shoulder_pts)
        # Small gold badge pin
        pygame.draw.circle(surface, PIN_BRASS, (cx - 10, cy + int(h * 0.26)), 3)

    else:  # curator (Dr. Lena Hart)
        # Elegant coiffed hair volume
        pygame.draw.ellipse(surface, color, (cx - w * 0.26, cy - h * 0.38, w * 0.52, h * 0.36))
        # Head
        pygame.draw.circle(surface, color, (cx, cy - int(h * 0.12)), int(w * 0.17))
        # Hair curls on side
        pygame.draw.circle(surface, color, (cx - int(w * 0.20), cy - int(h * 0.18)), int(w * 0.10))
        pygame.draw.circle(surface, color, (cx + int(w * 0.20), cy - int(h * 0.18)), int(w * 0.10))
        # Blazer shoulders and V-neck
        shoulder_pts = [
            (cx - w * 0.35, cy + h * 0.45),
            (cx - w * 0.20, cy + h * 0.12),
            (cx, cy + h * 0.24),
            (cx + w * 0.20, cy + h * 0.12),
            (cx + w * 0.35, cy + h * 0.45),
        ]
        pygame.draw.polygon(surface, color, shoulder_pts)
        # Small pendant
        pygame.draw.circle(surface, PIN_BRASS, (cx, cy + int(h * 0.26)), 2)
