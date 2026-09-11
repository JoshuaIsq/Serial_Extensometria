from PySide6.QtWidgets import QWidget, QVBoxLayout

class PaginaAquisição(QWidget):
    def __init__(self, gráfico, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.addWidget(gráfico)
        