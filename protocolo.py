def line_interpretation(text):

    part = text.strip().split(',')

    if len(part) != 4:
        return None  # Retorna None se a linha não tiver exatamente 4 partes, passível de mudança em placas futuras

    try:
        valores = [int(text_size) for text_size in part]  # Converte cada parte para inteiro e os transforma em uma lista

    except ValueError:
        return None  # Retorna None se houver algum erro na conversão para inteiro

    return valores  #
