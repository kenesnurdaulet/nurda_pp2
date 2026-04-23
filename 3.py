import pygame
import sys
from pygame.locals import *
import random

pygame.init()

FPS = 60
clock = pygame.time.Clock()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (60, 60, 60)
YELLOW = (255, 215, 0)

font = pygame.font.SysFont("Verdana", 22)

line_y = 0
coins_collected = 0


# ROAD
def draw_road():
    global line_y
    screen.fill(GRAY)

    for i in range(0, SCREEN_HEIGHT, 40):
        pygame.draw.rect(screen, WHITE,
                         (SCREEN_WIDTH//2 - 5, i + line_y, 10, 20))

    line_y += 6
    if line_y >= 40:
        line_y = 0


# PLAYER
class Player:
    def __init__(self):
        self.image = pygame.image.load("Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (200, 500)
        self.speed = 6

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# ENEMY
class Enemy:
    def __init__(self):
        self.image = pygame.image.load("Enemy.png")
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self):
        self.rect.x = random.randint(40, SCREEN_WIDTH - 80)
        self.rect.y = -100

    def move(self):
        self.rect.y += 6
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# COIN
class Coin:
    def __init__(self):
        self.x = random.randint(40, SCREEN_WIDTH - 40)
        self.y = -20

    def move(self):
        self.y += 5

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (self.x, self.y), 8)

    def rect(self):
        return pygame.Rect(self.x-8, self.y-8, 16, 16)


def game_over():
    text = font.render("GAME OVER", True, WHITE)
    screen.blit(text, (120, 250))
    pygame.display.update()
    pygame.time.delay(2000)
    pygame.quit()
    sys.exit()


# OBJECTS
player = Player()
enemy = Enemy()
coins = []

# LOOP
while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # spawn coins (less often)
    if random.randint(1, 140) == 1:
        coins.append(Coin())

    player.update()
    enemy.move()

    for coin in coins[:]:
        coin.move()

        if player.rect.colliderect(coin.rect()):
            coins.remove(coin)
            coins_collected += 1

    # collision enemy
    if player.rect.colliderect(enemy.rect):
        game_over()

    draw_road()

    player.draw(screen)
    enemy.draw(screen)

    for coin in coins:
        coin.draw(screen)

    score = font.render(f"Coins: {coins_collected}", True, WHITE)
    screen.blit(score, (250, 10))

    pygame.display.update()
    clock.tick(FPS)