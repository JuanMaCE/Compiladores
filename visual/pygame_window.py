import pygame
import sys
import math
from logic.node import Node
from logic.grafodirigdo import Grafodirigido

pygame.init()

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
        self.graph = 0
        self.shape_tipo = 0
        if self.tipo == "ENTRADA":
            self.shape_tipo = 1
        elif self.tipo == "SALIDA":
            self.shape_tipo = 2
        elif self.tipo == "PROCESO":
            self.shape_tipo = 3
        elif self.tipo == "DECISIÓN":
            self.shape_tipo = 4
        elif self.tipo == "FIN":
            self.shape_tipo = 5
        elif self.tipo == "CallMeBaby":
            self.shape_tipo = 6

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def center(self):
        return self.x + self.width // 2, self.y + self.height // 2

    def return_texto(self):
        return  self.texto

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
            pygame.draw.ellipse(surface, color, r) if self.tipo in ["INICIO", "FIN"] else pygame.draw.rect(surface,
                                                                                                           color, r,
                                                                                                           border_radius=10)
            pygame.draw.ellipse(surface, (0, 0, 0), r, 2) if self.tipo in ["INICIO", "FIN"] else pygame.draw.rect(
                surface, (0, 0, 0), r, 2, border_radius=10)

        text_surface = font.render(self.texto, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=r.center)
        surface.blit(text_surface, text_rect)

    def set_graph(self, valor:int):
        self.graph = valor



class Connection:
    def __init__(self, inicio: Shape, fin: Shape):
        self.a = inicio
        self.b = fin
        indice = self.b.tipo
        indice = self.b.tipo

        if inicio.graph != 0:
            functions[0].eliminar_por_id(self.b.id)
            print(self.b.id, "|" , self.b.shape_tipo, "|" , self.b.return_texto() , "|", self.b, "|", " eso almacena mi nodo")
            functions[inicio.graph].agregar_vertice(self.b.id, self.b.shape_tipo, self.b.return_texto(), self.b)
            functions[inicio.graph].agregar_arista(inicio.id, fin.id)
        else:
            functions[inicio.graph].agregar_arista(inicio.id, fin.id)


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
functions = []
id = 0
id_graph = 0
shape_beggin = shape_types[0]
create_shape_beggin = Shape(0, shape_beggin, 50, 50)
shapes.append(create_shape_beggin)
node_inicio = Node(id, 0, "INICIO", create_shape_beggin)
def_main =  Grafodirigido(node_inicio, id_graph) # -> aqui se crea el grafo
functions.append(def_main)
create_shape_beggin.set_graph(def_main.id)



def edit_text(shape: Shape):
    import tkinter as tk
    from tkinter import simpledialog
    root = tk.Tk()
    root.withdraw()
    new_text = simpledialog.askstring("Editar Texto", "Nuevo contenido:", initialvalue=shape.texto)

    try:
        id_of_function = 0
        for function in functions:
            lista = function.devolver_list_of_vertices()
            for nodo in lista:
                if shape.id == nodo.return_id():
                    id_of_function = function.id
                    break

        nodo = functions[id_of_function].obtener_nodo_por_id(shape.id)
        if nodo is not None:
            nodo.node_change_info(new_text)
    except Exception as e:
        print(f"Error al editar el nodo: {e}")

    if new_text:
        shape.texto = new_text
    return str(new_text)


running = True
while running:
    screen.fill((245, 245, 245))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # generacion de figuras
            if pygame.K_1 <= event.key <= pygame.K_7:
                id += 1
                shape_beggin = shape_types[event.key - pygame.K_1]
                create_shape_beggin = Shape(id, shape_beggin, 50, 50)
                shapes.append(create_shape_beggin)
                indice = event.key - pygame.K_1
                if indice == 0:
                    id_graph += 1
                    node_inicio = Node(id, 0, "INICIO", create_shape_beggin)
                    new_grafo = Grafodirigido(node_inicio, id_graph)
                    functions.append(new_grafo)
                    create_shape_beggin.set_graph(id_graph)

                if indice == 1:
                    def_main.agregar_vertice(id, indice, "ENTRADA", create_shape_beggin)
                elif indice == 2:
                    def_main.agregar_vertice(id, indice, "Salida", create_shape_beggin)
                elif indice == 3:
                    def_main.agregar_vertice(id, indice, "PROCESO", create_shape_beggin)
                elif indice == 4:
                    def_main.agregar_vertice(id, indice, "condicion", create_shape_beggin)
                elif indice == 5:
                    def_main.agregar_vertice(id, indice, "final", create_shape_beggin)
                elif indice == 6:
                    def_main.agregar_vertice(id, indice, "funcion", create_shape_beggin)
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
                                s.set_graph(connecting_from.graph)
                                arista = Connection(connecting_from, s)

                                connections.append(arista)
                                connecting_from = None
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


print("Grafos:")
print("  ")
print("  ")
print("  ")

for function in functions:
    function.generate_code_C()
    print(function.code_c)