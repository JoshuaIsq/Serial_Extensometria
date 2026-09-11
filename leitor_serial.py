import time
import serial

from PySide6.QtCore import QThread, Signal
from protocolo import line_interpreter

class LeitorSerial (QThread):
    data_received = Signal(float, list)  # Sinal para enviar os dados recebidos
    state = Signal(str)  # Sinal para enviar o estado da conexão

    def __init__(self, port='COM 3', baudrate=115200, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate

    def run(self):
        pendent = b""
        descart = False
        init = None

        try:
            with serial.Serial(self.port, self.baudrate, timeout=0.1) as conection:
                self.state.emit(f"Conectado: {self.port} | {self.baudrate} baud")

                while not self.isInterruptionRequested():
                    quant = max(1, min(conection.in_waiting, 4096))
                    tre = conection.read(quant)

                    if not tre:
                        continue

                    pendent += tre

                    while b"\n" in pendent:
                        line, pendent = pendent.split(b"\n", 1)

                        if descart:
                            descart = False
                            continue

                        if len(line) > 512:
                            continue

                        try:
                            texto = line.decode("utf-8")
                        except UnicodeDecodeError:
                            continue

                        values = line_interpreter(texto)

                        if values is None:
                            continue

                        agora = time.perf_counter()

                        # A primeira amostra recebida terá tempo zero.
                        if init is None:
                            init = agora

                        self.data_received.emit(
                            agora - init, values
                        )

                    # Evita acumular indefinidamente uma linha sem fim.
                    if len(pendent) > 512:
                        pendent = b""
                        descart = True

        except (serial.SerialException, OSError) as erro:
            self.estado.emit(f"Erro na serial: {erro}")