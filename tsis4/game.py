# game.py
import pygame, random
from config import *

UP, DOWN, LEFT, RIGHT = (0,-1),(0,1),(-1,0),(1,0)
OPPOSITE = {UP:DOWN, DOWN:UP, LEFT:RIGHT, RIGHT:LEFT}


class Food:
    def __init__(self, pos, kind="normal"):
        self.pos  = pos
        self.kind = kind
        self.born = pygame.time.get_ticks()
        self.pts  = {"normal":1, "bonus":3, "poison":0}[kind]
        self.color= {"normal":GREEN, "bonus":YELLOW, "poison":DARK_RED}[kind]
        self.timed= kind in ("bonus","poison")

    def expired(self):
        return self.timed and pygame.time.get_ticks()-self.born > FOOD_TIMEOUT_MS

    def draw(self, surface):
        x, y = self.pos[0]*CELL, self.pos[1]*CELL
        pygame.draw.rect(surface, self.color, (x+3,y+3,CELL-6,CELL-6), border_radius=4)


class PowerUp:
    def __init__(self, pos, kind):
        self.pos  = pos
        self.kind = kind
        self.born = pygame.time.get_ticks()
        self.color= {"speed":ORANGE,"slow":CYAN,"shield":PURPLE}[kind]
        self.label= {"speed":"S","slow":"W","shield":"X"}[kind]

    def expired(self):
        return pygame.time.get_ticks()-self.born > POWERUP_FIELD_MS

    def draw(self, surface):
        x, y = self.pos[0]*CELL, self.pos[1]*CELL
        pygame.draw.rect(surface, self.color, (x+2,y+2,CELL-4,CELL-4), border_radius=5)
        f = pygame.font.SysFont("monospace", CELL-4, bold=True)
        t = f.render(self.label, True, WHITE)
        surface.blit(t, (x+(CELL-t.get_width())//2, y+(CELL-t.get_height())//2))


class Game:
    def __init__(self, snake_color, grid, sound):
        self.snake_color = tuple(snake_color)
        self.grid  = grid
        self.sound = sound
        self.score = 0
        self.level = 1
        self.eaten = 0
        self.best  = 0
        self.shield= False

        mid = (COLS//2, ROWS//2)
        self.body = [mid, (mid[0]-1,mid[1]), (mid[0]-2,mid[1])]
        self.dir  = RIGHT

        self.foods    = []
        self.powerup  = None
        self.obstacles= set()
        self.effect   = None
        self.eff_start= 0
        self.next_pu  = pygame.time.get_ticks() + POWERUP_SPAWN_MS

        self._spawn_food()

    def _occupied(self):
        s = set(self.body) | self.obstacles
        s |= {f.pos for f in self.foods}
        if self.powerup: s.add(self.powerup.pos)
        return s

    def _empty_cell(self):
        occ  = self._occupied()
        free = [(c,r) for c in range(COLS) for r in range(ROWS) if (c,r) not in occ]
        return random.choice(free) if free else None

    def _spawn_food(self, kind="normal"):
        pos = self._empty_cell()
        if pos: self.foods.append(Food(pos, kind))

    def _place_obstacles(self):
        if self.level < 3: return
        count = OBSTACLE_BASE + (self.level-3)*OBSTACLE_PER_LEVEL
        head  = self.body[0]
        safe  = {(head[0]+dx, head[1]+dy) for dx in range(-3,4) for dy in range(-3,4)}
        cands = [(c,r) for c in range(COLS) for r in range(ROWS)
                 if (c,r) not in set(self.body) and (c,r) not in safe]
        random.shuffle(cands)
        self.obstacles = set(cands[:count])

    def get_fps(self):
        fps = FPS_BASE + (self.level-1)*FPS_PER_LEVEL
        if self.effect=="speed": fps = int(fps*1.6)
        if self.effect=="slow":  fps = max(3, int(fps*0.6))
        return min(fps, 25)

    def update(self):
        # expire effect
        if self.effect and self.effect!="shield":
            if pygame.time.get_ticks()-self.eff_start > POWERUP_EFFECT_MS:
                self.effect = None

        # expire field items
        self.foods = [f for f in self.foods if not f.expired()]
        if self.powerup and self.powerup.expired(): self.powerup = None

        # ensure normal food exists
        if not any(f.kind=="normal" for f in self.foods): self._spawn_food()

        # spawn power-up
        now = pygame.time.get_ticks()
        if self.powerup is None and now >= self.next_pu:
            pos = self._empty_cell()
            if pos: self.powerup = PowerUp(pos, random.choice(["speed","slow","shield"]))
            self.next_pu = now + POWERUP_SPAWN_MS

        # move
        head = (self.body[0][0]+self.dir[0], self.body[0][1]+self.dir[1])

        # collisions
        if not (0<=head[0]<COLS and 0<=head[1]<ROWS) or head in self.body[1:] or head in self.obstacles:
            if self.shield:
                self.shield = False; self.effect = None
                head = (head[0]%COLS, head[1]%ROWS)  # wrap on wall hit
            else:
                return "dead"

        self.body.insert(0, head)

        # food
        for food in self.foods[:]:
            if head==food.pos:
                self.foods.remove(food)
                if food.kind=="poison":
                    for _ in range(2):
                        if len(self.body)>1: self.body.pop()
                    if len(self.body)<=1: return "dead"
                else:
                    self.score += food.pts * self.level
                    if food.kind=="normal":
                        self.eaten += 1
                        if random.random()<0.2: self._spawn_food("bonus")
                        if random.random()<0.1: self._spawn_food("poison")
                        if self.eaten>=FOOD_PER_LEVEL:
                            self.level+=1; self.eaten=0
                            self._place_obstacles()
                        self._spawn_food()
                break
        else:
            self.body.pop()

        # power-up
        if self.powerup and head==self.powerup.pos:
            k = self.powerup.kind
            self.effect=k; self.eff_start=now
            if k=="shield": self.shield=True
            self.powerup=None

        return "alive"

    def draw(self, surface):
        surface.fill(BLACK)

        if self.grid:
            for c in range(COLS):
                pygame.draw.line(surface, (20,20,20),(c*CELL,0),(c*CELL,HEIGHT))
            for r in range(ROWS):
                pygame.draw.line(surface, (20,20,20),(0,r*CELL),(WIDTH,r*CELL))

        for (c,r) in self.obstacles:
            pygame.draw.rect(surface, (90,60,30),(c*CELL,r*CELL,CELL,CELL))

        for food in self.foods: food.draw(surface)
        if self.powerup: self.powerup.draw(surface)

        for i,(c,r) in enumerate(self.body):
            color = WHITE if i==0 else (self.snake_color if i%2==0 else DARK_GREEN)
            pygame.draw.rect(surface, color,(c*CELL+1,r*CELL+1,CELL-2,CELL-2),border_radius=3)

        # HUD
        f = pygame.font.SysFont("monospace",18,bold=True)
        surface.blit(f.render(f"Score:{self.score}",True,WHITE),(5,5))
        surface.blit(f.render(f"Lvl:{self.level}",True,YELLOW),(WIDTH//2-30,5))
        surface.blit(f.render(f"Best:{self.best}",True,CYAN),(WIDTH-90,5))
        if self.effect:
            clr={"speed":ORANGE,"slow":CYAN,"shield":PURPLE}[self.effect]
            surface.blit(f.render(f"[{self.effect.upper()}]",True,clr),(5,HEIGHT-25))