from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsLineItem,
    QGraphicsTextItem, QTextEdit, QDockWidget, QToolBar, QListWidget,
    QListWidgetItem, QMenu, QInputDialog, QPushButton
)
from PyQt6.QtGui import (
    QBrush, QPen, QColor, QPolygonF, QPainterPath, QFont, QPainter,
    QTextCursor, QAction, QTransform, QIcon
)
from PyQt6.QtCore import Qt, QPointF, QLineF, QRectF, pyqtSignal
import sys
from collections import defaultdict


class DiagramItem(QGraphicsItem):
    def __init__(self, item_type, parent=None):
        super().__init__(parent)
        self.item_type = item_type
        self.lines = []
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self.text_item = QGraphicsTextItem(self)
        self.text_item.setPlainText(item_type)
        self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.text_item.setDefaultTextColor(Qt.GlobalColor.black)
        self.text_item.setFont(QFont("Arial", 10))

        self.width = 120
        self.height = 60
        self.adjust_size()

    def adjust_size(self):
        text_width = self.text_item.boundingRect().width() + 20
        text_height = self.text_item.boundingRect().height() + 20
        self.width = max(self.width, text_width)
        self.height = max(self.height, text_height)
        self.center_text()

    def center_text(self):
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(
            (self.width - text_rect.width()) / 2,
            (self.height - text_rect.height()) / 2
        )

    def add_line(self, line):
        self.lines.append(line)

    def remove_line(self, line):
        if line in self.lines:
            self.lines.remove(line)

    def remove_all_lines(self):
        for line in list(self.lines):
            if line.scene():
                line.scene().removeItem(line)
        self.lines.clear()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            for line in self.lines:
                line.update_position()
        return super().itemChange(change, value)

    def get_connection_point(self, to_item=None):
        my_center = self.scenePos() + QPointF(self.width / 2, self.height / 2)

        if to_item is None:
            return my_center

        other_center = to_item.scenePos() + QPointF(to_item.width / 2, to_item.height / 2)
        direction = other_center - my_center
        if direction.x() == 0 and direction.y() == 0:
            return my_center

        length = (direction.x() ** 2 + direction.y() ** 2) ** 0.5
        direction = QPointF(direction.x() / length, direction.y() / length)

        if abs(direction.x()) > abs(direction.y()):
            x = self.width / 2 if direction.x() > 0 else -self.width / 2
            y = x * direction.y() / direction.x()
        else:
            y = self.height / 2 if direction.y() > 0 else -self.height / 2
            x = y * direction.x() / direction.y()

        return my_center + QPointF(x, y)


class FlowItem(DiagramItem):
    def __init__(self, label, item_type, shape="rect", color="#D5F5E3"):
        super().__init__(item_type)
        self.label = label
        self.shape = shape
        self.color = color
        self.set_text(label)

        if shape == "diamond":
            self.width = 100
            self.height = 80
        elif shape == "ellipse":
            self.width = 100
            self.height = 60

        self.adjust_size()

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))

        if self.isSelected():
            painter.setPen(QPen(QColor("#3498DB"), 3, Qt.PenStyle.DashLine))

        if self.shape == "rect":
            painter.drawRoundedRect(0, 0, self.width, self.height, 10, 10)
        elif self.shape == "trapezoid":
            path = QPainterPath()
            path.moveTo(self.width * 0.2, 0)
            path.lineTo(self.width * 0.8, 0)
            path.lineTo(self.width, self.height)
            path.lineTo(0, self.height)
            path.closeSubpath()
            painter.drawPath(path)
        elif self.shape == "parallelogram":
            path = QPainterPath()
            path.moveTo(self.width * 0.2, 0)
            path.lineTo(self.width, 0)
            path.lineTo(self.width * 0.8, self.height)
            path.lineTo(0, self.height)
            path.closeSubpath()
            painter.drawPath(path)
        elif self.shape == "diamond":
            path = QPainterPath()
            path.moveTo(self.width / 2, 0)
            path.lineTo(self.width, self.height / 2)
            path.lineTo(self.width / 2, self.height)
            path.lineTo(0, self.height / 2)
            path.closeSubpath()
            painter.drawPath(path)
        elif self.shape == "ellipse":
            painter.drawEllipse(0, 0, self.width, self.height)

    def set_text(self, text):
        self.text_item.setPlainText(text)
        self.adjust_size()

    def shape(self):
        path = QPainterPath()
        if self.shape == "ellipse":
            path.addEllipse(0, 0, self.width, self.height)
        elif self.shape == "diamond":
            path.moveTo(self.width / 2, 0)
            path.lineTo(self.width, self.height / 2)
            path.lineTo(self.width / 2, self.height)
            path.lineTo(0, self.height / 2)
            path.closeSubpath()
        elif self.shape == "trapezoid":
            path.moveTo(self.width * 0.2, 0)
            path.lineTo(self.width * 0.8, 0)
            path.lineTo(self.width, self.height)
            path.lineTo(0, self.height)
            path.closeSubpath()
        elif self.shape == "parallelogram":
            path.moveTo(self.width * 0.2, 0)
            path.lineTo(self.width, 0)
            path.lineTo(self.width * 0.8, self.height)
            path.lineTo(0, self.height)
            path.closeSubpath()
        else:  # rect
            path.addRoundedRect(0, 0, self.width, self.height, 10, 10)
        return path

    def edit_text(self):
        text, ok = QInputDialog.getText(
            None, "Editar texto", "Nuevo texto:", text=self.text_item.toPlainText()
        )
        if ok and text:
            self.set_text(text)


