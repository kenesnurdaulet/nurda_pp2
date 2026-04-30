import pygame
import sys
import datetime
from tools import draw_line, flood_fill, draw_shape

pygame.init()

# ---------- SCREEN ----------
WIDTH, HEIGHT = 1000, 700
TOOLBAR = 180

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint TSIS 2 FIXED")

clock = pygame.time.Clock()

# ---------- COLORS ----------
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (200,200,200)
DARK = (40,40,40)
BLUE = (0,120,215)

PALETTE = [
    (0,0,0),(255,255,255),(255,0,0),(0,255,0),
    (0,0,255),(255,255,0),(255,165,0),(128,0,128)
]

# ---------- CANVAS ----------
canvas = pygame.Surface((WIDTH-TOOLBAR, HEIGHT))
canvas.fill(WHITE)

# ---------- STATE ----------
tool = "pencil"
color = BLACK
brush_size = 5

drawing = False
start_pos = None
last_pos = None

# TEXT
text_mode = False
text_input = ""
text_pos = (0,0)

font = pygame.font.SysFont("Verdana", 18)
font_big = pygame.font.SysFont("Verdana", 24)

TOOLS = ["pencil","line","rect","circle","square","rtriangle","eqtriangle","rhombus","fill","text","erase"]

# ---------- UI ----------
def draw_ui():
    pygame.draw.rect(screen, DARK, (0,0,TOOLBAR,HEIGHT))

    for i,t in enumerate(TOOLS):
        rect = pygame.Rect(10,10+i*35,160,30)
        c = BLUE if t==tool else GRAY
        pygame.draw.rect(screen,c,rect)
        screen.blit(font.render(t,True,BLACK),(20,15+i*35))

    for i,c in enumerate(PALETTE):
        pygame.draw.rect(screen,c,(10+(i%2)*70,450+(i//2)*40,60,30))

# ---------- SAVE ----------
def save_canvas():
    name=f"paint_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    pygame.image.save(canvas,name)

# ---------- MAIN ----------
while True:
    screen.fill(WHITE)
    screen.blit(canvas,(TOOLBAR,0))
    draw_ui()

    mouse = pygame.mouse.get_pos()
    canvas_pos = (mouse[0]-TOOLBAR, mouse[1])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # KEYBOARD
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_1: brush_size=2
            if event.key == pygame.K_2: brush_size=5
            if event.key == pygame.K_3: brush_size=10

            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                save_canvas()

            if text_mode:
                if event.key == pygame.K_RETURN:
                    img = font_big.render(text_input,True,color)
                    canvas.blit(img,text_pos)
                    text_mode=False
                    text_input=""
                elif event.key == pygame.K_ESCAPE:
                    text_mode=False
                    text_input=""
                else:
                    text_input+=event.unicode

        # MOUSE DOWN
        if event.type == pygame.MOUSEBUTTONDOWN:
            x,y = event.pos

            if x < TOOLBAR:
                idx=(y-10)//35
                if 0<=idx<len(TOOLS):
                    tool=TOOLS[idx]

                for i,c in enumerate(PALETTE):
                    px=10+(i%2)*70
                    py=450+(i//2)*40
                    if px<=x<=px+60 and py<=y<=py+30:
                        color=c
            else:
                if tool=="fill":
                    flood_fill(canvas,*canvas_pos,color)
                elif tool=="text":
                    text_mode=True
                    text_pos=canvas_pos
                    text_input=""
                else:
                    drawing=True
                    start_pos=canvas_pos
                    last_pos=canvas_pos

        # MOUSE UP
        if event.type == pygame.MOUSEBUTTONUP:
            if drawing:
                if tool not in ["pencil","erase"]:
                    draw_shape(canvas,tool,start_pos,canvas_pos,color,brush_size)
                drawing=False

        # DRAW
        if event.type == pygame.MOUSEMOTION and drawing:
            if tool=="pencil":
                draw_line(canvas,color,last_pos,canvas_pos,brush_size)
                last_pos=canvas_pos
            elif tool=="erase":
                pygame.draw.line(canvas, WHITE, last_pos, canvas_pos, brush_size*2)
    # ---------- FIXED PREVIEW ----------
    if drawing and tool not in ["pencil","erase"]:
        start_screen = (start_pos[0]+TOOLBAR, start_pos[1])
        current_screen = (canvas_pos[0]+TOOLBAR, canvas_pos[1])

        draw_shape(screen,tool,start_screen,current_screen,color,brush_size)

    # TEXT PREVIEW
    if text_mode:
        preview=font_big.render(text_input+"|",True,color)
        screen.blit(preview,(text_pos[0]+TOOLBAR,text_pos[1]))

    pygame.display.update()
    clock.tick(60)