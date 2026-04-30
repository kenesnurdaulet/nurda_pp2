import pygame
import sys
import datetime
from tools import flood_fill

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint TSIS2")

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255, 255, 255))

clock = pygame.time.Clock()

# ---------------- SETTINGS ----------------
color = (0, 0, 0)
brush_size = 2

# tools: pencil, line, fill, text
tool = "pencil"
tool = "ereaser"

drawing = False
start_pos = None
last_pos = None

# ---------------- TEXT ----------------
font = pygame.font.SysFont("Arial", 24)
text_mode = False
text_input = ""
text_pos = (0, 0)

# ---------------- MAIN LOOP ----------------
while True:
    screen.blit(canvas, (0, 0))

    # preview line
    if tool == "line" and drawing and start_pos:
        temp = canvas.copy()
        pygame.draw.line(temp, color, start_pos, pygame.mouse.get_pos(), brush_size)
        screen.blit(temp, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # -------- KEYBOARD --------
        if event.type == pygame.KEYDOWN:

            # BRUSH SIZE
            if event.key == pygame.K_1:
                brush_size = 2
            if event.key == pygame.K_2:
                brush_size = 5
            if event.key == pygame.K_3:
                brush_size = 10

            # TOOLS
            if event.key == pygame.K_p:
                tool = "pencil"
            if event.key == pygame.K_l:
                tool = "line"
            if event.key == pygame.K_f:
                tool = "fill"
            if event.key == pygame.K_t:
                tool = "text"
            if event.key == pygame.K_e:
                tool = "eraser"

            # SAVE
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                filename = datetime.datetime.now().strftime("drawing_%Y%m%d_%H%M%S.png")
                pygame.image.save(canvas, filename)
                print("Saved:", filename)

            # TEXT INPUT
            if text_mode:
                if event.key == pygame.K_RETURN:
                    text_surface = font.render(text_input, True, color)
                    canvas.blit(text_surface, text_pos)
                    text_mode = False
                    text_input = ""

                elif event.key == pygame.K_ESCAPE:
                    text_mode = False
                    text_input = ""

                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]

                else:
                    text_input += event.unicode

        # -------- MOUSE --------
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            if tool == "fill":
                flood_fill(canvas, x, y, color)

            elif tool == "text":
                text_mode = True
                text_input = ""
                text_pos = (x, y)

            else:
                drawing = True
                start_pos = event.pos
                last_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            drawing = False

            if tool == "line" and start_pos:
                pygame.draw.line(canvas, color, start_pos, event.pos, brush_size)

        if event.type == pygame.MOUSEMOTION and drawing:
           if tool == "pencil":
             pygame.draw.line(canvas, color, last_pos, event.pos, brush_size)
             last_pos = event.pos

           elif tool == "eraser":
             pygame.draw.line(canvas, (255, 255, 255), last_pos, event.pos, brush_size*2)
             last_pos = event.pos

    # show typing text preview
    if text_mode:
        preview = font.render(text_input, True, color)
        screen.blit(preview, text_pos)

    pygame.display.update()
    clock.tick(60)