class DiagramLine(QGraphicsLineItem):
    def __init__(self, start_item, end_item, parent=None):
        super().__init__(parent)
        self.start_item = start_item
        self.end_item = end_item
        self.setPen(QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.SolidLine))
        self.setZValue(-1)

        # Conectar la línea a los items
        self.start_item.add_line(self)
        self.end_item.add_line(self)

        self.update_position()

    def update_position(self):
        if not (self.start_item and self.end_item):
            return

        start_point = self.start_item.get_connection_point(self.end_item)
        end_point = self.end_item.get_connection_point(self.start_item)
        self.setLine(QLineF(start_point, end_point))

    def remove_from_items(self):
        if self.start_item:
            self.start_item.remove_line(self)
        if self.end_item:
            self.end_item.remove_line(self)


class FlowChartScene(QGraphicsScene):
    item_removed = pyqtSignal(QGraphicsItem)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 800, 600)
        self.setBackgroundBrush(QBrush(Qt.GlobalColor.white))
        self.current_mode = "select"
        self.connection_start_item = None
        self.temp_line = None

    def set_mode(self, mode):
        self.current_mode = mode
        if self.connection_start_item:
            self.connection_start_item.setSelected(False)
            self.connection_start_item = None
        if self.temp_line:
            self.removeItem(self.temp_line)
            self.temp_line = None

    def mousePressEvent(self, event):
        items_at_pos = self.items(event.scenePos())
        item = next((i for i in items_at_pos if isinstance(i, FlowItem)), None)

        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_mode == "connect":
                if isinstance(item, FlowItem):
                    if self.connection_start_item is None:
                        self.connection_start_item = item
                        item.setSelected(True)
                        self.temp_line = QGraphicsLineItem()
                        self.temp_line.setPen(QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.DashLine))
                        self.addItem(self.temp_line)
                    else:

                        if item != self.connection_start_item:
                            line = DiagramLine(self.connection_start_item, item)
                            self.addItem(line)

                        self.connection_start_item.setSelected(False)
                        self.removeItem(self.temp_line)
                        self.connection_start_item = None
                        self.temp_line = None
                    return

            elif self.current_mode == "erase":
                if item:
                    if isinstance(item, DiagramLine):
                        item.remove_from_items()
                        self.removeItem(item)
                    elif isinstance(item, FlowItem):
                        self.removeItem(item)
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.current_mode == "connect" and self.connection_start_item and self.temp_line:
            start_point = self.connection_start_item.get_connection_point(None)
            end_pos = event.scenePos()
            self.temp_line.setLine(QLineF(start_point, end_pos))

        super().mouseMoveEvent(event)

    def get_execution_sequence(self):
        nodes = []
        edges = defaultdict(list)

        for item in self.items():
            if isinstance(item, FlowItem):
                nodes.append(item)
            elif isinstance(item, DiagramLine):
                edges[item.start_item].append(item.end_item)

        start_nodes = [n for n in nodes if n.item_type == "INICIO"]
        if not start_nodes:
            return []

        visited = set()
        sequence = []

        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            sequence.append(node)
            for neighbor in edges.get(node, []):
                dfs(neighbor)

        dfs(start_nodes[0])
        return sequence


class ShapeListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.add_shapes()
        self.setDragEnabled(True)

    def add_shapes(self):
        shapes = [
            ("INICIO", "ellipse", "#E74C3C"),
            ("FIN", "ellipse", "#E74C3C"),
            ("PROCESO", "rect", "#3498DB"),
            ("DECISIÓN", "diamond", "#2ECC71"),
            ("ENTRADA", "parallelogram", "#9B59B6"),
            ("SALIDA", "trapezoid", "#F39C12")
        ]

        for name, shape, color in shapes:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, (shape, color, name))
            self.addItem(item)


class FlowChartApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diagrama de Flujo - Compilador")
        self.setGeometry(100, 100, 1200, 700)
        self.initUI()

    def initUI(self):
        self.setup_central_widget()
        self.setup_tools_panel()
        self.setup_toolbar()
        self.statusBar().showMessage("Modo Selección")

    def setup_central_widget(self):
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)

        self.scene = FlowChartScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        layout.addWidget(self.view, 3)

        output_panel = QVBoxLayout()

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(False)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1px solid #ccc;
                font-family: monospace;
            }
        """)
        output_panel.addWidget(QLabel("Código Generado:"))
        output_panel.addWidget(self.output_text)

        btn_generate = QPushButton("Generar Secuencia")
        btn_generate.clicked.connect(self.generate_sequence)
        output_panel.addWidget(btn_generate)

        layout.addLayout(output_panel, 1)
        self.setCentralWidget(central_widget)

    def setup_tools_panel(self):
        dock = QDockWidget("Formas", self)
        shape_widget = QWidget()
        layout = QVBoxLayout(shape_widget)

        self.shape_list = ShapeListWidget()
        self.shape_list.itemDoubleClicked.connect(self.add_shape)
        layout.addWidget(self.shape_list)

        btn_select = QPushButton("Modo Selección")
        btn_select.clicked.connect(self.set_select_mode)

        btn_connect = QPushButton("Modo Conexión")
        btn_connect.clicked.connect(self.set_connect_mode)

        btn_erase = QPushButton("Modo Borrar")
        btn_erase.clicked.connect(self.set_erase_mode)

        layout.addWidget(btn_select)
        layout.addWidget(btn_connect)
        layout.addWidget(btn_erase)
        layout.addStretch()

        dock.setWidget(shape_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

    def setup_toolbar(self):
        toolbar = self.addToolBar("Herramientas")

        act_clear = QAction(QIcon.fromTheme("edit-clear"), "Limpiar Todo", self)
        act_clear.triggered.connect(self.clear_diagram)
        toolbar.addAction(act_clear)

    def add_shape(self, item):
        shape, color, item_type = item.data(Qt.ItemDataRole.UserRole)
        new_item = FlowItem(item_type, item_type, shape, color)

        view_center = self.view.mapToScene(self.view.viewport().rect().center())
        new_item.setPos(view_center.x() - new_item.width / 2,
                        view_center.y() - new_item.height / 2)

        self.scene.addItem(new_item)

    def set_select_mode(self):
        self.scene.set_mode("select")
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.statusBar().showMessage("Modo Selección")

    def set_connect_mode(self):
        self.scene.set_mode("connect")
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.statusBar().showMessage("Modo Conexión - Seleccione el primer elemento")

    def set_erase_mode(self):
        self.scene.set_mode("erase")
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.statusBar().showMessage("Modo Borrar - Haga clic en elementos para eliminarlos")

    def generate_sequence(self):
        sequence = self.scene.get_execution_sequence()
        if not sequence:
            self.output_text.setPlainText("No se encontró una secuencia válida.\nAsegúrese de tener un nodo INICIO.")
            return

        output = "Secuencia de ejecución:\n"
        for i, item in enumerate(sequence, 1):
            output += f"{i}. {item.item_type}: {item.text_item.toPlainText()}\n"

        self.output_text.setPlainText(output)

    def clear_diagram(self):
        self.scene.clear()
        self.output_text.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = FlowChartApp()
    window.show()
    sys.exit(app.exec())