"""
TSIS 3 — Racer Game
Controls: LEFT / RIGHT arrows (or A / D)
"""

import pygame
import sys

from racer import Game, load_images, W, H
from ui import (was_clicked, draw_menu, draw_username,
                draw_gameover, draw_leaderboard, draw_settings)
from persistence import load_settings, save_settings, save_lb

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Racer TSIS 3")
clock = pygame.time.Clock()

load_images()   # must be called after pygame.init()

# ── Scene constants ───────────────────────────────────────────────────────────
MENU, UNAME, PLAY, OVER, LB, SET = "menu", "uname", "play", "over", "lb", "set"

# ── State ─────────────────────────────────────────────────────────────────────
state    = MENU
settings = load_settings()
game     = None
result   = {}
username = ""
uinput   = ""

# ── Main loop ─────────────────────────────────────────────────────────────────
while True:
    events = pygame.event.get()
    for ev in events:
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # ── Main Menu ─────────────────────────────────────────────────────────────
    if state == MENU:
        b1, b2, b3, b4 = draw_menu(screen, W)
        for ev in events:
            if was_clicked(b1, ev): state = UNAME; uinput = ""
            if was_clicked(b2, ev): state = LB
            if was_clicked(b3, ev): state = SET
            if was_clicked(b4, ev): pygame.quit(); sys.exit()

    # ── Username entry ────────────────────────────────────────────────────────
    elif state == UNAME:
        b1, b2 = draw_username(screen, W, uinput)
        for ev in events:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_BACKSPACE:
                    uinput = uinput[:-1]
                elif ev.key == pygame.K_RETURN and uinput.strip():
                    username = uinput.strip()
                    game = Game(settings["difficulty"])
                    state = PLAY
                elif len(uinput) < 14:
                    uinput += ev.unicode
            if was_clicked(b1, ev) and uinput.strip():
                username = uinput.strip()
                game = Game(settings["difficulty"])
                state = PLAY
            if was_clicked(b2, ev):
                state = MENU

    # ── Gameplay ──────────────────────────────────────────────────────────────
    elif state == PLAY:
        for ev in events:
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_LEFT,  pygame.K_a): game.player.move(-1)
                if ev.key in (pygame.K_RIGHT, pygame.K_d): game.player.move(1)
                if ev.key == pygame.K_ESCAPE:
                    result = {"score": game.score,
                              "dist":  int(game.distance),
                              "coins": game.coin_count}
                    save_lb(username, result["score"], result["dist"])
                    state = OVER

        game.update()
        game.draw(screen)

        if not game.alive or game.finished:
            result = {"score": game.score,
                      "dist":  int(game.distance),
                      "coins": game.coin_count}
            save_lb(username, result["score"], result["dist"])
            state = OVER

    # ── Game Over ─────────────────────────────────────────────────────────────
    elif state == OVER:
        fin = game and game.finished
        b1, b2 = draw_gameover(screen, W, result, fin)
        for ev in events:
            if was_clicked(b1, ev):
                game = Game(settings["difficulty"])
                state = PLAY
            if was_clicked(b2, ev):
                state = MENU

    # ── Leaderboard ───────────────────────────────────────────────────────────
    elif state == LB:
        b = draw_leaderboard(screen, W)
        for ev in events:
            if was_clicked(b, ev): state = MENU

    # ── Settings ──────────────────────────────────────────────────────────────
    elif state == SET:
        diff_btns, b_back = draw_settings(screen, W, settings)
        for ev in events:
            for r, d in diff_btns:
                if was_clicked(r, ev):
                    settings["difficulty"] = d
            if was_clicked(b_back, ev):
                save_settings(settings)
                state = MENU

    pygame.display.flip()
    clock.tick(60)