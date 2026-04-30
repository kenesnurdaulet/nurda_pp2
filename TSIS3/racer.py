import pygame
import random
import time
import os

# ── Colors ────────────────────────────────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
YELLOW = (255, 215, 0)
RED    = (220, 50,  50)
GREEN  = (50,  200, 80)
ORANGE = (255, 140, 0)
CYAN   = (0,   200, 230)

# ── Screen size & lanes ───────────────────────────────────────────────────────
W, H  = 400, 640
LANES = [60, 160, 260, 360]   # x-centers of 4 lanes

# ── Difficulty presets ────────────────────────────────────────────────────────
DIFF = {
    "easy":   {"speed": 3.5, "t_int": 2.2, "o_int": 3.0},
    "normal": {"speed": 5.0, "t_int": 1.6, "o_int": 2.2},
    "hard":   {"speed": 7.0, "t_int": 1.0, "o_int": 1.4},
}

# ── Load images ───────────────────────────────────────────────────────────────
BASE = os.path.join(os.path.dirname(__file__), "assets")

def _load(name, size):
    img = pygame.image.load(os.path.join(BASE, name)).convert_alpha()
    return pygame.transform.scale(img, size)

# These are set once after pygame.init() is called (done in main.py)
img_player = None
img_enemy  = None
img_street = None
img_coin   = None

def load_images():
    """Call this after pygame.init()."""
    global img_player, img_enemy, img_street, img_coin
    img_player = _load("Player.png", (44, 80))
    img_enemy  = _load("Enemy.png",  (44, 80))
    img_street = _load("Street.png", (W, H))
    img_coin   = _load("Coin.png",   (30, 30))


# ── Helper: draw text ─────────────────────────────────────────────────────────
def _txt(surf, msg, size, x, y, color=WHITE, bold=False, center=True):
    f = pygame.font.SysFont("Arial", size, bold=bold)
    img = f.render(msg, True, color)
    r = img.get_rect()
    if center:
        r.centerx = x
    else:
        r.x = x
    r.y = y
    surf.blit(img, r)


# ── Game objects ──────────────────────────────────────────────────────────────
class Player:
    def __init__(self):
        self.lane      = 1
        self.x         = float(LANES[self.lane])
        self.y         = H - 110.0
        self.shield    = False
        self.nitro     = False
        self.nitro_end = 0

    def move(self, d):
        nl = self.lane + d
        if 0 <= nl <= 3:
            self.lane = nl

    def update(self):
        tx = float(LANES[self.lane])
        self.x += (tx - self.x) * 0.2
        if self.nitro and time.time() > self.nitro_end:
            self.nitro = False

    def rect(self):
        return pygame.Rect(int(self.x) - 22, int(self.y) - 40, 44, 80)

    def draw(self, surf):
        surf.blit(img_player, (int(self.x) - 22, int(self.y) - 40))
        if self.shield:
            pygame.draw.ellipse(surf, CYAN,
                (int(self.x) - 28, int(self.y) - 46, 56, 92), 3)
        if self.nitro:
            pygame.draw.rect(surf, ORANGE,
                (int(self.x) - 26, int(self.y) - 44, 52, 88), 3, border_radius=6)


class Enemy:
    def __init__(self, speed):
        self.lane  = random.randint(0, 3)
        self.x     = float(LANES[self.lane])
        self.y     = -50.0
        self.speed = speed

    def update(self):       self.y += self.speed
    def rect(self):         return pygame.Rect(int(self.x) - 22, int(self.y) - 40, 44, 80)
    def draw(self, surf):   surf.blit(img_enemy, (int(self.x) - 22, int(self.y) - 40))
    def off(self):          return self.y > H + 60


class Coin:
    def __init__(self, speed):
        kinds   = ["bronze", "silver", "gold"]
        weights = [0.6, 0.3, 0.1]
        values  = {"bronze": 1, "silver": 3, "gold": 5}
        tints   = {"bronze": (180, 100, 30, 80), "silver": (200, 200, 200, 80), "gold": None}
        self.lane  = random.randint(0, 3)
        self.x     = float(LANES[self.lane])
        self.y     = -20.0
        self.speed = speed
        self.kind  = random.choices(kinds, weights)[0]
        self.val   = values[self.kind]
        self.tint  = tints[self.kind]

    def update(self):       self.y += self.speed
    def rect(self):         return pygame.Rect(int(self.x) - 15, int(self.y) - 15, 30, 30)
    def off(self):          return self.y > H + 20

    def draw(self, surf):
        surf.blit(img_coin, (int(self.x) - 15, int(self.y) - 15))
        if self.tint:
            ov = pygame.Surface((30, 30), pygame.SRCALPHA)
            ov.fill(self.tint)
            surf.blit(ov, (int(self.x) - 15, int(self.y) - 15))
        if self.kind != "bronze":
            col = (180, 180, 180) if self.kind == "silver" else YELLOW
            _txt(surf, f"+{self.val}", 12, int(self.x), int(self.y) - 20, col)


