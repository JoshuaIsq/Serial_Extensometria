from PySide6.QtWidgets import QWidget, QVBoxLayout


class PaginaAquisição(QWidget):
    def __init__(self, gráfico, channel_bar, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(8)

        # Controles na parte superior da página.
        self.main_layout.addWidget(channel_bar)

        # O gráfico recebe o espaço restante.
        self.main_layout.addWidget(gráfico, 1)