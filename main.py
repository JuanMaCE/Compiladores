from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsRectItem, \
    QGraphicsPathItem, QGraphicsTextItem, QPushButton, QGraphicsProxyWidget
from PyQt6.QtGui import QBrush, QColor, QPainterPath, QPen, QPainter, QFont
from PyQt6.QtCore import Qt, QRectF

class DraggableEllipse(QGraphicsEllipseItem):
    def __init__(self, x, y, w, h, movable: bool, text: str):
        super().__init__(0, 0, w, h)  # Coordenadas relativas (0,0)
        self.setPos(x, y)  # Posición en la escena
        self.setBrush(QBrush(QColor("skyblue")))
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        # Añadir texto centrado
        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setDefaultTextColor(Qt.GlobalColor.white)
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
    def __init__(self, x, y, width, height, movable):
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

def create_final(scene):
    button = Create_square_round(350, 350, 100, 50, True, "FIN")
    scene.addItem(button)

def create_decision(scene):
    print("hola mundo")
    button = DiamondPathItem(250, 250, 100, 50, True, "DECISION")
    scene.addItem(button)



def main():
    app = QApplication([])
    scene = QGraphicsScene()
    scene.setSceneRect(0, 0, 800, 600)

    view = QGraphicsView(scene)
    view.setWindowTitle("Arrastrar Figuras en PyQt6")
    view.setRenderHint(QPainter.RenderHint.Antialiasing)  # Suavizado activado
    view.setFixedSize(800, 600)

    # crear figuras

    rs_incio = Create_square_round(350, 50, 100, 50, False, "INICIO")
    DE = Create_square_round
    rs_fin = Create_square_round(60, 400, 100, 50, False, "FIN")

    ## decision
    diamond = DiamondPathItem(70, 200, 75, 75, False)

    bttn_create_decision = QPushButton() # 4
    bttn_create_decision.setFixedSize(100, 50)
    make_transparante_button(bttn_create_decision)
    proxy = QGraphicsProxyWidget(diamond)  # 5
    proxy.setWidget(bttn_create_decision)  # 6
    proxy.setPos(0, 0)
    bttn_create_decision.clicked.connect(lambda:create_decision(scene))

    ## final
    bttn_create_final = QPushButton() # 4
    bttn_create_final.setFixedSize(100, 50)
    make_transparante_button(bttn_create_final)
    proxy = QGraphicsProxyWidget(rs_fin)  # 5
    proxy.setWidget(bttn_create_final)  # 6
    proxy.setPos(0, 0)
    bttn_create_final.clicked.connect(lambda:create_final(scene))

    scene.addItem(diamond)


    scene.addItem(rs_incio)
    scene.addItem(rs_fin)

    view.show()
    app.exec()

if __name__ == "__main__":
    main()