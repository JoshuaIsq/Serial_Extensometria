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
        self.grafico.setBackground('w') #cor
        self.setCentralWidget(self.grafico) #define o widget do gráfico como widget central
        self.grafico.setWindowTitle("Gráfico de Dados") 
        self.grafico.setLabel('bottom', 'Time', units='s') 
        self.grafico.setLabel('left', 'Value') 

        self.grafico.showGrid(x=True, y=True, alpha=0.3) #exibe a grade do gráfico
        self.grafico.addLegend() #exibe a legenda do gráfico

        self.grafico.setXRange(0, 10) 
        self.grafico.setYRange(0, 66000)

        colors = ["#1565C0", "#C62828", "#2E7D32", "#7B1FA2"]

        self.curvas = [] #lista para armazenar as curvas do gráfico

        for i, cor in enumerate(colors):
            curva = self.grafico.plot(pen=pg.mkPen(cor, width=2), name=f"Canal {i+1}") #cria uma curva no gráfico
            self.curvas.append(curva) #adiciona a curva na lista de curvas


if __name__ == "__main__":
    aplicacao = QApplication(sys.argv)

    janela = MainWindow()
    janela.show()

    sys.exit(aplicacao.exec())