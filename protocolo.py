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