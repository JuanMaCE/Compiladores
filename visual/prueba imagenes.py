import pygame
import sys
import os
import math
import json
from tkinter import filedialog
from tkinter import Tk
from logic.node import Node
from logic.grafodirigdo import Grafodirigido

pygame.init()
WIDTH, HEIGHT = 1400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Editor de Diagramas de Flujo")

# Colors
DARK_BG = (0, 0, 0)  # Black background
PANEL_COLOR = (30, 30, 30)  # Dark gray panels
TEXT_COLOR = (255, 255, 255)  # White text (general)
SHAPE_TEXT_COLOR = (0, 0, 0)  # Black text for shapes
ACCENT_COLOR = (0, 100, 200)  # Blue for selection
SHAPE_COLOR = (200, 200, 200)  # Default shape color

# Panel dimensions
PANEL_LEFT_WIDTH = 250
PANEL_RIGHT_WIDTH = 300
WORK_AREA_WIDTH = WIDTH - PANEL_LEFT_WIDTH - PANEL_RIGHT_WIDTH

# Shape types with colors from second code
SHAPE_TYPES = ["inicio", "entrada", "salida", "proceso", "decision", "fin", "llamada"]
SHAPE_COLORS = {
    "inicio": (220, 70, 70),
    "entrada": (150, 100, 200),
    "salida": (240, 160, 50),
    "proceso": (70, 130, 180),
    "decision": (50, 200, 120),
    "fin": (220, 70, 70),
    "llamada": (220, 130, 70)
}

# Graph logic variables
id_counter = 0
id_graph = 0
functions = []  # Will store Grafodirigido instances


def cargar_imagenes():
    images = {}
    for shape in SHAPE_TYPES:
        try:
            image_path = os.path.join(r"C:\Users\DELL\PycharmProjects\Compiladores\images", f"{shape}.png")
            image = pygame.image.load(image_path).convert_alpha()
            base_width = 85
            aspect_ratio = image.get_height() / image.get_width()
            new_height = int(base_width * aspect_ratio)
            images[shape] = pygame.transform.scale(image, (base_width, new_height))
        except Exception as e:
            print(f"Error cargando imagen para {shape}: {e}")
            surf = pygame.Surface((120, 60), pygame.SRCALPHA)
            pygame.draw.rect(surf, SHAPE_COLORS.get(shape, SHAPE_COLOR), (0, 0, 120, 60), border_radius=8)
            images[shape] = surf
    return images


shape_images = cargar_imagenes()

texto_panel_derecho = [
    ""
]

texto_instructivo = [
    "INSTRUCCIONES:",
    "1. Arrastra formas del panel izquierdo",
    "2. Haz clic derecho para editar texto",
    "3. Ctrl + clic para conectar formas(mantener)",
    "4. Botón COMPILAR para generar código",
    "5. Suprimir: borrar forma seleccionada",
    "6. G: Guardar grafo, C: Cargar grafo"
]


class TemplateShape:
    def __init__(self, tipo, x, y):
        self.tipo = tipo
        self.x = x
        self.y = y
        self.image = shape_images[tipo]
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))
        font = pygame.font.SysFont('Arial', 14)
        text = font.render(self.tipo.upper(), True, SHAPE_TEXT_COLOR)
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height + 15))
        surface.blit(text, text_rect)

    def clickeada(self, pos):
        return (self.x <= pos[0] <= self.x + self.width and
                self.y <= pos[1] <= self.y + self.height)


