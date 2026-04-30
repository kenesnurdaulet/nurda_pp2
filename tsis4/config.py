# config.py
WIDTH, HEIGHT = 600, 600
CELL = 20
COLS = WIDTH // CELL
ROWS = HEIGHT // CELL

FPS_BASE       = 8
FPS_PER_LEVEL  = 2
FOOD_PER_LEVEL = 5

# Colors
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (60,  60,  60)
LIGHT_GRAY = (180, 180, 180)
GREEN      = (50,  200, 50)
DARK_GREEN = (20,  120, 20)
RED        = (220, 50,  50)
DARK_RED   = (120, 10,  10)
YELLOW     = (230, 200, 50)
ORANGE     = (230, 130, 30)
CYAN       = (50,  200, 200)
PURPLE     = (150, 50,  200)

# Food disappear time (ms) for bonus/poison
FOOD_TIMEOUT_MS = 7000

# Power-up timings (ms)
POWERUP_FIELD_MS  = 8000   # stays on field
POWERUP_EFFECT_MS = 5000   # effect duration
POWERUP_SPAWN_MS  = 12000  # interval between spawns

# Obstacles
OBSTACLE_BASE      = 4
OBSTACLE_PER_LEVEL = 2  # extra per level above 3

# DB
DB_CONFIG = {
    "dbname":   "snake_game",
    "user":     "postgres",
    "password": "postgres",
    "host":     "localhost",
    "port":     5432,
}