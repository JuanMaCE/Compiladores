from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
    QGraphicsPolygonItem, QGraphicsTextItem, QTextEdit, QGraphicsEllipseItem,
    QGraphicsPathItem, QMenu, QInputDialog
)
from PyQt6.QtGui import (
    QBrush, QPen, QColor, QPolygonF, QPainterPath, QFont, QPainter,
    QTextCursor, QAction, QTransform
)
from PyQt6.QtCore import Qt, QPointF, QLineF, QRectF, pyqtSignal
import sys
import math


class Arrow(QGraphicsPathItem):
    def __init__(self, start_item, end_item, parent=None):
        super().__init__(parent)
        self.start_item = start_item
        self.end_item = end_item
        self.setZValue(-1)
        self.setPen(QPen(QColor("#2C3E50"), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        self.setBrush(QBrush(QColor("#2C3E50")))
        self.arrow_size = 10
        self.update_position()

    def update_position(self):
        if not self.start_item or not self.end_item:
            return

        # Obtener puntos de conexión entre los elementos
        start_pos = self.start_item.sceneBoundingRect().center()
        end_pos = self.end_item.sceneBoundingRect().center()

        # Calcular línea entre los centros
        line = QLineF(start_pos, end_pos)

        # Ajustar los puntos para que la flecha conecte con los bordes
        start_rect = self.start_item.sceneBoundingRect()
        end_rect = self.end_item.sceneBoundingRect()
        start_point = self.calculate_intersection(start_rect, line)
        end_point = self.calculate_intersection(end_rect, line.reversed())

        if not start_point or not end_point:
            start_point = start_pos
            end_point = end_pos
        # Linea de flecha no sirve ptm
        self.set_line(start_point, end_point)
    def calculate_intersection(self, rect, line):
        path = QPainterPath()
        path.addRect(rect)
        shape = path.toFillPolygon()
        polygon = QPolygonF(shape)

        for i in range(polygon.size()):
            p1 = polygon.at(i)
            p2 = polygon.at((i + 1) % polygon.size())
            poly_line = QLineF(p1, p2)
            intersect_point = QPointF()
            if line.intersects(poly_line, intersect_point) == QLineF.IntersectType.BoundedIntersection:
                return intersect_point
        return None

    def set_line(self, start_point, end_point):
        path = QPainterPath()
        path.moveTo(start_point)
        path.lineTo(end_point)
        angle = math.atan2(end_point.y() - start_point.y(), end_point.x() - start_point.x())
        arrow_p1 = end_point - QPointF(math.cos(angle + math.pi / 6) * self.arrow_size,
            math.sin(angle + math.pi / 6) * self.arrow_size)
        arrow_p2 = end_point - QPointF(math.cos(angle - math.pi / 6) * self.arrow_size,
            math.sin(angle - math.pi / 6) * self.arrow_size)
        path.moveTo(end_point)
        path.lineTo(arrow_p1)
        path.moveTo(end_point)
        path.lineTo(arrow_p2)
        self.setPath(path)


class FlowItem(QGraphicsItem):
    def __init__(self, label, item_type, shape="rect", color="#D5F5E3"):
        super().__init__()
        self.label = label
        self.item_type = item_type
        self.shape = shape
        self.color = color
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)

        # Texto editable Igual guarda de que tipo es osea inicio y asi
        self.text_item = QGraphicsTextItem(label, self)
        self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.text_item.setDefaultTextColor(QColor("#2C3E50"))
        self.text_item.setPos(10, 10)
        # Esto si lo podemos ir viendo
        # Configurar fuente
        font = QFont("Arial", 8)
        self.text_item.setFont(font)
        # Conexiones
        self.input_arrows = []
        self.output_arrows = []
        # Ajustar tamaño según el texto
        self.adjust_size()
    def adjust_size(self):
        text_width = self.text_item.boundingRect().width() + 20
        text_height = self.text_item.boundingRect().height() + 20

        # Tamaño mínimo
        self.width = max(100, text_width)
        self.height = max(50, text_height)
        # Centrar texto
        text_x = (self.width - self.text_item.boundingRect().width()) / 2
        text_y = (self.height - self.text_item.boundingRect().height()) / 2
        self.text_item.setPos(text_x, text_y)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        # Dibujar sombra pero no me convence
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 50))
        painter.drawRoundedRect(3, 3, self.width, self.height, 10, 10)
        # Dibujar forma principal
        if self.isSelected():
            painter.setPen(QPen(QColor("#3498DB"), 3, Qt.PenStyle.DashLine))
        else:
            painter.setPen(QPen(QColor("#2C3E50"), 2))
        painter.setBrush(QBrush(QColor(self.color)))
        self.draw_shape(painter)

    def draw_shape(self, painter):
        if self.shape == "rect":
            painter.drawRoundedRect(0, 0, self.width, self.height, 10, 10)
        elif self.shape == "trapezoid":
            points = [
                QPointF(self.width * 0.2, 0),
                QPointF(self.width * 0.8, 0),
                QPointF(self.width, self.height),
                QPointF(0, self.height)
            ]
            painter.drawPolygon(QPolygonF(points))
        elif self.shape == "parallelogram":
            points = [
                QPointF(self.width * 0.2, 0),
                QPointF(self.width, 0),
                QPointF(self.width * 0.8, self.height),
                QPointF(0, self.height)
            ]
            painter.drawPolygon(QPolygonF(points))
        elif self.shape == "diamond":
            points = [
                QPointF(self.width / 2, 0),
                QPointF(self.width, self.height / 2),
                QPointF(self.width / 2, self.height),
                QPointF(0, self.height / 2)
            ]
            painter.drawPolygon(QPolygonF(points))
        elif self.shape == "ellipse":
            painter.drawEllipse(0, 0, self.width, self.height)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for arrow in self.input_arrows + self.output_arrows:
                if arrow in self.scene().items():
                    arrow.update_position()

        return super().itemChange(change, value)

    def get_text(self):
        return f"{self.item_type}: {self.text_item.toPlainText()}"

    def mouseDoubleClickEvent(self, event):
        self.text_item.setFocus()
        cursor = self.text_item.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        self.text_item.setTextCursor(cursor)
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu()
        delete_action = QAction("Eliminar", self)
        delete_action.triggered.connect(lambda: self.scene().remove_item(self))
        edit_action = QAction("Editar texto", self)
        edit_action.triggered.connect(self.edit_text)
        menu.addAction(edit_action)
        menu.addAction(delete_action)
        menu.exec(event.screenPos())
    def edit_text(self):
        text, ok = QInputDialog.getText(
            None, "Editar texto", "Nuevo texto:", text=self.text_item.toPlainText()
        )
        if ok:
            self.text_item.setPlainText(text)
            self.adjust_size()
            self.update()