class WorkShape:
    def __init__(self, tipo, x, y, texto=""):
        global id_counter, id_graph, functions

        self.tipo = tipo
        self.x = x
        self.y = y
        self.image = shape_images[tipo]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.texto = texto or tipo.capitalize()
        self.selected = False
        self.connections = []
        self.connection_count = 0
        self.dragging = False
        self.drag_offset = (0, 0)
        self.editing = False
        self.edit_text = ""

        # Graph logic attributes
        self.id = id_counter
        id_counter += 1
        self.graph_id = 0  # Default to main graph

        # Shape type mapping
        self.shape_tipo = 0
        if self.tipo == "entrada":
            self.shape_tipo = 1
        elif self.tipo == "salida":
            self.shape_tipo = 2
        elif self.tipo == "proceso":
            self.shape_tipo = 3
        elif self.tipo == "decision":
            self.shape_tipo = 4
        elif self.tipo == "fin":
            self.shape_tipo = 5
        elif self.tipo == "llamada":
            self.shape_tipo = 6

        # If it's an "inicio" node, create a new graph
        if self.tipo == "inicio":
            self.graph_id = id_graph
            node = Node(self.id, self.shape_tipo, self.texto, self)
            new_graph = Grafodirigido(node, id_graph)
            functions.append(new_graph)
            id_graph += 1
        else:
            # Add to main graph by default
            if functions:
                functions[0].agregar_vertice(self.id, self.shape_tipo, self.texto, self)

    def draw(self, surface):
        # Draw image
        surface.blit(self.image, (self.x, self.y))

        # Draw text in black
        font = pygame.font.SysFont('Arial', 14)
        if self.editing:
            text = font.render(self.edit_text, True, (255, 0, 0))  # Red when editing
            pygame.draw.rect(surface, (240, 240, 240),
                             (self.x + 5, self.y + self.height // 2 - 10,
                              self.width - 10, 20))
        else:
            text = font.render(self.texto, True, SHAPE_TEXT_COLOR)

        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        surface.blit(text, text_rect)

        # Highlight selection
        if self.selected:
            pygame.draw.rect(surface, ACCENT_COLOR,
                             (self.x - 5, self.y - 5, self.width + 10, self.height + 10),
                             2, border_radius=12)

    def clickeada(self, pos):
        mask = pygame.mask.from_surface(self.image)
        rel_pos = (pos[0] - self.x, pos[1] - self.y)
        if 0 <= rel_pos[0] < self.width and 0 <= rel_pos[1] < self.height:
            return mask.get_at(rel_pos)
        return False

    def start_editing(self):
        self.editing = True
        self.edit_text = self.texto

    def stop_editing(self):
        self.editing = False
        if self.edit_text:
            self.texto = self.edit_text
            # Update the node in the graph
            for graph in functions:
                node = graph.obtener_nodo_por_id(self.id)
                if node:
                    node.node_change_info(self.texto)
                    break

    def return_texto(self):
        return self.texto

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'x': self.x,
            'y': self.y,
            'texto': self.texto,
            'graph_id': self.graph_id,
            'shape_tipo': self.shape_tipo
        }

    @classmethod
    def from_dict(cls, data):
        shape = cls(data['tipo'], data['x'], data['y'], data['texto'])
        shape.id = data['id']
        shape.graph_id = data['graph_id']
        shape.shape_tipo = data['shape_tipo']
        return shape


