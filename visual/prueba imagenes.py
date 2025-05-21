import pygame
import sys
import os

pygame.init()
WIDTH, HEIGHT = 1400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Editor de Diagramas de Flujo")

DARK_BG = (0, 0, 0)  # Fondo negro
PANEL_COLOR = (30, 30, 30)  # Paneles gris oscuro
TEXT_COLOR = (255, 255, 255)  # Texto blanco (general)
SHAPE_TEXT_COLOR = (0, 0, 0)  # Texto negro solo para objetos
ACCENT_COLOR = (0, 100, 200)  # Azul para selección
SHAPE_COLOR = (200, 200, 200)  # Color de respaldo para formas

PANEL_LEFT_WIDTH = 250
PANEL_RIGHT_WIDTH = 300
WORK_AREA_WIDTH = WIDTH - PANEL_LEFT_WIDTH - PANEL_RIGHT_WIDTH

SHAPE_TYPES = ["inicio", "fin", "decision", "entrada", "salida", "proceso", "llamada"]


def cargar_imagenes():
    images = {}
    for shape in SHAPE_TYPES:
        try:
            image_path = os.path.join("C:\programas python\COMPILADORES\Compiladores\images", f"{shape}.png")
            image = pygame.image.load(image_path).convert_alpha()

            # si se hace mas grande se ve feo
            base_width = 85
            aspect_ratio = image.get_height() / image.get_width()
            new_height = int(base_width * aspect_ratio)
            images[shape] = pygame.transform.scale(image, (base_width, new_height))
        except Exception as e:
            print(f"Error cargando imagen para {shape}: {e}")
            surf = pygame.Surface((120, 60), pygame.SRCALPHA)
            pygame.draw.rect(surf, SHAPE_COLOR, (0, 0, 120, 60), border_radius=8)
            images[shape] = surf
    return images


shape_images = cargar_imagenes()

texto_panel_derecho = [
    "Código en C generado",
    "Código en Python generado",
    "Resultado en Ensamblador"
]

