from PyQt6.QtCore import Qt, QRectF, QLineF
from PyQt6.QtGui import QBrush, QColor, QPen, QFont, QPainterPath, QPainter, QMouseEvent
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsRectItem, QGraphicsPathItem, \
    QGraphicsView, QGraphicsLineItem, QMainWindow, QGraphicsScene


class DraggableEllipse(QGraphicsEllipseItem):
    def __init__(self, x, y, w, h, movable: bool, text: str):
        super().__init__(0, 0, w, h)  # Coordenadas relativas (0,0)
        self.setPos(x, y)  # Posición en la escena
        self.setBrush(QBrush(QColor("skyblue")))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        # Añadir texto centrado
        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setDefaultTextColor(Qt.GlobalColor.black)
        self.text_item.setFont(QFont("Arial", 10))
        # Centrar texto en el rectángulo
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(w/2 - text_rect.width()/2, h/2 - text_rect.height()/2)
        if movable:
            self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable)
            self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)


class CustomButton(QGraphicsRectItem):
    def __init__(self, x, y, w, h, text):
        super().__init__(x, y, w, h)
        self.setBrush(QBrush(QColor("green")))
        self.text = text

    def mousePressEvent(self, event):
        print(f"Botón '{self.text}' presionado!")
        super().mousePressEvent(event)


class DraggableRect(QGraphicsRectItem):
    def __init__(self, x, y, w, h, movable: bool, text: str):
        super().__init__(0, 0, w, h)  # Coordenadas relativas (0,0)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("blue")))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        # Añadir texto centrado
        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setDefaultTextColor(Qt.GlobalColor.white)
        self.text_item.setFont(QFont("Arial", 10))
        # Centrar texto en el rectángulo
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(w/2 - text_rect.width()/2, h/2 - text_rect.height()/2)
        if movable:
            self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
            self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)

class Create_square_round(QGraphicsPathItem):
    def __init__(self, x, y, w, h, movable: bool, text: str):
        print("me genere")
        super().__init__()
        path = QPainterPath()
        rect = QRectF(0, 0, w, h)
        path.addRoundedRect(rect, 20, 20)
        self.setPath(path)
        self.setBrush(QBrush(QColor("lightgreen")))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setPos(x, y)
        if movable:
            self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsMovable)
            self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable)
        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setDefaultTextColor(Qt.GlobalColor.black)
        self.text_item.setFont(QFont("Arial", 10))
        # Centrar texto en el rectángulo redondeado
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(w/2 - text_rect.width()/2, h/2 - text_rect.height()/2)

class DiamondPathItem(QGraphicsPathItem):
    def __init__(self, x, y, width, height, movable, text: str):
        super().__init__()

        path = QPainterPath()
        path.moveTo(width / 2, 0)  # Empezar arriba
        path.lineTo(width, height / 2)  # Derecha
        path.lineTo(width / 2, height)  # Abajo
        path.lineTo(0, height / 2)  # Izquierda
        path.closeSubpath()  # Cerrar el camino

        self.setPath(path)
        self.setPos(x, y)
        self.setBrush(QColor("magenta"))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        if movable:
            self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsMovable)
            self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable)


class InclinedRectangle(QGraphicsPathItem):
    def __init__(self, x, y, w, h, angle, movable: bool, text: str):
        super().__init__()

        path = QPainterPath()
        offset = h * 0.3

        path.moveTo(0, 0)
        path.lineTo(w, 0)
        path.lineTo(w + offset, h)
        path.lineTo(offset, h)
        path.closeSubpath()

        self.setPath(path)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("orange")))
        self.setPen(QPen(Qt.GlobalColor.black, 2))

        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setDefaultTextColor(Qt.GlobalColor.black)
        self.text_item.setFont(QFont("Arial", 10))


        text_rect = self.text_item.boundingRect()
        self.text_item.setPos((w + offset) / 2 - text_rect.width() / 2,
                              h / 2 - text_rect.height() / 2)

        if movable:
            self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsMovable)
            self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable)

def make_transparante_button(button):
    button.setStyleSheet("""
        QPushButton {
            background: transparent;  /* Fondo transparente */
            border: none;            /* Sin bordes */
            color: black;            /* Color del texto (ajústalo) */
            padding: 0px;            /* Elimina relleno interno */
        }
        QPushButton:hover {
            color: blue;             /* Color del texto al pasar el mouse */
        }
    """)


