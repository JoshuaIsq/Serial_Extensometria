from datetime import datetime
from pathlib import Path
import time

class GravadorTxt:

    def __init__(self):
        self.arquivo = None
        self.caminho = None
        self.atualização = 0.0

    @property
    def active(self):
        return self.arquivo is not None

    #Cria um arquivo novo a cada gravação
    def start(self, paste):
        if self.active:
            return

        paste = Path(paste)
        paste.mkdir(parents=True, exist_ok=True)
        time_now = datetime.now().strftime("%Y -%m -%d -H, %M-%S_f")
        self.caminho = paste / f"LOG_{time_now}.txt"
        self.arquivo = self.caminho.open(
            mode="x",
            encoding="utf-8",
            newline="",
        )
        self.arquivo.write("timestamp;canal_1;canal_2;canal_3;canal_4")
        self.arquivo.flush()
        self.atualização = time.perf_counter()

    #Somente escreve quando há uma gravação ativa
    def register(self, valores): 
        if not self.active:
            return

        timestamp = datetime.now().isoformat(sep=' ', timespec='milliseconds')
        field = [f"{valor:.6f}" for valor in valores]
        line = ';'.join([timestamp]+field)
        self.arquivo.write(line + "\n")
        now = time.perf_counter()

        if now - self.atualização >= 1:
            self.arquivo.flush()
            self.atualização = now

    def stop(self):
        if not self.active:
            return

        arquivo = self.arquivo
        self.arquivo = None
        arquivo.close()
