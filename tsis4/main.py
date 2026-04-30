# main.py
import sys
import pygame
import db
import settings as S
from game import Game
from config import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock  = pygame.time.Clock()

FL = pygame.font.SysFont("monospace", 48, bold=True)
FM = pygame.font.SysFont("monospace", 28, bold=True)
FS = pygame.font.SysFont("monospace", 20)
FSB= pygame.font.SysFont("monospace", 20, bold=True)

def txt(text, font, color, y, x=None):
    s = font.render(text, True, color)
    if x is None: x = WIDTH//2 - s.get_width()//2
    screen.blit(s, (x, y))

def btn_rect(y, w=200, h=42):
    return pygame.Rect(WIDTH//2 - w//2, y, w, h)

def draw_btn(rect, label, hover=False, color=GREEN):
    c = tuple(min(v+40,255) for v in color) if hover else color
    pygame.draw.rect(screen, c, rect, border_radius=7)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=7)
    s = FSB.render(label, True, WHITE)
    screen.blit(s, (rect.centerx-s.get_width()//2, rect.centery-s.get_height()//2))


# ── Username screen ───────────────────────────────────────────────────────────
def screen_username():
    name = ""; error = ""; cursor = True; ct = 0
    box  = pygame.Rect(WIDTH//2-140, 240, 280, 44)
    ok   = btn_rect(310)
    while True:
        dt = clock.tick(30); ct += dt
        if ct > 500: cursor = not cursor; ct = 0
        m = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    if name.strip(): return name.strip()
                    error = "Enter a username!"
                elif e.key == pygame.K_BACKSPACE: name = name[:-1]
                elif len(name)<20 and e.unicode.isprintable(): name += e.unicode
            if e.type == pygame.MOUSEBUTTONDOWN:
                if ok.collidepoint(m):
                    if name.strip(): return name.strip()
                    error = "Enter a username!"
        screen.fill(BLACK)
        txt("SNAKE", FL, GREEN, 100)
        txt("Enter username:", FM, LIGHT_GRAY, 195)
        pygame.draw.rect(screen, GRAY, box, border_radius=6)
        pygame.draw.rect(screen, GREEN if name else GRAY, box, 2, border_radius=6)
        s = FM.render(name+( "|" if cursor else " "), True, WHITE)
        screen.blit(s, (box.x+8, box.centery-s.get_height()//2))
        draw_btn(ok, "Start", ok.collidepoint(m))
        if error: txt(error, FS, RED, 370)
        pygame.display.flip()


# ── Main menu ─────────────────────────────────────────────────────────────────
def screen_menu(username):
    btns = [("Play", btn_rect(220)), ("Leaderboard", btn_rect(275)),
            ("Settings", btn_rect(330)), ("Quit", btn_rect(385))]
    while True:
        clock.tick(30); m = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "quit"
            if e.type == pygame.MOUSEBUTTONDOWN:
                for label, r in btns:
                    if r.collidepoint(m): return label.lower()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return "quit"
        screen.fill(BLACK)
        txt("SNAKE", FL, GREEN, 100)
        txt(f"Hi, {username}!", FM, CYAN, 165)
        for label, r in btns:
            draw_btn(r, label, r.collidepoint(m))
        pygame.display.flip()


# ── Gameplay ──────────────────────────────────────────────────────────────────
def screen_play(settings, player_id):
    game = Game(settings["snake_color"], settings["grid"], settings["sound"])
    if player_id: game.best = db.get_best(player_id)
    tick = 0
    while True:
        dt = clock.tick(60); tick += dt
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                from game import UP,DOWN,LEFT,RIGHT
                keys = {pygame.K_UP:UP, pygame.K_w:UP, pygame.K_DOWN:DOWN,
                        pygame.K_s:DOWN, pygame.K_LEFT:LEFT, pygame.K_a:LEFT,
                        pygame.K_RIGHT:RIGHT, pygame.K_d:RIGHT}
                if e.key in keys:
                    from game import OPPOSITE
                    nd = keys[e.key]
                    if nd != OPPOSITE.get(game.dir): game.dir = nd
                if e.key == pygame.K_ESCAPE:
                    return game.score, game.level
        if tick >= 1000 // game.get_fps():
            tick = 0
            if game.update() == "dead":
                return game.score, game.level
        game.draw(screen)
        pygame.display.flip()


# ── Game over ─────────────────────────────────────────────────────────────────
def screen_gameover(score, level, best):
    retry = btn_rect(370); menu = btn_rect(425)
    while True:
        clock.tick(30); m = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if retry.collidepoint(m): return "retry"
                if menu.collidepoint(m):  return "menu"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return "retry"
                if e.key == pygame.K_ESCAPE: return "menu"
        screen.fill(BLACK)
        txt("GAME OVER", FL, RED, 120)
        txt(f"Score : {score}",     FM, WHITE,  220)
        txt(f"Level : {level}",     FM, YELLOW, 265)
        txt(f"Best  : {max(score,best)}", FM, CYAN, 310)
        draw_btn(retry, "Retry",    retry.collidepoint(m))
        draw_btn(menu,  "Main Menu", menu.collidepoint(m), GRAY)
        pygame.display.flip()


# ── Leaderboard ───────────────────────────────────────────────────────────────
def screen_leaderboard():
    rows = db.get_top10()
    back = btn_rect(HEIGHT-55)
    while True:
        clock.tick(30); m = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if back.collidepoint(m): return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return
        screen.fill(BLACK)
        txt("LEADERBOARD", FL, YELLOW, 30)
        heads = ["#","Player","Score","Lvl","Date"]
        xs    = [30,70,200,320,390]
        y0    = 105
        for x,h in zip(xs, heads):
            screen.blit(FSB.render(h,True,CYAN),(x,y0))
        pygame.draw.line(screen,GRAY,(30,y0+26),(WIDTH-30,y0+26))
        if not rows:
            txt("No scores yet!", FM, GRAY, 200)
        for rank,user,score,level,date in rows:
            y = y0+34+(rank-1)*30
            c = YELLOW if rank==1 else WHITE
            for x,v in zip(xs,[str(rank),user[:12],str(score),str(level),date]):
                screen.blit(FS.render(v,True,c),(x,y))
        draw_btn(back, "Back", back.collidepoint(m), GRAY)
        pygame.display.flip()


# ── Settings ──────────────────────────────────────────────────────────────────
COLORS = [("Green",(50,200,50)),("Blue",(50,100,220)),("Orange",(230,130,30)),
          ("Pink",(220,80,150)),("Cyan",(50,200,200)),("Purple",(150,50,200))]

def screen_settings(settings):
    s    = dict(settings)
    clist= [c for _,c in COLORS]; clbls=[n for n,_ in COLORS]
    try:   ci = clist.index(tuple(s["snake_color"]))
    except:ci = 0
    grid_r  = btn_rect(200); sound_r = btn_rect(260)
    prev_r  = pygame.Rect(WIDTH//2-150,330,44,44)
    swatch  = pygame.Rect(WIDTH//2-36, 330,72,44)
    next_r  = pygame.Rect(WIDTH//2+106,330,44,44)
    back    = btn_rect(HEIGHT-55)
    while True:
        clock.tick(30); m = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if grid_r.collidepoint(m):  s["grid"]  = not s["grid"]
                if sound_r.collidepoint(m): s["sound"] = not s["sound"]
                if prev_r.collidepoint(m):  ci=(ci-1)%len(clist)
                if next_r.collidepoint(m):  ci=(ci+1)%len(clist)
                if back.collidepoint(m):
                    s["snake_color"] = list(clist[ci]); S.save(s); return s
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                s["snake_color"] = list(clist[ci]); S.save(s); return s
        screen.fill(BLACK)
        txt("SETTINGS", FL, CYAN, 80)
        draw_btn(grid_r,  f"Grid: {'ON' if s['grid'] else 'OFF'}",  grid_r.collidepoint(m),  GREEN if s["grid"]  else GRAY)
        draw_btn(sound_r, f"Sound: {'ON' if s['sound'] else 'OFF'}", sound_r.collidepoint(m), GREEN if s["sound"] else GRAY)
        txt("Snake Color:", FSB, LIGHT_GRAY, 305)
        pygame.draw.rect(screen, clist[ci], swatch, border_radius=7)
        pygame.draw.rect(screen, WHITE, swatch, 2, border_radius=7)
        cl = FS.render(clbls[ci], True, WHITE)
        screen.blit(cl,(swatch.centerx-cl.get_width()//2, swatch.centery-cl.get_height()//2))
        for r,lbl in [(prev_r,"<"),(next_r,">")]:
            pygame.draw.rect(screen,GRAY,r,border_radius=7)
            ar = FM.render(lbl,True,WHITE)
            screen.blit(ar,(r.centerx-ar.get_width()//2,r.centery-ar.get_height()//2))
        draw_btn(back, "Save & Back", back.collidepoint(m), GRAY)
        pygame.display.flip()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    db_ok    = db.init()
    settings = S.load()
    username = screen_username()
    pid      = db.get_or_create_player(username) if db_ok else None
    state    = "menu"
    result   = {}

    while True:
        if state == "menu":
            action = screen_menu(username)
            if action == "quit":          break
            elif action == "play":        state = "play"
            elif action == "leaderboard": screen_leaderboard()
            elif action == "settings":    settings = screen_settings(settings)

        elif state == "play":
            score, level = screen_play(settings, pid)
            if db_ok and pid: db.save_session(pid, score, level)
            best   = db.get_best(pid) if db_ok and pid else 0
            result = {"score":score,"level":level,"best":best}
            state  = "gameover"

        elif state == "gameover":
            action = screen_gameover(result["score"], result["level"], result["best"])
            state  = "play" if action == "retry" else "menu"

    pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()