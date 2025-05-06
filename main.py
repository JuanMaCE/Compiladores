from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtCore import Qt, QPointF
import sys

class DraggableEllipse(QGraphicsEllipseItem):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.setBrush(QBrush(QColor("skyblue")))
        self.setFlags(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)

app = QApplication(sys.argv)

scene = QGraphicsScene()
view = QGraphicsView(scene)
view.setWindowTitle("Arrastrar Figura")
view.setRenderHint(view.renderHints())  # Suaviza el dibujo

# Crear figura
ellipse = DraggableEllipse(0, 0, 50, 50)
scene.addItem(ellipse)

view.setScene(scene)
view.setFixedSize(400, 300)
view.show()

sys.exit(app.exec())