class Obstacle:
    def __init__(self, speed):
        self.lane  = random.randint(0, 3)
        self.x     = float(LANES[self.lane])
        self.y     = -20.0
        self.speed = speed
        self.kind  = random.choice(["oil", "barrier", "pothole"])

    def update(self):   self.y += self.speed
    def rect(self):     return pygame.Rect(int(self.x) - 30, int(self.y) - 11, 60, 22)
    def off(self):      return self.y > H + 30

    def draw(self, surf):
        r = self.rect()
        if self.kind == "oil":
            pygame.draw.ellipse(surf, (20, 20, 80), r)
            pygame.draw.ellipse(surf, (60, 60, 180), r.inflate(-8, -4), 2)
        elif self.kind == "barrier":
            pygame.draw.rect(surf, ORANGE, r, border_radius=4)
            pygame.draw.rect(surf, WHITE, r, 2, border_radius=4)
        else:  # pothole
            pygame.draw.ellipse(surf, (50, 50, 50), r)
            pygame.draw.ellipse(surf, BLACK, r.inflate(-10, -6))
        lbl = pygame.font.SysFont("Arial", 11, bold=True).render(
            self.kind.upper(), True, WHITE)
        surf.blit(lbl, lbl.get_rect(center=r.center))


class PowerUp:
    KINDS = {
        "nitro":  (ORANGE, "N"),
        "shield": (CYAN,   "S"),
        "repair": (GREEN,  "R"),
    }

    def __init__(self, speed):
        self.kind  = random.choice(list(self.KINDS))
        self.lane  = random.randint(0, 3)
        self.x     = float(LANES[self.lane])
        self.y     = -30.0
        self.speed = speed
        self.born  = time.time()
        self.col, self.sym = self.KINDS[self.kind]

    def update(self):   self.y += self.speed
    def rect(self):     return pygame.Rect(int(self.x) - 20, int(self.y) - 20, 40, 40)
    def off(self):      return self.y > H + 40 or time.time() - self.born > 8

    def draw(self, surf):
        r = self.rect()
        pygame.draw.rect(surf, self.col, r, border_radius=6)
        pygame.draw.rect(surf, WHITE, r, 2, border_radius=6)
        lbl = pygame.font.SysFont("Arial", 20, bold=True).render(self.sym, True, BLACK)
        surf.blit(lbl, lbl.get_rect(center=r.center))
        _txt(surf, self.kind.upper(), 11, int(self.x), int(self.y) + 24, self.col)


