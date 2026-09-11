"""
Módulo responsável pela leitura da porta serial em uma thread separada,
permitindo que a interface continue respondendo enquanto os dados chegam.

Classe LeitorSerial:
Herda de QThread e realiza a conexão, a leitura e as tentativas de reconexão.

Sinais:
- data_received: envia o tempo decorrido e a lista dos quatro valores recebidos.
- state: envia mensagens sobre o estado da conexão para a interface.

Método __init__:
Inicializa a thread e armazena a porta e a taxa de comunicação nos atributos
self.port e self.baudrate.

Os valores padrão são COM3 e 115200 baud, mas podem ser substituídos quando
o objeto é criado. A reconexão é automática na porta configurada; ainda não
existe identificação automática da placa em outras portas.

Método run:
É executado em segundo plano quando o método start() da thread é chamado.

O laço externo verifica isInterruptionRequested(). Enquanto não houver um
pedido explícito de encerramento, a tarefa continua tentando se conectar.
Essa verificação não detecta, por si só, a retirada do cabo ou qualquer erro.

Dentro do try, o bloco with serial.Serial(...) abre e configura a porta.
Ao sair desse bloco, inclusive por uma exceção durante a leitura, a conexão
é fechada. O timeout de 0,1 segundo limita a espera de cada leitura.

Com a porta aberta, o laço interno recebe bytes na variável trecho e os
acumula em pendent. Se nenhum byte chegar, a tarefa continua aguardando.
Uma leitura pode conter parte de uma linha ou várias linhas completas.

O laço que procura quebras de linha separa as mensagens completas e mantém
em pendent o fragmento ainda incompleto.

A variável descart permite ignorar os bytes até a primeira quebra de linha
após a conexão, evitando interpretar um possível fragmento inicial.
Isso também descarta a primeira linha caso ela tenha chegado completa.

Cada linha aceita é decodificada de bytes para texto usando UTF-8. Depois,
line_interpreter(), do módulo protocolo, verifica seu formato e converte
os quatro campos em números.

Se o resultado não for None, ele é armazenado em valores e enviado pelo
sinal data_received, junto ao tempo decorrido desde a primeira linha válida.

O tempo é calculado com time.perf_counter() no computador. Portanto, indica
o momento de processamento da mensagem recebida, não o instante exato da
aquisição no ESP32. A referência de tempo é preservada nas reconexões.

Linhas maiores que 512 bytes são ignoradas. Se o fragmento pendente superar
esse limite, ele é descartado, e a leitura busca a próxima quebra de linha
para recuperar o alinhamento das mensagens.

Falhas de abertura ou comunicação são tratadas sem encerrar a tarefa.
A variável waiting evita repetir o mesmo aviso a cada tentativa.
Após a falha, a tarefa aguarda aproximadamente um segundo antes de tentar
novamente, verificando a cada 100 ms se houve pedido de encerramento.

Uma configuração serial inválida informa o problema pelo sinal state
e encerra o método.
"""


import time
import serial
from PySide6.QtCore import QThread, Signal
from protocolo import line_interpreter

class LeitorSerial (QThread):
    data_received = Signal(float, list)  
    state = Signal(str)  

    def __init__(self, port='COM3', baudrate=115200, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate

    def run(self):
        start = None
        waiting = False

        #Enquanto o software estiver aberto ele tenta se conectar
        while not self.isInterruptionRequested():
            try:
                with serial.Serial(self.port, self.baudrate, timeout=0.1) as conection: #Abrir a porta serial
                    waiting = False
                    pendent = b"" #Inicializa uma variavel de bytes vazia que é alimentada em seguida
                    descart = True
                    self.state.emit(f"Conectado: {self.port} | {self.baudrate} baud")

                    while not self.isInterruptionRequested(): #Mantem a conexão infinito 
                        quantidade = max(1, min(conection.in_waiting, 4096))
                        trecho = conection.read(quantidade) #Recebe os dados da serial 

                        if not trecho:
                            continue
                        pendent += trecho 

                        while b"\n" in pendent:
                            line, pendent =pendent.split(b"\n", 1)

                            if descart: #Caso se conecte a serial no meio do caminho, considera que a linha é lixo e a ignora, podendo ser somada depois
                                descart = False
                                continue

                            if len(line) > 512: #Se tiver mais de 512bytes em uma linha algo deu ruim
                                continue

                            try:
                                text = line.decode("utf-8") #Transforma o dado em valor legivel
                            except UnicodeDecodeError:
                                continue

                            valores = line_interpreter(text) #joga no modulo protocolo, o que garante que as mensagens sejam de 4 em 4

                            if valores is None:
                                continue

                            now = time.perf_counter()

                            if start is None:
                                start = now

                            self.data_received.emit(now - start, valores)

                if len(pendent) > 512:
                    pendent = b""
                    descart = True

            except (serial.SerialException, OSError):
                # Avisa uma vez por período de indisponibilidade.
                if not waiting:
                    self.state.emit(
                        f"{self.port} indisponível. "
                        "Aguardando conexão..."
                    )
                    waiting = True

            except ValueError as erro:
                self.state.emit(
                    f"Configuração serial inválida: {erro}"
                )
                return

            # Aguarda cerca de 1 segundo antes de tentar novamente.
            # Verifica a cada 100 ms se você fechou a janela.
            for _ in range(10):
                if self.isInterruptionRequested():
                    return

                self.msleep(100)