class FlowChartScene(QGraphicsScene):
    item_removed = pyqtSignal(QGraphicsItem)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 800, 600)
        self.setBackgroundBrush(QBrush(QColor("#F5F7FA")))

        # Variables para la conexión
        self.start_item = None
        self.temp_arrow = None

    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())

        if event.button() == Qt.MouseButton.LeftButton:
            if isinstance(item, FlowItem):
                if self.start_item is None:
                    # Primer clic - seleccionar elemento de inicio
                    self.start_item = item
                    item.setSelected(True)
                else:
                    # Segundo clic - crear conexión
                    if item != self.start_item:
                        arrow = Arrow(self.start_item, item)
                        self.addItem(arrow)
                        self.start_item.output_arrows.append(arrow)
                        item.input_arrows.append(arrow)
                        self.start_item = None
                    else:
                        self.start_item = None
            else:
                self.start_item = None
                self.clearSelection()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.start_item and not self.temp_arrow:
            # Crear flecha temporal durante el arrastre peeeeero no conecta con otro bloque
            self.temp_arrow = Arrow(self.start_item, None)
            self.addItem(self.temp_arrow)

        if self.temp_arrow:
            start_pos = self.start_item.sceneBoundingRect().center()
            end_pos = event.scenePos()

            path = QPainterPath()
            path.moveTo(start_pos)
            path.lineTo(end_pos)
            # Dibujar punta de flecha
            angle = math.atan2(end_pos.y() - start_pos.y(), end_pos.x() - start_pos.x())
            arrow_size = 10
            arrow_p1 = end_pos - QPointF(math.cos(angle + math.pi / 6) * arrow_size,
                math.sin(angle + math.pi / 6) * arrow_size)
            arrow_p2 = end_pos - QPointF(math.cos(angle - math.pi / 6) * arrow_size,
                math.sin(angle - math.pi / 6) * arrow_size)

            path.moveTo(end_pos)
            path.lineTo(arrow_p1)
            path.moveTo(end_pos)
            path.lineTo(arrow_p2)
            self.temp_arrow.setPath(path)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.temp_arrow:
            item = self.itemAt(event.scenePos(), QTransform())
            if isinstance(item, FlowItem) and item != self.start_item:
                # Crear conexión permanente
                self.removeItem(self.temp_arrow)
                arrow = Arrow(self.start_item, item)
                self.addItem(arrow)
                self.start_item.output_arrows.append(arrow)
                item.input_arrows.append(arrow)
            else:
                # Eliminar flecha temporal pero igual no establece aun la fija
                self.removeItem(self.temp_arrow)

            self.temp_arrow = None
            self.start_item = None

        super().mouseReleaseEvent(event)

    def remove_item(self, item):
        for arrow in item.input_arrows[:]:
            if arrow.start_item and arrow in arrow.start_item.output_arrows:
                arrow.start_item.output_arrows.remove(arrow)
            self.removeItem(arrow)
        for arrow in item.output_arrows[:]:
            if arrow.end_item and arrow in arrow.end_item.input_arrows:
                arrow.end_item.input_arrows.remove(arrow)
            self.removeItem(arrow)

        self.removeItem(item)
        self.item_removed.emit(item)


class FlowChartApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("COMPILADOR FINAL")
        self.setGeometry(100, 100, 1200, 700)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        self.setup_tools_panel(layout)
        # Panel del centro
        self.setup_flowchart_view(layout)
        # Panel derecho se acuerdan de lo que dijo el inge de agregar el ensamblador
        self.setup_output_panel(layout)

    def setup_tools_panel(self, main_layout):
        tools_panel = QVBoxLayout()
        tools_panel.setSpacing(10)
        main_layout.addLayout(tools_panel, 1)
        title = QLabel("Elementos del Diagrama")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        tools_panel.addWidget(title)
        shapes = {
            "INICIO/FIN": ("ellipse", "#E74C3C"),
            "PROCESO": ("rect", "#3498DB"),
            "DECISIÓN": ("diamond", "#2ECC71"),
            "ENTRADA": ("parallelogram", "#9B59B6"),
            "SALIDA": ("trapezoid", "#F39C12")
        }

        for label, (shape, color) in shapes.items():
            btn = QPushButton(label)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
            """)
            btn.clicked.connect(lambda _, s=shape, c=color, l=label: self.add_shape(s, c, l.split("/")[0]))
            tools_panel.addWidget(btn)
        tools_panel.addStretch()
        clear_btn = QPushButton("Limpiar Diagrama")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        clear_btn.clicked.connect(self.clear_diagram)
        tools_panel.addWidget(clear_btn)

    def darken_color(self, hex_color, factor=0.8):
        """Oscurece un color hexadecimal"""
        color = QColor(hex_color)
        return color.darker(int(100 / factor)).name()

    def setup_flowchart_view(self, main_layout):
        self.scene = FlowChartScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.view.setStyleSheet("background: transparent; border: 1px solid #BDC3C7; border-radius: 4px;")
        main_layout.addWidget(self.view, 3)

    def setup_output_panel(self, main_layout):
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        main_layout.addLayout(right_panel, 1)
        title = QLabel("Código Generado")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_panel.addWidget(title)
        self.output_text = QTextEdit()
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #ECF0F1;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                padding: 5px;
                font-family: monospace;
            }
        """)
        self.output_text.setReadOnly(False)
        right_panel.addWidget(self.output_text, 1)
        compile_btn = QPushButton("Generar Secuencia")
        compile_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ECC71;
            }
        """)
        compile_btn.clicked.connect(self.compile_flowchart)
        right_panel.addWidget(compile_btn)
        export_btn = QPushButton("Exportar Diagrama")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980B9;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498DB;
            }
        """)
        export_btn.clicked.connect(self.export_diagram)
        right_panel.addWidget(export_btn)

    def add_shape(self, shape, color, label):
        item = FlowItem(label, label, shape, color)
        item.setPos(200, 200)
        self.scene.addItem(item)

    def compile_flowchart(self):
        flow = []
        for item in self.scene.items():
            if isinstance(item, FlowItem):
                flow.append(item.get_text())
        flow.sort(key=lambda x: x.startswith("INICIO"), reverse=True)
        self.output_text.setPlainText("Secuencia de acciones:\n\n" + "\n".join(flow))

    def clear_diagram(self):
        self.scene.clear()
        self.output_text.clear()

    def export_diagram(self):
        self.output_text.append("Exportando diagrama... (función no implementada)")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    app.setStyleSheet("""
        QWidget {
            font-family: Arial;
        }
        QMenu {
            background-color: white;
            border: 1px solid #BDC3C7;
        }
        QMenu::item:selected {
            background-color: #3498DB;
            color: white;
        }
    """)

    window = FlowChartApp()
    window.show()
    sys.exit(app.exec())