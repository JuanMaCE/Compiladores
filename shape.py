import pygame



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
            pygame.draw.ellipse(surface, color, r) if self.tipo in ["INICIO", "FIN"] else pygame.draw.rect(surface,
                                                                                                           color, r,
                                                                                                           border_radius=10)
            pygame.draw.ellipse(surface, (0, 0, 0), r, 2) if self.tipo in ["INICIO", "FIN"] else pygame.draw.rect(
                surface, (0, 0, 0), r, 2, border_radius=10)

        text_surface = font.render(self.texto, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=r.center)
        surface.blit(text_surface, text_rect)

