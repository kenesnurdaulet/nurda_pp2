import pygame
import math

def draw_line(surface, color, start, end, width):
    pygame.draw.line(surface, color, start, end, width)

def flood_fill(surface, x, y, new_color):
    target = surface.get_at((x,y))
    if target == new_color:
        return

    stack = [(x,y)]
    w,h = surface.get_size()

    while stack:
        px,py = stack.pop()
        if 0<=px<w and 0<=py<h:
            if surface.get_at((px,py)) == target:
                surface.set_at((px,py), new_color)
                stack.extend([(px+1,py),(px-1,py),(px,py+1),(px,py-1)])

def draw_shape(surface, tool, p1, p2, color, size):
    x1,y1 = p1
    x2,y2 = p2

    if tool == "line":
        pygame.draw.line(surface, color, p1, p2, size)

    elif tool == "rect":
        pygame.draw.rect(surface, color,
            pygame.Rect(min(x1,x2),min(y1,y2),abs(x2-x1),abs(y2-y1)), size)

    elif tool == "circle":
        r = int(math.hypot(x2-x1,y2-y1))
        pygame.draw.circle(surface, color, p1, r, size)

    elif tool == "square":
        s = min(abs(x2-x1),abs(y2-y1))
        pygame.draw.rect(surface, color, (x1,y1,s,s), size)

    elif tool == "rtriangle":
        pygame.draw.polygon(surface, color, [(x1,y1),(x2,y1),(x2,y2)], size)

    elif tool == "eqtriangle":
        s = math.hypot(x2-x1,y2-y1)
        h = (math.sqrt(3)/2)*s
        pygame.draw.polygon(surface, color, [(x1,y1),(x2,y2),(x1,y1-h)], size)

    elif tool == "rhombus":
        mx,my = (x1+x2)//2,(y1+y2)//2
        dx,dy = abs(x2-x1)//2,abs(y2-y1)//2
        pts = [(mx,my-dy),(mx+dx,my),(mx,my+dy),(mx-dx,my)]
        pygame.draw.polygon(surface, color, pts, size)