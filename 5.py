"""
paint.py — Main entry point for the Paint application (TSIS 2).
 
Controls
--------
  Left-click + drag : Use the active tool
  1 / 2 / 3         : Switch brush size (small / medium / large)
  Ctrl + S          : Save canvas as timestamped PNG
  Escape            : Cancel text input (or deselect start point for line tool)
 
Tools available in the toolbar:
  Pencil, Line, Rectangle, Square, Circle,
  Right Triangle, Equilateral Triangle, Rhombus,
  Eraser, Fill, Text
"""
 
import pygame
import sys
import datetime
import os
 
from tools import (
    BRUSH_SIZES, BRUSH_LABELS,
    draw_pencil, draw_line, draw_line_preview,
    draw_eraser, draw_rectangle, draw_square,
    draw_circle, draw_right_triangle,
    draw_equilateral_triangle, draw_rhombus,
    flood_fill, render_text_cursor, commit_text,
    draw_shape_preview,
)
 
# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
WINDOW_W  = 1100
WINDOW_H  = 700
TOOLBAR_W = 160          # left toolbar width
CANVAS_X  = TOOLBAR_W
CANVAS_W  = WINDOW_W - TOOLBAR_W
CANVAS_H  = WINDOW_H
 
BG_COLOR      = (255, 255, 255)   # canvas background (white)
TOOLBAR_BG    = (40,  40,  40)    # toolbar background (dark grey)
BTN_COLOR     = (70,  70,  70)    # default button fill
BTN_ACTIVE    = (200, 140,  50)   # highlighted button (active tool)
BTN_HOVER     = (90,  90,  90)    # hover state
TEXT_COLOR    = (240, 240, 240)   # toolbar label text
SEPARATOR_COL = (60,  60,  60)    # divider lines
 
# Palette — 20 colors shown as small swatches at the bottom of the toolbar
PALETTE = [
    (0,   0,   0),   (255, 255, 255), (128, 128, 128), (192, 192, 192),
    (255,   0,   0), (128,   0,   0), (255, 165,   0), (255, 255,   0),
    (0,   255,   0), (0,   128,   0), (0,   255, 255), (0,     0, 255),
    (0,     0, 128), (128,   0, 128), (255,   0, 255), (255, 182, 193),
    (139,  69,  19), (255, 140,   0), (75,    0, 130), (255, 215,   0),
]
 