# ── Game class ────────────────────────────────────────────────────────────────
class Game:
    FINISH = 3000

    def __init__(self, diff="normal"):
        d = DIFF.get(diff, DIFF["normal"])
        self.base_spd  = d["speed"]
        self.t_int     = d["t_int"]
        self.o_int     = d["o_int"]

        self.player    = Player()
        self.enemies   = []
        self.coins     = []
        self.obstacles = []
        self.powerups  = []

        self.coin_count = 0
        self.score      = 0
        self.distance   = 0.0
        self.crashes    = 0        # max 1 crash allowed (2 lives)
        self.alive      = True
        self.finished   = False

        self.active_pu  = None    # "nitro" | "shield" | None
        self.pu_end     = 0

        self.road_y1 = 0.0         # two road tiles for seamless scroll
        self.road_y2 = float(-H)

        self.t_timer = self.o_timer = self.c_timer = self.p_timer = time.time()

    # ── Speed helpers ─────────────────────────────────────────────────────────
    def current_speed(self):
        prog = min(self.distance / self.FINISH, 1.0)
        s = self.base_spd + prog * self.base_spd * 0.8
        return s * (1.6 if self.player.nitro else 1.0)

    def progress(self):
        return min(self.distance / self.FINISH, 1.0)

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self):
        if not self.alive or self.finished:
            return

        sp = self.current_speed()

        # Scroll road
        self.road_y1 += sp
        self.road_y2 += sp
        if self.road_y1 >= H:  self.road_y1 = self.road_y2 - H
        if self.road_y2 >= H:  self.road_y2 = self.road_y1 - H

        self.player.update()
        self.distance += sp * 0.1

        # Expire nitro
        if self.active_pu == "nitro" and time.time() > self.pu_end:
            self.active_pu = None
            self.player.nitro = False

        # Spawn timers (get harder over time)
        t_int = max(0.5, self.t_int - self.progress() * 0.8)
        o_int = max(0.8, self.o_int - self.progress() * 0.5)
        now   = time.time()

        if now - self.t_timer > t_int:
            count = 1 + int(self.progress() * 1.5)
            for _ in range(count):
                self.enemies.append(Enemy(sp * random.uniform(0.7, 1.0)))
            self.t_timer = now

        if now - self.o_timer > o_int:
            self.obstacles.append(Obstacle(sp))
            self.o_timer = now

        if now - self.c_timer > 0.9:
            self.coins.append(Coin(sp))
            self.c_timer = now

        if now - self.p_timer > 6.0:
            self.powerups.append(PowerUp(sp))
            self.p_timer = now

        pr = self.player.rect()

        # Enemy collisions
        for e in self.enemies[:]:
            e.update()
            if e.rect().colliderect(pr):
                self.enemies.remove(e)
                if self._take_hit(): return
            elif e.off():
                self.enemies.remove(e)

        # Obstacle collisions
        for o in self.obstacles[:]:
            o.update()
            if o.rect().colliderect(pr):
                self.obstacles.remove(o)
                if self._take_hit(): return
            elif o.off():
                self.obstacles.remove(o)

        # Collect coins
        for c in self.coins[:]:
            c.update()
            if c.rect().colliderect(pr):
                self.coin_count += c.val
                self.coins.remove(c)
                if self.coin_count % 10 == 0:   # speed up every 10 coins
                    self.base_spd = min(self.base_spd + 0.3, 14)
            elif c.off():
                self.coins.remove(c)

        # Collect power-ups
        for p in self.powerups[:]:
            p.update()
            if p.rect().colliderect(pr):
                self._activate(p.kind)
                self.score += 50
                self.powerups.remove(p)
            elif p.off():
                self.powerups.remove(p)

        self.score = int(self.coin_count * 10 + self.distance * 0.5)

        if self.distance >= self.FINISH:
            self.finished = True
            self.score += 500

    def _take_hit(self):
        if self.player.shield:
            self.player.shield = False
            self.active_pu = None
            return False
        self.crashes += 1
        if self.crashes > 1:
            self.alive = False
            return True
        return False

    def _activate(self, kind):
        if kind == "nitro":
            self.active_pu = "nitro"
            self.pu_end = time.time() + 4
            self.player.nitro = True
            self.player.nitro_end = self.pu_end
        elif kind == "shield":
            self.active_pu = "shield"
            self.player.shield = True
        elif kind == "repair":
            if self.crashes > 0:
                self.crashes -= 1

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surf):
        surf.blit(img_street, (0, int(self.road_y2)))
        surf.blit(img_street, (0, int(self.road_y1)))

        for o in self.obstacles: o.draw(surf)
        for c in self.coins:     c.draw(surf)
        for e in self.enemies:   e.draw(surf)
        for p in self.powerups:  p.draw(surf)
        self.player.draw(surf)
        self._draw_hud(surf)

    def _draw_hud(self, surf):
        pygame.draw.rect(surf, BLACK, (0, 0, W, 50))

        _txt(surf, f"Score: {self.score}",      19,  8,  6, WHITE,  center=False)
        _txt(surf, f"Coins: {self.coin_count}",  19,  8, 28, YELLOW, center=False)

        # Progress bar
        bx, by, bw = 170, 10, 160
        pygame.draw.rect(surf, (60, 60, 60), (bx, by, bw, 14), border_radius=5)
        pygame.draw.rect(surf, GREEN,
                         (bx, by, int(bw * self.progress()), 14), border_radius=5)
        _txt(surf, f"{int(self.distance)}/{self.FINISH}m", 12, bx + bw // 2, by + 2)

        # Lives (hearts)
        lives = "♥ " * (2 - self.crashes)
        _txt(surf, lives, 18, W - 6, 6, RED, center=False)

        # Active power-up
        if self.active_pu == "nitro":
            rem = max(0, self.pu_end - time.time())
            _txt(surf, f"NITRO {rem:.1f}s", 17, W // 2, 56, ORANGE)
        elif self.active_pu == "shield":
            _txt(surf, "SHIELD ON", 17, W // 2, 56, CYAN)