texto_instructivo = [
    "INSTRUCCIONES:",
    "1. Arrastra formas del panel izquierdo",
    "2. Haz clic derecho para editar texto",
    "3. Ctrl + clic para conectar formas(mantener)",
    "4. Botón COMPILAR para generar código",
    "5. Suprimir: borrar forma seleccionada"
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

    def draw(self, surface):
        # Dibujar imagen
        surface.blit(self.image, (self.x, self.y))

        # Dibujar texto en negro (solo para objetos)
        font = pygame.font.SysFont('Arial', 14)
        if self.editing:
            text = font.render(self.edit_text, True, (255, 0, 0))  # Rojo al editar
            pygame.draw.rect(surface, (240, 240, 240),
                             (self.x + 5, self.y + self.height // 2 - 10,
                              self.width - 10, 20))
        else:
            text = font.render(self.texto, True, SHAPE_TEXT_COLOR)

        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        surface.blit(text, text_rect)

        # Resaltar selección
        if self.selected:
            pygame.draw.rect(surface, ACCENT_COLOR,
                             (self.x - 5, self.y - 5, self.width + 10, self.height + 10),
                             2, border_radius=12)

    def clickeada(self, pos):
        # Crear máscara para detección precisa
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


class Connection:
    def __init__(self, start_shape, end_shape):
        self.start = start_shape
        self.end = end_shape
        self.label = ""

        if start_shape.tipo == "decision":
            existing_connections = sum(1 for c in connections if c.start == start_shape)
            self.is_first_connection = (existing_connections == 0)
            self.label = "Sí" if self.is_first_connection else "No"

    def draw(self, surface):
        if self.start.tipo == "decision":
            if self.is_first_connection:  
                start_pos = (self.start.x + self.start.width, self.start.y + self.start.height // 2)
            else:  # Abajo
                start_pos = (self.start.x + self.start.width // 2, self.start.y + self.start.height)
        elif self.start.tipo == "entrada":
            start_pos = (self.start.x + self.start.width, self.start.y + self.start.height // 2)
        elif self.start.tipo == "salida":
            start_pos = (self.start.x, self.start.y + self.start.height // 2)
        else:
            start_pos = (self.start.x + self.start.width // 2, self.start.y + self.start.height // 2)

        end_pos = (self.end.x + self.end.width // 2, self.end.y + self.end.height // 2)

        # Dibuja la linea de conexiones 
        pygame.draw.line(surface, (255, 255, 255), start_pos, end_pos, 2)

        # Etiqueta para decisiones
        if self.start.tipo == "decision":
            mid_x = (start_pos[0] + end_pos[0]) // 2
            mid_y = (start_pos[1] + end_pos[1]) // 2
            font = pygame.font.SysFont('Arial', 12)
            label = font.render(self.label, True, (255, 255, 255))
            surface.blit(label, (mid_x - 10, mid_y - 10))


def compilada(texto_c, texto_py, texto_ens):
    texto_panel_derecho[
        0] = texto_c
    texto_panel_derecho[1] = texto_py
    texto_panel_derecho[
        2] = texto_ens
    return texto_panel_derecho


def draw_text_panels(surface):
    panel_x = WIDTH - PANEL_RIGHT_WIDTH + 10
    font = pygame.font.SysFont('Arial', 12)

    for i, text in enumerate(texto_panel_derecho):
        y_pos = 20 + i * 180
        pygame.draw.rect(surface, PANEL_COLOR, (panel_x, y_pos, PANEL_RIGHT_WIDTH - 20, 150), border_radius=5)
        lines = text.split('\n')
        for j, line in enumerate(lines):
            text_surface = font.render(line, True, TEXT_COLOR)  # Texto blanco en paneles
            surface.blit(text_surface, (panel_x + 10, y_pos + 20 + j * 20))

    compile_btn_rect = pygame.Rect(panel_x, HEIGHT - 50, PANEL_RIGHT_WIDTH - 20, 40)
    pygame.draw.rect(surface, (0, 150, 0), compile_btn_rect, border_radius=5)
    btn_text = font.render("COMPILAR", True, (255, 255, 255))  # Texto blanco en botón
    surface.blit(btn_text, (panel_x + (PANEL_RIGHT_WIDTH - 20 - btn_text.get_width()) // 2, HEIGHT - 40))

    return compile_btn_rect


def draw_texto_instructivo(surface):
    font = pygame.font.SysFont('Arial', 12)
    y_pos = HEIGHT - 180  # Más espacio para instrucciones
    for i, instruction in enumerate(texto_instructivo):
        text = font.render(instruction, True, TEXT_COLOR)  # Texto blanco en instrucciones
        surface.blit(text, (10, y_pos + i * 20))


template_shapes = []
for i, shape_type in enumerate(SHAPE_TYPES):
    template_shapes.append(TemplateShape(shape_type, 20, 20 + i * 80))

work_shapes = []
connections = []
selected_shape = None
dragging_template = None
creating_connection = False
connection_start = None
active_text_edit = None
ctrl_pressed = False
compile_btn_rect = None  # Rectángulo del botón compilar

# Bucle principal
clock = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Manejo de teclado
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                ctrl_pressed = True
            elif event.key == pygame.K_DELETE and selected_shape:
                # ELimina formas y conexiones hay que considerar el grafo
                work_shapes.remove(selected_shape)
                connections = [c for c in connections if c.start != selected_shape and c.end != selected_shape]
                selected_shape = None
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
            if event.button == 1:  # Click izquierdo
                if active_text_edit:
                    active_text_edit.stop_editing()
                    active_text_edit = None

                if mouse_pos[0] < PANEL_LEFT_WIDTH:
                    for shape in template_shapes:
                        if shape.clickeada(mouse_pos):
                            dragging_template = WorkShape(shape.tipo, mouse_pos[0], mouse_pos[1])
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

                elif compile_btn_rect and compile_btn_rect.collidepoint(mouse_pos):
                    # AQUI ROGER ROGER GAY
                    texto_c = ""
                    texto_py = ""
                    texto_ens = ""
                    compilada(texto_c, texto_py, texto_ens)

            elif event.button == 3:  # Click derecho
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
                    work_shapes.append(WorkShape(
                        dragging_template.tipo,
                        mouse_pos[0] - dragging_template.width // 2,
                        mouse_pos[1] - dragging_template.height // 2,
                        dragging_template.texto
                    ))
                dragging_template = None

                for shape in work_shapes:
                    shape.dragging = False

                # Finalizar conexión
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

            # Mover formas si no hay ztrl para editarlo
            if not ctrl_pressed:
                for shape in work_shapes:
                    if shape.dragging:
                        shape.x = mouse_pos[0] - shape.drag_offset[0]
                        shape.y = mouse_pos[1] - shape.drag_offset[1]

    screen.fill(DARK_BG)  # Fondo negro

    pygame.draw.rect(screen, PANEL_COLOR, (0, 0, PANEL_LEFT_WIDTH, HEIGHT))
    pygame.draw.rect(screen, PANEL_COLOR, (WIDTH - PANEL_RIGHT_WIDTH, 0, PANEL_RIGHT_WIDTH, HEIGHT))

    # Formas del panel izquierdo
    for shape in template_shapes:
        shape.draw(screen)

    draw_texto_instructivo(screen)
    work_area = pygame.Rect(PANEL_LEFT_WIDTH, 0, WORK_AREA_WIDTH, HEIGHT)
    pygame.draw.rect(screen, (20, 20, 20), work_area)  # Fondo gris muy oscuro

    for connection in connections:
        connection.draw(screen)

    for shape in work_shapes:
        shape.draw(screen)

    compile_btn_rect = draw_text_panels(screen)

    # Forma que se está arrastrando
    if dragging_template:
        dragging_template.draw(screen)

    # Conexión en progreso
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

        pygame.draw.line(screen, (255, 255, 255), start_pos, mouse_pos, 2)  # Línea blanca

    # Indicador de modo conexión
    if ctrl_pressed:
        font = pygame.font.SysFont('Arial', 16)
        mode_text = font.render("MODO CONEXIÓN", True, (255, 100, 100))
        screen.blit(mode_text, (WIDTH // 2 - mode_text.get_width() // 2, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()