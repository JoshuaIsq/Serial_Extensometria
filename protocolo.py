"""
Módulo responsável por interpretar as linhas recebidas pela comunicação
serial. Não abre a porta nem atualiza o gráfico.

Função line_interpreter:
Recebe uma linha de texto e retorna uma lista com quatro valores float,
ou None quando a linha não apresenta o formato esperado.

Primeiro, remove espaços e quebras de linha das extremidades do texto.
Em seguida, divide a linha pelas vírgulas, formando uma lista de campos.

Verifica se existem exatamente quatro campos, um para cada canal.
Se a quantidade for diferente, retorna None.

Tenta converter cada campo para float. Essa conversão aceita números
negativos e casas decimais escritas com ponto. Se algum campo não puder
ser convertido, a função retorna None.

Depois, verifica quais valores são finitos usando math.isfinite().
Valores não finitos, como infinito e NaN, são representados por math.nan,
permitindo que o gráfico mostre uma lacuna naquele canal.

A presença de NaN em um canal não descarta os valores dos outros canais.

Essa verificação não determina se o valor está fisicamente correto,
calibrado ou dentro da faixa válida do sensor. Um número finito pode
representar saturação ou uma leitura inadequada e ainda ser aceito.

A função não realiza calibração, filtragem ou conversão para tensão
mecânica. Seu papel é interpretar e validar o formato da mensagem.
"""

import math

def line_interpreter(text):
    part = text.strip().split(",")  

    if len(part) != 4:
        return None

    try: 
        values = [float(parte) for parte in part] 

    except ValueError:
        return None

    return [
        valor if math.isfinite(valor) else math.nan
        for valor in values
    ]