# Tool definitions: (display_label, internal_key)
TOOLS = [
    ("Pencil",     "pencil"),
    ("Line",       "line"),
    ("Rectangle",  "rectangle"),
    ("Square",     "square"),
    ("Circle",     "circle"),
    ("Rt Triangle","right_triangle"),
    ("Eq Triangle","equilateral_triangle"),
    ("Rhombus",    "rhombus"),
    ("Eraser",     "eraser"),
    ("Fill",       "fill"),
    ("Text",       "text"),
]
 
 
# ---------------------------------------------------------------------------
# Helper: draw a rounded button
# ---------------------------------------------------------------------------
def draw_button(surface, rect, label, font, active=False, hover=False):
    """Render a toolbar button with optional active/hover highlight."""
    color = BTN_ACTIVE if active else (BTN_HOVER if hover else BTN_COLOR)
    pygame.draw.rect(surface, color, rect, border_radius=6)
    pygame.draw.rect(surface, (100, 100, 100), rect, 1, border_radius=6)
    text_surf = font.render(label, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
 
 
# ---------------------------------------------------------------------------
# Helper: build button rects for the toolbar
# ---------------------------------------------------------------------------
def build_tool_rects():
    """Return a list of pygame.Rect objects, one per tool, stacked vertically."""
    rects = []
    btn_w, btn_h = TOOLBAR_W - 16, 32
    x = 8
    y = 36   # leave room for the section title
    for _ in TOOLS:
        rects.append(pygame.Rect(x, y, btn_w, btn_h))
        y += btn_h + 4
    return rects
 
 
def build_size_rects(start_y):
    """Three brush-size buttons placed side-by-side below the tool list."""
    rects = []
    btn_w = (TOOLBAR_W - 16) // 3
    for i in range(3):
        rects.append(pygame.Rect(8 + i * (btn_w + 2), start_y, btn_w, 26))
    return rects
 
 
def build_palette_rects(start_y):
    """20-color palette as a 4-column grid of swatches."""
    rects = []
    swatch = 28
    cols   = 4
    gap    = 4
    for i, _ in enumerate(PALETTE):
        col = i % cols
        row = i // cols
        x = 8 + col * (swatch + gap)
        y = start_y + row * (swatch + gap)
        rects.append(pygame.Rect(x, y, swatch, swatch))
    return rects
 
 
# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------
def main():
    pygame.init()
    pygame.display.set_caption("Paint — TSIS 2")
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock  = pygame.time.Clock()
 
    # --- Fonts ---
    ui_font   = pygame.font.SysFont("segoeui",    13)
    label_font= pygame.font.SysFont("segoeui",    11)
    text_font = pygame.font.SysFont("segoeui",    20)  # text tool
 
    # --- Canvas surface (drawing target) ---
    canvas = pygame.Surface((CANVAS_W, CANVAS_H))
    canvas.fill(BG_COLOR)
 
    # --- Build toolbar layout ---
    tool_rects   = build_tool_rects()
    # place size buttons just below the last tool button
    size_y       = tool_rects[-1].bottom + 12
    size_rects   = build_size_rects(size_y)
    # palette below size buttons
    palette_y    = size_rects[0].bottom + 12
    palette_rects= build_palette_rects(palette_y)
    # colour preview swatch (shows active colour)
    preview_rect = pygame.Rect(8, palette_rects[-1].bottom + 10, TOOLBAR_W - 16, 30)
 
    # --- State ---
    active_tool   = "pencil"
    brush_size_idx= 0               # index into BRUSH_SIZES
    active_color  = (0, 0, 0)       # current drawing colour
 
    drawing       = False           # mouse button is held
    prev_pos      = None            # previous mouse position (pencil)
    drag_start    = None            # start of drag (shapes / line)
 
    # Text-tool state
    text_active   = False
    text_pos      = None            # where typing started
    typed_text    = ""
 
    # ---------------------------------------------------------------------------
    # Main loop
    # ---------------------------------------------------------------------------
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        # Map screen coords → canvas coords
        canvas_mouse = (mouse_pos[0] - CANVAS_X, mouse_pos[1])
        on_canvas = mouse_pos[0] >= CANVAS_X
 
        brush = BRUSH_SIZES[brush_size_idx]
 
        # ---- Event processing ----
        for event in pygame.event.get():
 
            # Quit
            if event.type == pygame.QUIT:
                running = False
 
            # ---- Keyboard ----
            elif event.type == pygame.KEYDOWN:
 
                # Text tool — accumulate typed characters
                if text_active:
                    if event.key == pygame.K_RETURN:
                        # Commit text permanently to canvas
                        commit_text(canvas, text_font, typed_text,
                                    text_pos, active_color)
                        text_active = False
                        typed_text  = ""
                        text_pos    = None
                    elif event.key == pygame.K_ESCAPE:
                        # Cancel without committing
                        text_active = False
                        typed_text  = ""
                        text_pos    = None
                    elif event.key == pygame.K_BACKSPACE:
                        typed_text = typed_text[:-1]
                    else:
                        # Append printable characters
                        if event.unicode and event.unicode.isprintable():
                            typed_text += event.unicode
                else:
                    # Brush-size shortcuts
                    if event.key == pygame.K_1:
                        brush_size_idx = 0
                    elif event.key == pygame.K_2:
                        brush_size_idx = 1
                    elif event.key == pygame.K_3:
                        brush_size_idx = 2
 
                    # Ctrl+S → save
                    elif (event.key == pygame.K_s
                          and pygame.key.get_mods() & pygame.KMOD_CTRL):
                        timestamp = datetime.datetime.now().strftime(
                            "%Y%m%d_%H%M%S")
                        filename = f"canvas_{timestamp}.png"
                        pygame.image.save(canvas, filename)
                        print(f"[Saved] {filename}")  # console confirmation
 
                    # Escape cancels line start-point selection
                    elif event.key == pygame.K_ESCAPE:
                        drag_start = None
 
            # ---- Mouse button DOWN ----
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Clicked inside toolbar?
                if mouse_pos[0] < CANVAS_X:
                    # Tool buttons
                    for i, rect in enumerate(tool_rects):
                        if rect.collidepoint(mouse_pos):
                            active_tool = TOOLS[i][1]
                            # Switching tool cancels active text input
                            if active_tool != "text":
                                text_active = False
                                typed_text  = ""
                                text_pos    = None
                    # Brush size buttons
                    for i, rect in enumerate(size_rects):
                        if rect.collidepoint(mouse_pos):
                            brush_size_idx = i
                    # Palette swatches
                    for i, rect in enumerate(palette_rects):
                        if rect.collidepoint(mouse_pos):
                            active_color = PALETTE[i]
 
                # Clicked on canvas
                else:
                    cp = canvas_mouse  # canvas-space position
 
                    if active_tool == "fill":
                        flood_fill(canvas, cp, active_color)
 
                    elif active_tool == "text":
                        # Start or reposition text cursor
                        if text_active:
                            # Commit whatever was typed so far at old position
                            commit_text(canvas, text_font, typed_text,
                                        text_pos, active_color)
                        text_active = True
                        text_pos    = cp
                        typed_text  = ""
 
                    elif active_tool == "pencil":
                        drawing  = True
                        prev_pos = cp
 
                    elif active_tool == "eraser":
                        drawing  = True
                        draw_eraser(canvas, cp, BG_COLOR, brush)
                        prev_pos = cp
 
                    else:
                        # Shape / line tools: record drag start
                        drawing    = True
                        drag_start = cp
 
            # ---- Mouse MOTION ----
            elif event.type == pygame.MOUSEMOTION:
                if drawing and on_canvas:
                    cp = canvas_mouse
 
                    if active_tool == "pencil":
                        draw_pencil(canvas, prev_pos, cp, active_color, brush)
                        prev_pos = cp
 
                    elif active_tool == "eraser":
                        draw_eraser(canvas, cp, BG_COLOR, brush)
                        prev_pos = cp
 
                    # Shape/line tools: preview drawn each frame (see render step)
 
            # ---- Mouse button UP ----
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and on_canvas:
                    cp = canvas_mouse
 
                    # Commit shape / line to canvas
                    shape_tools = {
                        "line":               draw_line,
                        "rectangle":          draw_rectangle,
                        "square":             draw_square,
                        "circle":             draw_circle,
                        "right_triangle":     draw_right_triangle,
                        "equilateral_triangle": draw_equilateral_triangle,
                        "rhombus":            draw_rhombus,
                    }
                    if active_tool in shape_tools and drag_start:
                        shape_tools[active_tool](
                            canvas, drag_start, cp, active_color, brush)
                        drag_start = None
 
                drawing  = False
                prev_pos = None
 
        # ---- Rendering ----
        screen.fill((20, 20, 20))
 
        # 1. Canvas (with live shape preview on top)
        screen.blit(canvas, (CANVAS_X, 0))
 
        # 2. Shape preview while dragging
        preview_tools = {
            "line", "rectangle", "square", "circle",
            "right_triangle", "equilateral_triangle", "rhombus"
        }
        if drawing and active_tool in preview_tools and drag_start and on_canvas:
            # Blit a temporary overlay for the preview line/shape
            preview_surf = canvas.copy()
            draw_shape_preview(
                preview_surf, active_tool,
                drag_start, canvas_mouse,
                active_color, brush
            )
            screen.blit(preview_surf, (CANVAS_X, 0))
 
        # 3. Text cursor preview
        if text_active and text_pos:
            # Overlay on the screen (not committed to canvas yet)
            render_text_cursor(screen, text_font, typed_text,
                               (text_pos[0] + CANVAS_X, text_pos[1]),
                               active_color)
 
        # 4. Eraser cursor outline
        if active_tool == "eraser" and on_canvas:
            esize = brush * 6
            er = pygame.Rect(
                mouse_pos[0] - esize // 2,
                mouse_pos[1] - esize // 2,
                esize, esize
            )
            pygame.draw.rect(screen, (180, 0, 0), er, 1)
 
        # ---- Toolbar ----
        pygame.draw.rect(screen, TOOLBAR_BG,
                         pygame.Rect(0, 0, TOOLBAR_W, WINDOW_H))
 
        # Section: Tools
        t = ui_font.render("TOOLS", True, (160, 160, 160))
        screen.blit(t, (8, 14))
        for i, (label, key) in enumerate(TOOLS):
            hover  = tool_rects[i].collidepoint(mouse_pos)
            active = (active_tool == key)
            draw_button(screen, tool_rects[i], label, label_font, active, hover)
 
        # Separator
        sy = size_y - 8
        pygame.draw.line(screen, SEPARATOR_COL, (8, sy), (TOOLBAR_W - 8, sy))
 
        # Section: Brush Size
        t = label_font.render("BRUSH  (1/2/3)", True, (160, 160, 160))
        screen.blit(t, (8, size_y - 8))
        for i, rect in enumerate(size_rects):
            hover  = rect.collidepoint(mouse_pos)
            active = (brush_size_idx == i)
            draw_button(screen, rect,
                        f"{BRUSH_LABELS[i]} ({BRUSH_SIZES[i]}px)",
                        label_font, active, hover)
 
        # Separator
        py = palette_y - 8
        pygame.draw.line(screen, SEPARATOR_COL, (8, py), (TOOLBAR_W - 8, py))
 
        # Section: Palette
        t = label_font.render("COLOR", True, (160, 160, 160))
        screen.blit(t, (8, palette_y - 8))
        for i, rect in enumerate(palette_rects):
            pygame.draw.rect(screen, PALETTE[i], rect)
            # White border for white swatch so it's visible
            border_col = (120, 120, 120) if PALETTE[i] == (255, 255, 255) else PALETTE[i]
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)
            # Highlight active colour
            if PALETTE[i] == active_color:
                pygame.draw.rect(screen, (255, 200, 50), rect, 2)
 
        # Active colour preview
        pygame.draw.rect(screen, active_color, preview_rect)
        pygame.draw.rect(screen, (200, 200, 200), preview_rect, 1)
 
        # Save hint at very bottom
        hint = label_font.render("Ctrl+S  to save", True, (100, 100, 100))
        screen.blit(hint, (8, WINDOW_H - 20))
 
        # ---- Canvas border ----
        pygame.draw.rect(screen, (80, 80, 80),
                         pygame.Rect(CANVAS_X - 1, -1, CANVAS_W + 1, WINDOW_H + 1), 1)
 
        pygame.display.flip()
        clock.tick(60)
 
    pygame.quit()
    sys.exit()
 
 
if __name__ == "__main__":
    main()