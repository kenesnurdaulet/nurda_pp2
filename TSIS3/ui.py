import pygame
from persistence import load_lb

# ── Colors ────────────────────────────────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
YELLOW = (255, 215, 0)
RED    = (220, 50,  50)
GREEN  = (50,  200, 80)
GRAY   = (160, 160, 160)
ORANGE = (255, 140, 0)
CYAN   = (0,   200, 230)
DARK   = (30,  30,  50)


# ── Base helpers ──────────────────────────────────────────────────────────────
def draw_text(surf, msg, size, x, y, color=WHITE, bold=False, center=True):
    f = pygame.font.SysFont("Arial", size, bold=bold)
    img = f.render(msg, True, color)
    r = img.get_rect()
    if center:
        r.centerx = x
    else:
        r.x = x
    r.y = y
    surf.blit(img, r)


def draw_button(surf, msg, cx, cy, w=180, h=44, col=DARK):
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    pygame.draw.rect(surf, col, r, border_radius=8)
    pygame.draw.rect(surf, GRAY, r, 2, border_radius=8)
    f = pygame.font.SysFont("Arial", 22, bold=True)
    img = f.render(msg, True, WHITE)
    surf.blit(img, img.get_rect(center=r.center))
    return r


def was_clicked(rect, event):
    return event.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(event.pos)


# ── Screens ───────────────────────────────────────────────────────────────────
def draw_menu(screen, W):
    screen.fill(DARK)
    draw_text(screen, "RACER",  54, W // 2, 90,  YELLOW, bold=True)
    draw_text(screen, "TSIS 3", 20, W // 2, 150, GRAY)
    b1 = draw_button(screen, "Play",        W // 2, 240, col=(40, 110, 40))
    b2 = draw_button(screen, "Leaderboard", W // 2, 300, col=(50, 70, 130))
    b3 = draw_button(screen, "Settings",    W // 2, 360, col=(70, 50, 100))
    b4 = draw_button(screen, "Quit",        W // 2, 420, col=(110, 35, 35))
    return b1, b2, b3, b4


def draw_username(screen, W, txt):
    screen.fill(DARK)
    draw_text(screen, "Enter Your Name", 30, W // 2, 195, YELLOW, bold=True)
    box = pygame.Rect(W // 2 - 120, 240, 240, 42)
    pygame.draw.rect(screen, (55, 55, 75), box, border_radius=6)
    pygame.draw.rect(screen, GRAY, box, 2, border_radius=6)
    draw_text(screen, txt + "|", 24, box.centerx, box.y + 10)
    b1 = draw_button(screen, "Start", W // 2, 325, col=(40, 110, 40))
    b2 = draw_button(screen, "Back",  W // 2, 380, col=(90, 50, 50))
    return b1, b2


def draw_gameover(screen, W, res, fin):
    screen.fill((12, 8, 18))
    title = "FINISHED!" if fin else "GAME OVER"
    draw_text(screen, title, 40, W // 2, 115, GREEN if fin else RED, bold=True)
    draw_text(screen, f"Score:    {res['score']}",  22, W // 2, 205)
    draw_text(screen, f"Distance: {res['dist']}m",  22, W // 2, 240)
    draw_text(screen, f"Coins:    {res['coins']}",  22, W // 2, 275, YELLOW)
    b1 = draw_button(screen, "Retry",     W // 2, 355, col=(40, 110, 40))
    b2 = draw_button(screen, "Main Menu", W // 2, 415, col=(50, 70, 130))
    return b1, b2


def draw_leaderboard(screen, W):
    screen.fill(DARK)
    draw_text(screen, "Leaderboard", 34, W // 2, 35, YELLOW, bold=True)
    pygame.draw.line(screen, GRAY, (20, 75), (W - 20, 75))
    entries = load_lb()
    if not entries:
        draw_text(screen, "No scores yet!", 22, W // 2, 200, GRAY)
    for i, e in enumerate(entries[:10]):
        y = 88 + i * 44
        col = [YELLOW, (200, 200, 200), (180, 100, 40)][i] if i < 3 else WHITE
        draw_text(screen, f"{i+1}.", 18, 28,  y, col, center=False)
        draw_text(screen, e["name"][:12], 18, 65,  y, col, center=False)
        draw_text(screen, str(e["score"]), 18, 255, y, col, center=False)
        draw_text(screen, f"{e['dist']}m",  18, 315, y, col, center=False)
    b = draw_button(screen, "Back", W // 2, 590, col=(50, 70, 130))
    return b


def draw_settings(screen, W, cfg):
    screen.fill(DARK)
    draw_text(screen, "Settings", 34, W // 2, 50, YELLOW, bold=True)
    draw_text(screen, "Difficulty:", 22, W // 2, 135)
    diffs = ["easy", "normal", "hard"]
    diff_btns = []
    for i, d in enumerate(diffs):
        col = (40, 130, 40) if cfg["difficulty"] == d else (60, 60, 80)
        r = draw_button(screen, d.capitalize(), 70 + i * 120, 180, w=110, h=40, col=col)
        diff_btns.append((r, d))
    b_back = draw_button(screen, "Save & Back", W // 2, 270, col=(50, 70, 130))
    return diff_btns, b_back