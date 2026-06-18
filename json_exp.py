import json

def generar_json(operacion):
    return json.dumps(
        operacion,
        indent=4,
        ensure_ascii=False
    )