class Connection:
    def __init__(self, start_shape, end_shape):
        self.start = start_shape
        self.end = end_shape
        self.label = ""

        if start_shape.tipo == "decision":
            existing_connections = sum(1 for c in connections if c.start == start_shape)
            self.is_first_connection = (existing_connections == 0)
            self.label = "Sí" if self.is_first_connection else "No"

        # Add connection to graph
        if functions:
            # If connecting to a different graph, move the node
            if start_shape.graph_id != end_shape.graph_id and start_shape.graph_id != 0:
                # Remove from current graph
                for graph in functions:
                    if graph.id == end_shape.graph_id:
                        graph.eliminar_por_id(end_shape.id)
                        break

                # Add to new graph
                for graph in functions:
                    if graph.id == start_shape.graph_id:
                        graph.agregar_vertice(end_shape.id, end_shape.shape_tipo, end_shape.texto, end_shape)
                        graph.agregar_arista(start_shape.id, end_shape.id)
                        end_shape.graph_id = start_shape.graph_id
                        break
            else:
                # Add regular connection
                for graph in functions:
                    if graph.id == start_shape.graph_id:
                        graph.agregar_arista(start_shape.id, end_shape.id)
                        break

    def draw(self, surface):
        if self.start.tipo == "decision":
            if self.is_first_connection:
                start_pos = (self.start.x + self.start.width, self.start.y + self.start.height // 2)
            else:  # Bottom
                start_pos = (self.start.x + self.start.width // 2, self.start.y + self.start.height)
        elif self.start.tipo == "entrada":
            start_pos = (self.start.x + self.start.width, self.start.y + self.start.height // 2)
        elif self.start.tipo == "salida":
            start_pos = (self.start.x, self.start.y + self.start.height // 2)
        else:
            start_pos = (self.start.x + self.start.width // 2, self.start.y + self.start.height // 2)

        end_pos = (self.end.x + self.end.width // 2, self.end.y + self.end.height // 2)

        # Draw connection line
        pygame.draw.line(surface, (255, 255, 255), start_pos, end_pos, 2)

        # Label for decisions
        if self.start.tipo == "decision":
            mid_x = (start_pos[0] + end_pos[0]) // 2
            mid_y = (start_pos[1] + end_pos[1]) // 2
            font = pygame.font.SysFont('Arial', 12)
            label = font.render(self.label, True, (255, 255, 255))
            surface.blit(label, (mid_x - 10, mid_y - 10))

    def to_dict(self):
        return {
            'start_id': self.start.id,
            'end_id': self.end.id,
            'label': self.label
        }


def save_graph():
    root = Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        initialfile="diagrama_flujo.txt"
    )

    if not file_path:
        return False

    try:
        with open(file_path, 'w') as f:
            f.write("DIAGRAMA_DE_FLUJO\n")
            f.write(f"Total_grafos:{len(functions)}\n")
            f.write(f"Ultimo_ID_grafo:{id_graph}\n")
            f.write(f"Ultimo_ID_nodo:{id_counter}\n\n")

            for graph in functions:
                f.write(f"===GRAFO_ID:{graph.id}===\n")
                f.write(f"Raiz_ID:{graph.head.id}\n")

                # Guardar nodos
                f.write("NODOS:\n")
                for nodo in graph.adyacencia:
                    shape = getattr(nodo, 'shape', None)
                    tipo_str = shape.tipo if shape else nodo.tipo
                    texto = shape.texto if shape else nodo.informacion
                    x = shape.x if shape else 0
                    y = shape.y if shape else 0
                    f.write(f"{nodo.id}|{tipo_str}|{texto}|{x}|{y}|{graph.id}\n")

                # Guardar aristas
                f.write("ARISTAS:\n")
                for destino in graph.aristas:
                    for origen in graph.aristas[destino]:
                        label = getattr(graph, 'etiquetas', {}).get((origen, destino), "")
                        tipo_origen = graph.get_tipo(origen)
                        tipo_destino = graph.get_tipo(destino)
                        f.write(f"{origen}->{destino}|{tipo_origen}|{tipo_destino}|{label}\n")

                # Guardar variables
                if hasattr(graph, 'variables'):
                    f.write("VARIABLES:\n")
                    for name, typ in graph.variables.items():
                        f.write(f"{typ} {name}\n")

                f.write("\n")

        texto_panel_derecho[0] = f"Diagrama guardado: {os.path.basename(file_path)}"
        return True

    except Exception as e:
        texto_panel_derecho[0] = f"Error al guardar: {str(e)}"
        return False


def load_graph():
    global id_counter, id_graph, functions, work_shapes, connections

    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        title="Seleccionar archivo"
    )
    if not file_path:
        return False

    try:
        # Resetear estructuras
        functions = []
        work_shapes = []
        connections = []
        shapes_by_id = {}
        node_by_id = {}
        temp_shapes = []
        graph_map = {}

        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        current_section = None
        current_graph = None
        root_id = None

        for line in lines:
            if line.startswith("DIAGRAMA_DE_FLUJO"):
                continue
            elif line.startswith("Total_grafos:"):
                continue
            elif line.startswith("Ultimo_ID_grafo:"):
                id_graph = int(line.split(":")[1]) + 1
            elif line.startswith("Ultimo_ID_nodo:"):
                id_counter = int(line.split(":")[1]) + 1
            elif line.startswith("===GRAFO_ID:"):
                graph_id = int(line.split(":")[1])
                current_graph = Grafodirigido(None, graph_id)
                functions.append(current_graph)
                graph_map[graph_id] = current_graph
            elif line.startswith("Raiz_ID:"):
                root_id = int(line.split(":")[1])
            elif line == "NODOS:":
                current_section = "NODOS"
            elif line == "ARISTAS:":
                current_section = "ARISTAS"
            elif line == "VARIABLES:":
                current_section = "VARIABLES"
            elif "|" in line and current_section == "NODOS":
                parts = line.split("|")
                node_id = int(parts[0])
                tipo_str = parts[1]
                texto = parts[2]
                x = int(parts[3])
                y = int(parts[4])
                g_id = int(parts[5])

                tipo = {
                    "entrada": 1, "salida": 2, "proceso": 3,
                    "decision": 4, "fin": 5, "llamada": 6
                }.get(tipo_str, 0)

                shape = WorkShape(tipo_str, x, y, texto)
                shape.id = node_id
                shape.graph_id = g_id
                shape.shape_tipo = tipo

                node = Node(node_id, tipo, texto, shape)
                shapes_by_id[node_id] = (node, shape)
                temp_shapes.append(shape)

                graph = graph_map[g_id]
                graph.agregar_vertice_nodo(node)
                if node.id == root_id:
                    graph.head = node

            elif "->" in line and current_section == "ARISTAS":
                origin_str, rest = line.split("->")
                origin_id = int(origin_str.strip())
                dest_id, tipo_o, tipo_d, label = (rest.split("|") + ["", "", ""])[:4]
                dest_id = int(dest_id.strip())
                label = label.strip()

                if origin_id in shapes_by_id and dest_id in shapes_by_id:
                    origin_node, origin_shape = shapes_by_id[origin_id]
                    dest_node, dest_shape = shapes_by_id[dest_id]
                    graph_id = origin_shape.graph_id
                    graph = graph_map[graph_id]

                    graph.agregar_arista(origin_id, dest_id)
                    conn = Connection(origin_shape, dest_shape)
                    conn.label = label
                    connections.append(conn)

            elif current_section == "VARIABLES":
                parts = line.split()
                if len(parts) >= 2:
                    var_type, var_name = parts[0], parts[1]
                    if not hasattr(current_graph, 'variables'):
                        current_graph.variables = {}
                    current_graph.variables[var_name] = var_type

        work_shapes = temp_shapes
        texto_panel_derecho[0] = f"Diagrama cargado: {os.path.basename(file_path)}"
        return True

    except Exception as e:
        texto_panel_derecho[0] = f"Error al cargar archivo: {str(e)}"
        return False


def compilada():
    global functions, texto_panel_derecho

    if not functions:
        return

    # Generate code for all graphs
    c_code = ""


    for graph in functions:
        graph.generate_code_C()
        c_code += graph.code_c + "\n\n"

        # These would be uncommented when implemented
        # graph.generate_code_python()
        # py_code += graph.code_py + "\n\n"

        # graph.generate_code_asm()
        # asm_code += graph.code_asm + "\n\n"

    # Update right panel text
    texto_panel_derecho = [
        c_code,
    ]

    return texto_panel_derecho


def draw_text_panels(surface):
    panel_x = WIDTH - PANEL_RIGHT_WIDTH + 10
    font = pygame.font.SysFont('Arial', 12)

    for i, text in enumerate(texto_panel_derecho):
        y_pos = 20 + i * 180
        pygame.draw.rect(surface, PANEL_COLOR, (panel_x, y_pos, PANEL_RIGHT_WIDTH - 20, 150), border_radius=5)
        lines = text.split('\n')
        for j, line in enumerate(lines):
            if j < 10:  # Limit to 10 lines per panel to avoid overflow
                text_surface = font.render(line, True, TEXT_COLOR)
                surface.blit(text_surface, (panel_x + 10, y_pos + 20 + j * 20))

    # Buttons
    btn_y = HEIGHT - 100

    # Compile button
    compile_btn_rect = pygame.Rect(panel_x, btn_y, PANEL_RIGHT_WIDTH - 20, 40)
    pygame.draw.rect(surface, (0, 150, 0), compile_btn_rect, border_radius=5)
    btn_text = font.render("COMPILAR", True, (255, 255, 255))
    surface.blit(btn_text, (panel_x + 100000 // 2, btn_y + 10))

    # Save button
    save_btn_rect = pygame.Rect(panel_x, btn_y + 50, (PANEL_RIGHT_WIDTH - 25) // 2, 30)
    pygame.draw.rect(surface, (100, 100, 200), save_btn_rect, border_radius=5)
    save_text = font.render("GUARDAR", True, (255, 255, 255))
    surface.blit(save_text, (panel_x + ((PANEL_RIGHT_WIDTH - 25) // 2 - save_text.get_width()) // 2, btn_y + 60))

    # Load button
    load_btn_rect = pygame.Rect(panel_x + (PANEL_RIGHT_WIDTH - 25) // 2 + 5, btn_y + 50, (PANEL_RIGHT_WIDTH - 25) // 2,
                                30)
    pygame.draw.rect(surface, (200, 100, 100), load_btn_rect, border_radius=5)
    load_text = font.render("CARGAR", True, (255, 255, 255))
    surface.blit(load_text, (
    panel_x + (PANEL_RIGHT_WIDTH - 25) // 2 + 5 + ((PANEL_RIGHT_WIDTH - 25) // 2 - load_text.get_width()) // 2,
    btn_y + 60))

    return compile_btn_rect, save_btn_rect, load_btn_rect


def draw_texto_instructivo(surface):
    font = pygame.font.SysFont('Arial', 12)
    y_pos = HEIGHT - 220
    for i, instruction in enumerate(texto_instructivo):
        text = font.render(instruction, True, TEXT_COLOR)
        surface.blit(text, (10, y_pos + i * 20))


# Initialize template shapes
template_shapes = []
for i, shape_type in enumerate(SHAPE_TYPES):
    template_shapes.append(TemplateShape(shape_type, 20, 20 + i * 80))

# Initialize work area
work_shapes = []
connections = []
selected_shape = None
dragging_template = None
creating_connection = False
connection_start = None
active_text_edit = None
ctrl_pressed = False
buttons_rect = None

# Create initial main graph
initial_shape = WorkShape("inicio", PANEL_LEFT_WIDTH + 100, 100)
work_shapes.append(initial_shape)

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard handling
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                ctrl_pressed = True
            elif event.key == pygame.K_DELETE and selected_shape:
                # Remove shape and its connections
                work_shapes.remove(selected_shape)
                connections = [c for c in connections if c.start != selected_shape and c.end != selected_shape]

                # Remove from graph
                for graph in functions:
                    if graph.eliminar_por_id(selected_shape.id):
                        break

                selected_shape = None
            elif event.key == pygame.K_g:  # Save with G key
                save_graph()
            elif event.key == pygame.K_c:  # Load with C key
                load_graph()
            elif active_text_edit and active_text_edit.editing:
                if event.key == pygame.K_RETURN:
                    active_text_edit.stop_editing()
                    active_text_edit = None
                elif event.key == pygame.K_BACKSPACE:
                    active_text_edit.edit_text = active_text_edit.edit_text[:-1]
                else:
                    active_text_edit.edit_text += event.unicode

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                ctrl_pressed = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if active_text_edit:
                    active_text_edit.stop_editing()
                    active_text_edit = None

                if mouse_pos[0] < PANEL_LEFT_WIDTH:
                    for shape in template_shapes:
                        if shape.clickeada(mouse_pos):
                            # Create new work shape at mouse position
                            x = mouse_pos[0] - shape.width // 2
                            y = mouse_pos[1] - shape.height // 2

                            # Ensure it's in the work area
                            x = max(x, PANEL_LEFT_WIDTH)
                            x = min(x, WIDTH - PANEL_RIGHT_WIDTH - shape.width)
                            y = max(y, 0)
                            y = min(y, HEIGHT - shape.height)

                            dragging_template = WorkShape(shape.tipo, x, y)
                            break

                elif PANEL_LEFT_WIDTH < mouse_pos[0] < WIDTH - PANEL_RIGHT_WIDTH:
                    for shape in reversed(work_shapes):
                        if shape.clickeada(mouse_pos):
                            selected_shape = shape
                            shape.selected = True

                            if not ctrl_pressed:
                                shape.dragging = True
                                shape.drag_offset = (mouse_pos[0] - shape.x, mouse_pos[1] - shape.y)

                            for s in work_shapes:
                                if s != shape:
                                    s.selected = False

                            if ctrl_pressed:
                                creating_connection = True
                                connection_start = shape
                            break

                elif buttons_rect:
                    compile_rect, save_rect, load_rect = buttons_rect
                    if compile_rect.collidepoint(mouse_pos):
                        compilada()
                    elif save_rect.collidepoint(mouse_pos):
                        save_graph()
                    elif load_rect.collidepoint(mouse_pos):
                        load_graph()

            elif event.button == 3:  # Right click
                if PANEL_LEFT_WIDTH < mouse_pos[0] < WIDTH - PANEL_RIGHT_WIDTH:
                    for shape in reversed(work_shapes):
                        if shape.clickeada(mouse_pos):
                            if active_text_edit:
                                active_text_edit.stop_editing()
                            shape.start_editing()
                            active_text_edit = shape
                            break

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if dragging_template and PANEL_LEFT_WIDTH < mouse_pos[0] < WIDTH - PANEL_RIGHT_WIDTH:
                    work_shapes.append(dragging_template)
                    dragging_template = None

                for shape in work_shapes:
                    shape.dragging = False

                # Finish connection
                if creating_connection and selected_shape:
                    for shape in work_shapes:
                        if shape != connection_start and shape.clickeada(mouse_pos):
                            connections.append(Connection(connection_start, shape))
                            break
                    creating_connection = False
                    connection_start = None

        elif event.type == pygame.MOUSEMOTION:
            if dragging_template:
                dragging_template.x = mouse_pos[0] - dragging_template.width // 2
                dragging_template.y = mouse_pos[1] - dragging_template.height // 2

            if not ctrl_pressed:
                for shape in work_shapes:
                    if shape.dragging:
                        shape.x = mouse_pos[0] - shape.drag_offset[0]
                        shape.y = mouse_pos[1] - shape.drag_offset[1]

    # Drawing
    screen.fill(DARK_BG)

    # Draw panels
    pygame.draw.rect(screen, PANEL_COLOR, (0, 0, PANEL_LEFT_WIDTH, HEIGHT))
    pygame.draw.rect(screen, PANEL_COLOR, (WIDTH - PANEL_RIGHT_WIDTH, 0, PANEL_RIGHT_WIDTH, HEIGHT))

    # Draw template shapes
    for shape in template_shapes:
        shape.draw(screen)

    draw_texto_instructivo(screen)

    # Draw work area
    work_area = pygame.Rect(PANEL_LEFT_WIDTH, 0, WORK_AREA_WIDTH, HEIGHT)
    pygame.draw.rect(screen, (20, 20, 20), work_area)

    # Draw connections
    for connection in connections:
        connection.draw(screen)

    # Draw work shapes
    for shape in work_shapes:
        shape.draw(screen)

    buttons_rect = draw_text_panels(screen)

    # Draw dragging template
    if dragging_template:
        dragging_template.draw(screen)

    # Draw connection in progress
    if creating_connection and selected_shape:
        if selected_shape.tipo == "decision":
            if connections and connections[-1].start == selected_shape:
                start_pos = (selected_shape.x + selected_shape.width // 2, selected_shape.y + selected_shape.height)
            else:
                start_pos = (selected_shape.x + selected_shape.width, selected_shape.y + selected_shape.height // 2)
        elif selected_shape.tipo == "entrada":
            start_pos = (selected_shape.x + selected_shape.width, selected_shape.y + selected_shape.height // 2)
        elif selected_shape.tipo == "salida":
            start_pos = (selected_shape.x, selected_shape.y + selected_shape.height // 2)
        else:
            start_pos = (selected_shape.x + selected_shape.width // 2, selected_shape.y + selected_shape.height // 2)

        pygame.draw.line(screen, (255, 255, 255), start_pos, mouse_pos, 2)

    # Connection mode indicator
    if ctrl_pressed:
        font = pygame.font.SysFont('Arial', 16)
        mode_text = font.render("MODO CONEXIÓN", True, (255, 100, 100))
        screen.blit(mode_text, (WIDTH // 2 - mode_text.get_width() // 2, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()