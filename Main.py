import serial

from protocolo import line_interpretation

PORTA = 'COM3' 
BAUD_RATE = 115200


def main():
    try:
        with serial.Serial(PORTA, BAUD_RATE, timeout=1) as conection:
            print(f"Conexão estabelecida na porta {PORTA} com baud rate {BAUD_RATE}.")
            print('Aguardando dados (CNTRL+C para sair)...')

            line_pendent = b'' #Linha para guardar bytes até ter uma linha completa

            while True:
                # Lê os bytes disponíveis na porta serial
                trecho = conection.readline()  # Lê uma linha completa (terminada por \n)
                if not trecho:
                    continue  

                line_pendent += trecho  # Adiciona os bytes lidos à linha pendente

                if not line_pendent.endswith(b'\n'):
                    continue  # Se a linha não estiver completa, continua para a próxima iteração

                text = line_pendent.decode('utf-8', errors='replace').strip()  # Decodifica os bytes para string e remove espaços em branco

                line_pendent = b'' 

                if text: 
                    valores = line_interpretation(text)  # Interpreta a linha recebida

                    if valores is not None:
                        ch_1, ch_2, ch_3, ch_4 = valores #separa cada valor da lista text em valores por canal
                        print(
                                f"CH1: {ch_1} | "
                                f"CH2: {ch_2} | "
                                f"CH3: {ch_3} | "
                                f"CH4: {ch_4}")

    except serial.SerialException as e:
        print(f"Erro ao conectar na porta serial: {e}")

    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário.")

if __name__ == "__main__":
    main()