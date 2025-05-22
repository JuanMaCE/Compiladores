import pygame
import sys
import math
from logic.node import Node
from logic.grafodirigdo import Grafodirigido

pygame.init()
WIDTH2, HEIGHT2 = 400, 300
FONT = pygame.font.SysFont(None, 24)
instrucciones_texto = "Presione 1 2 3 4 5 6"
salida_texto = "Resultado al presionar enter"
GAP2 = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Editor de Diagrama de Flujo")
font = pygame.font.SysFont("arial", 18)
clock = pygame.time.Clock()

colors = {
    "INICIO": (220, 70, 70),
    "ENTRADA": (150, 100, 200),
    "SALIDA": (240, 160, 50),
    "PROCESO": (70, 130, 180),
    "DECISIÓN": (50, 200, 120),
    "FIN": (220, 70, 70),
    "CallMeBaby" : (220, 130, 70)

}

shape_types = list(colors.keys())


class Shape:
    def __init__(self, id: int, tipo, x, y, texto=""):
        self.tipo = tipo
        self.x = x
        self.y = y
        self.texto = texto or tipo
        self.width = 140
        self.height = 60
        self.selected = False
        self.id = id

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def center(self):
        return self.x + self.width // 2, self.y + self.height // 2

    def return_texto(self):
        return self.texto

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
            points = [(r.left, r.top + 20), (r.right - 20, r.top), (r.right, r.centery), (r.right - 20, r.bottom),(r.left, r.bottom)]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (0, 0, 0), points, 2)
        else:
            pygame.draw.rect(surface, color, r, border_radius=10)
            pygame.draw.rect(surface, (0, 0, 0), r, 2, border_radius=10)

        text_surface = font.render(self.texto, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=r.center)
        surface.blit(text_surface, text_rect)


class Connection:
    def __init__(self, a: Shape, b: Shape):
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

id = 0
shape_beggin = shape_types[0]
create_shape_beggin = Shape(0, shape_beggin, 50, 50)
shapes.append(create_shape_beggin)
node_inicio = Node(id, 0, "INICIO", create_shape_beggin)
grafo = Grafodirigido(node_inicio) # -> aqui se crea el grafo


def draw_left():
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH2, HEIGHT2))
    text_surface = FONT.render(instrucciones_texto, True, BLACK)
    screen.blit(text_surface, (20, HEIGHT // 2))


# Función 2: Dibujar ventana derecha
def draw_right(text):
    pygame.draw.rect(screen, WHITE, (WIDTH + GAP2, 0, WIDTH2, HEIGHT2))
    text_surface = FONT.render(text, True, BLACK)
    screen.blit(text_surface, (WIDTH + GAP2 + 20, HEIGHT // 2))


def update_text(new_text):
    global salida_texto
    salida_texto = new_text


def edit_text(shape: Shape):
    import tkinter as tk
    from tkinter import simpledialog
    root = tk.Tk()
    root.withdraw()
    new_text = simpledialog.askstring("Editar Texto", "Nuevo contenido:", initialvalue=shape.texto)
    nodo = grafo.obtener_nodo_por_id(shape.id)
    nodo.node_change_info(new_text)

    if new_text:
        shape.texto = new_text
    return str(new_text)


running = True
while running:
    draw_left()
    draw_right(salida_texto)
    screen.fill((245, 245, 245))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # generacion de figuras
            if event.key == pygame.K_RETURN:
                grafo.generate_code_C()
                # aqui van las funciones ROGER
                # code_asm = grafo.generate_code_asm()
                # code_py = grafo.generate_code_python()
                # EN CONSOLA AUN
                print("Código C:\n", grafo.code_c)
                update_text(grafo.code_c)
                # print("Código ASM:\n", code_asm)
                # print("Código Python:\n", code_py)
            if pygame.K_1 <= event.key <= pygame.K_7:
                id += 1
                shape_beggin = shape_types[event.key - pygame.K_1]
                create_shape_beggin = Shape(id, shape_beggin, 50, 50)
                shapes.append(create_shape_beggin)
                indice = event.key - pygame.K_1
                if indice == 0:
                    grafo.agregar_vertice(id, indice, "INICIO", create_shape_beggin)
                elif indice == 1:
                    grafo.agregar_vertice(id, indice, "ENTRADA", create_shape_beggin)
                elif indice == 2:
                    grafo.agregar_vertice(id, indice, "Salida", create_shape_beggin)
                elif indice == 3:
                    grafo.agregar_vertice(id, indice, "PROCESO", create_shape_beggin)
                elif indice == 4:
                    grafo.agregar_vertice(id, indice, "condicion", create_shape_beggin)
                elif indice == 5:
                    grafo.agregar_vertice(id, indice, "final", create_shape_beggin)
                elif indice == 6:
                    grafo.agregar_vertice(id, indice, "funcion", create_shape_beggin)


            elif event.key == pygame.K_DELETE:
                for s in shapes:
                    if s.selected:
                        connections[:] = [c for c in connections if c.a != s and c.b != s]
                        shapes.remove(s)
                        break

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # click izquierdo
                for s in shapes:
                    s.selected = False  # deseleccionar todas
                for s in reversed(shapes):
                    if s.rect().collidepoint(event.pos):
                        selected_shape = s
                        s.selected = True
                        drag_offset = (s.x - event.pos[0], s.y - event.pos[1])
                        if pygame.key.get_mods() & pygame.KMOD_CTRL:
                            if connecting_from and connecting_from != s:
                                arista = Connection(connecting_from, s)
                                connections.append(arista)
                                connecting_from = None
                                grafo.agregar_arista(arista.a.id, arista.b.id)
                            else:
                                connecting_from = s
                        break
            if event.button == 3:  # click derecho
                for s in shapes:
                    s.selected = False
                for s in reversed(shapes):
                    if s.rect().collidepoint(event.pos):
                        selected_shape = s
                        s.selected = True
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
