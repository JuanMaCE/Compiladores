import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsView, QGraphicsScene, QTextEdit, QGraphicsRectItem
)
from PyQt6.QtGui import QColor, QBrush, QPainter
from PyQt6.QtCore import Qt, pyqtSignal

# IMPORTACIONES DE FIGURAS PERSONALIZADAS
from create_figures import DraggableEllipse, DraggableRect, DiamondPathItem, Create_square_round, InclinedRectangle


class FlowChartScene(QGraphicsScene):
    item_removed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 800, 600)
        self.setBackgroundBrush(QColor("#F5F7FA"))


class FlowChartApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("COMPILADOR FINAL")
        self.setGeometry(100, 100, 1200, 700)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.setup_tools_panel(layout)
        self.setup_flowchart_view(layout)
        self.setup_output_panel(layout)

    def setup_tools_panel(self, main_layout):
        self.botones_menu = []
        tools_panel = QVBoxLayout()
        tools_panel.setSpacing(10)
        main_layout.addLayout(tools_panel, 1)

        title = QLabel("Elementos del Diagrama")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        tools_panel.addWidget(title)

        shapes = {
            "INICIO": ("ellipse", "#E74C3C"),
            "ENTRADA": ("parallelogram", "#9B59B6"),
            "SALIDA": ("trapezoid", "#F39C12"),
            "PROCESO": ("rect", "#3498DB"),
            "CONDICION": ("diamond", "#2ECC71"),
            "FINAL": ("ellipse", "#E74C3C"),
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
            self.botones_menu.append(btn)
            btn.clicked.connect(lambda _, l=label: self.add_element(l))
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
        clear_btn.clicked.connect(self.clear_output)
        tools_panel.addWidget(clear_btn)

    def setup_flowchart_view(self, main_layout):
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 2000, 2000)

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.TextAntialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
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
        compile_btn.clicked.connect(self.show_elements)
        right_panel.addWidget(compile_btn)

    def darken_color(self, hex_color, factor=0.8):
        color = QColor(hex_color)
        return color.darker(int(100 / factor)).name()

    def add_element(self, element_type):
        x, y = 100, 100
        width, height = 120, 60

        try:
            if element_type == "INICIO":
                item = DraggableEllipse(x, y, width, height, True, "INICIO")
            elif element_type == "ENTRADA":
                item = InclinedRectangle(x, y, width, height, 30, True, "Inclinado")
            elif element_type == "SALIDA":
                item = DraggableRect(x, y, width, height, True, "SALIDA")
            elif element_type == "PROCESO":
                item = Create_square_round(x, y, width, height, True, "PROCESO")
            elif element_type == "CONDICION":
                item = DiamondPathItem(x, y, width, height, True, "CONDICION")
            elif element_type == "FINAL":
                item = DraggableEllipse(x, y, width, height, True, "FINAL")
            else:
                raise ValueError("Elemento no reconocido")

            self.scene.addItem(item)
            print(f"Item agregado en posición: {item.pos()}")
            self.view.centerOn(item)

        except Exception as e:
            print(f"Error al agregar item: {str(e)}")
            self.output_text.append(f"Error: {str(e)}")

    def clear_output(self):
        self.output_text.clear()

    def show_elements(self):
        self.output_text.append("\nSecuencia de elementos creados:")
        # Aquí podrías recorrer los elementos de la escena:
        for item in self.scene.items():
            self.output_text.append(str(item))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet("QWidget { font-family: Arial; }")
    window = FlowChartApp()
    window.show()
    sys.exit(app.exec())
