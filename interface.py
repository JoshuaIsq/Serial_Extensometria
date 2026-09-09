import sys

from PySide6.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__() #inicializa os recursos de uma janela qt

        self.setWindowTitle("SerialMonitor ISQ Brasil") #define o título da janela
        self.resize(1000, 600) #define o tamanho da janela

        # Configurações do gráfico
        self.grafico = pg.PlotWidget() #cria o widget do gráfico
        self.grafico.setBackground('w') #define a cor de fundo do gráfico
        self.setCentralWidget(self.grafico) #define o widget do gráfico como widget central


if __name__ == "__main__":
    aplicacao = QApplication(sys.argv)

    janela = MainWindow()
    janela.show()

    sys.exit(aplicacao.exec())