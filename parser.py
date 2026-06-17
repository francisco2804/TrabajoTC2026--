from lexer import analizar_lexico

PATRONES = {
#gramatica

    "INGRESAR": [
        "INGRESAR",
        "PRODUCTO",
        "NUM_INT"
    ],

    "RETIRAR": [
        "RETIRAR",
        "PRODUCTO",
        "NUM_INT"
    ],

    "CONSULTAR": [
        "CONSULTAR",
        "PRODUCTO"
    ],

    "AJUSTAR": [
        "AJUSTAR",
        "PRODUCTO",
        "NUM_INT"
    ],

    "TRANSFERIR": [
        "TRANSFERIR",
        "PRODUCTO",
        "DESDE",
        "UBICACION",
        "HACIA",
        "UBICACION",
        "NUM_INT"
    ],

    "RECIBIR_LOTE": [
        "RECIBIR_LOTE",
        "PRODUCTO",
        "LOTE",
        "PROVEEDOR",
        "NUM_INT"
    ]
}

def validar_sintaxis(linea):

    resultado_lexico = analizar_lexico(linea)

    if resultado_lexico["errores"]:

        return {
            "valido": False,
            "motivo": "Existen errores léxicos"
        }

    tokens_obtenidos = [

        token["token"]

        for token in resultado_lexico["tokens"]

    ]

    operacion = tokens_obtenidos[0]

    if operacion not in PATRONES:

        return {
            "valido": False,
            "motivo": "Operación desconocida"
        }

    patron_esperado = PATRONES[operacion]
    #tf

    for i in range(len(patron_esperado)):
        if i >= len(tokens_obtenidos):

            return {
                "valido": False,
                "error": "Faltan elementos",
                "posicion": i + 1,
                "esperado": patron_esperado[i]
        }

        if tokens_obtenidos[i] != patron_esperado[i]:

            return {
                "valido": False,
                "error": "Token inesperado",
                "posicion": i + 1,
                "esperado": patron_esperado[i],
                "recibido": tokens_obtenidos[i]
            }
        
        if len(tokens_obtenidos) > len(patron_esperado):
            return {
                "valido": False,
                "error": "Demasiados elementos"
            }

    return {
        "valido": True,
        "motivo": "Estructura válida"
    }


#pruebas x2

if __name__ == "__main__":

    prueba = (
        "RECIBIR_LOTE "
        "PROD-FRU-001 "
        "LOT-TAC-202505 "
        "PROV-AGRO-001 "
        "50"
    )

    print(
        validar_sintaxis(prueba)
    ) 
    