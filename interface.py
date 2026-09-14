import sys
from collections import deque

from PySide6.QtCore import QTimer, Slot, Qt
from leitor_serial import LeitorSerial
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QToolBar, QCheckBox, 
                               QPushButton,  QWidget, QVBoxLayout, QTabBar, QStackedWidget, QLabel, QListWidget)

import pyqtgraph as pg
from pagina_aquisição import PaginaAquisição

class MainWindow(QMainWindow):

    @Slot(bool)
    def alternar_pausa(self, pausado):
        self.paused = pausado

        if pausado:
            self.pause_button.setText("Retomar gráfico")
        else:
            self.pause_button.setText("Pausar gráfico")

            # Mostra os dados recentes assim que retomar.
            self.atualizar_grafico()

    def __init__(self):
        super().__init__() #inicializa os recursos de uma janela qt

        self.setWindowTitle("SerialMonitor ISQ Brasil") #define o título da janela
        self.resize(1000, 600) #define o tamanho da janela

        # Configurações do gráfico
        self.grafico = pg.PlotWidget() #cria o widget do gráfico
        self.grafico.setBackground('w') #cor
        self.grafico.setWindowTitle("Gráfico de Dados") 
        self.grafico.setLabel('bottom', 'Time', units='s') 
        self.grafico.setLabel('left', 'Value') 

        self.grafico.showGrid(x=True, y=True, alpha=0.3) #exibe a grade do gráfico
        self.grafico.addLegend() #exibe a legenda do gráfico

        self.grafico.setXRange(0, 10) 
        self.grafico.enableAutoRange('y')

        colors = ["#1565C0", "#C62828", "#2E7D32", "#7B1FA2"]

        self.curvas = [] #lista para armazenar as curvas do gráfico

        for i, cor in enumerate(colors):
            curva = self.grafico.plot(pen=pg.mkPen(cor, width=2), name=f"Canal {i+1}") #cria uma curva no gráfico
            self.curvas.append(curva) #adiciona a curva na lista de curvas

        #Barra de controle da pagina de aquisição
        self.channel_bar = QToolBar("Controle de vizualização", self)
        self.channel_bar.setMovable(False)

        #Chama a função alternar pausa para mudar o estado do botão
        self.paused = True
        self.pause_button = QPushButton("Iniciar")
        self.pause_button.setCheckable(True)
        self.pause_button.setChecked(True)
        self.pause_button.toggled.connect(self.alternar_pausa) 
        self.channel_bar.addWidget(self.pause_button)
        self.channel_bar.addSeparator

        #Seleção de canais
        self.seletor = []
        for i, curva in enumerate(self.curvas):
            checkbox = QCheckBox(f"Canal {i + 1}")
            checkbox.setChecked(True)
            checkbox.toggled.connect(lambda checked, c=curva: c.setVisible(checked))
            self.channel_bar.addWidget(checkbox)
            self.channel_bar.addSeparator()
            self.seletor.append(checkbox)


        # Histórico usado somente para desenhar o gráfico.
        self.tempos = deque(maxlen=10000)

        self.valores_canais = [
            deque(maxlen=10000) for _ in range(4)
        ]

        # Redesenha o gráfico a cada 50 ms.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.atualizar_grafico)
        self.timer.start(50)

        self.statusBar().showMessage("Abrindo COM3...")

        # Cria e conecta a tarefa de leitura.
        self.leitor = LeitorSerial(
            port="COM3",
            baudrate=115200,
            parent=self,
        )

        self.leitor.data_received.connect(self.receber_dados)
        self.leitor.state.connect(self.mostrar_estado)
        self.navigate()
        self.leitor.start()

    @Slot(float, list)

    def receber_dados(self, tempo, valores):
        # Guarda o tempo e os quatro canais na mesma posição.
        self.tempos.append(tempo)

        for i, valor in enumerate(valores):
            self.valores_canais[i].append(valor)

        # Mantém apenas os últimos 10 segundos.
        while self.tempos and self.tempos[0] < tempo - 10:
            self.tempos.popleft()

            for canal in self.valores_canais:
                canal.popleft()

    def atualizar_grafico(self):
        if self.paused or not self.tempos:
            return

        tempos = list(self.tempos)

        for i, curva in enumerate(self.curvas):
            curva.setData(tempos, list(self.valores_canais[i]), connect="finite")

        fim = max(10, tempos[-1])

        self.grafico.setXRange(fim - 10, fim, padding=0,)

    @Slot(str)
    def mostrar_estado(self, mensagem):
        self.statusBar().showMessage(mensagem)

    def closeEvent(self, event):

        # Pede que a leitura termine e libere a COM3.
        self.leitor.requestInterruption()

        if not self.leitor.wait(1000):
            event.ignore()
            self.statusBar().showMessage("Encerrando a serial...")
            QTimer.singleShot(100, self.close)
            return

        self.timer.stop()
        event.accept()

    def navigate(self):
        self.area_central = QWidget()

        # Cria o layout vertical para a área central
        layout = QVBoxLayout(self.area_central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        #Menu Lateral
        self.lateral_menu = QTabBar()
        self.lateral_menu.setExpanding(False)
        self.lateral_menu.addTab("Aquisição")
        self.lateral_menu.addTab("Configurações")
        self.lateral_menu.addTab("Em breve")

        #Guarda as paginas em um QStackedWidget para alternar entre elas
        self.paginas = QStackedWidget()

        #Pagina principal
        self.pagina_aquisicao = PaginaAquisição(self.grafico, self.channel_bar)
        self.paginas.addWidget(self.pagina_aquisicao)

        #Pagina 1: Provisorio
        self.pag1 = QLabel("Próximos menus")
        self.pag1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pag1.setWordWrap(True)
        self.paginas.addWidget(self.pag1)

        #Página 2: espaço para funcionalidades futuras.
        self.pag2 = QLabel("Próximos menus.")
        self.pag2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pag2.setWordWrap(True)
        self.paginas.addWidget(self.pag2)

        # O menu ocupa sua largura definida.
        # As páginas recebem o restante do espaço disponível.
        layout.addWidget(self.lateral_menu)
        layout.addWidget(self.paginas, 1)

        self.setCentralWidget(self.area_central)

        # Conecta a seleção do menu à troca de página.
        self.lateral_menu.currentChanged.connect(self.paginas.setCurrentIndex)
        self.lateral_menu.setCurrentIndex(0)
        self.paginas.setCurrentIndex(0)

if __name__ == "__main__":
    aplicacao = QApplication(sys.argv)

    janela = MainWindow()
    janela.show()

    sys.exit(aplicacao.exec())