import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Editor de Diagrama de Flujo")
font = pygame.font.SysFont("arial", 18)
clock = pygame.time.Clock()

colors = {
    "INICIO": (220, 70, 70),
    "FIN": (220, 70, 70),
    "PROCESO": (70, 130, 180),
    "DECISIÓN": (50, 200, 120),
    "ENTRADA": (150, 100, 200),
    "SALIDA": (240, 160, 50),
}

shape_types = list(colors.keys())

class Shape:
    def __init__(self, tipo, x, y, texto=""):
        self.tipo = tipo
        self.x = x
        self.y = y
        self.texto = texto or tipo
        self.width = 140
        self.height = 60
        self.selected = False

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def center(self):
        return self.x + self.width // 2, self.y + self.height // 2

    def draw(self, surface):
        color = colors[self.tipo]
        points = []
        r = self.rect()

        if self.tipo == "DECISIÓN":
            cx, cy = r.center
            points = [(cx, r.top), (r.right, cy), (cx, r.bottom), (r.left, cy)]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (0, 0, 0), points, 2)
        elif self.tipo == "ENTRADA":
            points = [(r.left + 30, r.top), (r.right, r.top), (r.right - 30, r.bottom), (r.left, r.bottom)]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (0, 0, 0), points, 2)
        elif self.tipo == "SALIDA":
            points = [(r.left, r.top), (r.right - 30, r.top), (r.right, r.bottom), (r.left + 30, r.bottom)]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (0, 0, 0), points, 2)
        else:
            pygame.draw.ellipse(surface, color, r) if self.tipo in ["INICIO", "FIN"] else pygame.draw.rect(surface, color, r, border_radius=10)
            pygame.draw.ellipse(surface, (0, 0, 0), r, 2) if self.tipo in ["INICIO", "FIN"] else pygame.draw.rect(surface, (0, 0, 0), r, 2, border_radius=10)

        text_surface = font.render(self.texto, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=r.center)
        surface.blit(text_surface, text_rect)

class Connection:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def draw(self, surface):
        ax, ay = self.a.center()
        bx, by = self.b.center()
        pygame.draw.line(surface, (0, 0, 0), (ax, ay), (bx, by), 2)
        self.draw_arrow(surface, (ax, ay), (bx, by))

    def draw_arrow(self, surface, start, end):
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        size = 10
        x = end[0] - size * math.cos(angle)
        y = end[1] - size * math.sin(angle)
        points = [
            end,
            (x + size * math.sin(angle), y - size * math.cos(angle)),
            (x - size * math.sin(angle), y + size * math.cos(angle)),
        ]
        pygame.draw.polygon(surface, (0, 0, 0), points)

shapes = []
connections = []
selected_shape = None
drag_offset = (0, 0)
connecting_from = None

def edit_text(shape):
    import tkinter as tk
    from tkinter import simpledialog
    root = tk.Tk()
    root.withdraw()
    new_text = simpledialog.askstring("Editar Texto", "Nuevo contenido:", initialvalue=shape.texto)
    if new_text:
        shape.texto = new_text

running = True
while running:
    screen.fill((245, 245, 245))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_6:
                shape_type = shape_types[event.key - pygame.K_1]
                shapes.append(Shape(shape_type, 50, 50))
            elif event.key == pygame.K_SPACE:
                print("Secuencia:")
                for i, s in enumerate(shapes):
                    print(f"{i+1}. {s.tipo}: {s.texto}")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # click izquierdo
                for s in reversed(shapes):
                    if s.rect().collidepoint(event.pos):
                        selected_shape = s
                        s.selected = True
                        drag_offset = (s.x - event.pos[0], s.y - event.pos[1])
                        if pygame.key.get_mods() & pygame.KMOD_CTRL:
                            if connecting_from and connecting_from != s:
                                connections.append(Connection(connecting_from, s))
                                connecting_from = None
                            else:
                                connecting_from = s
                        break
            elif event.button == 3:  # click derecho
                for s in shapes:
                    if s.rect().collidepoint(event.pos):
                        edit_text(s)
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if selected_shape:
                    selected_shape.selected = False
                    selected_shape = None

        elif event.type == pygame.MOUSEMOTION:
            if selected_shape:
                selected_shape.x = event.pos[0] + drag_offset[0]
                selected_shape.y = event.pos[1] + drag_offset[1]

    for c in connections:
        c.draw(screen)
    for s in shapes:
        s.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
