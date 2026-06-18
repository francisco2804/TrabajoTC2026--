from lexer import analizar_lexico
from parser import PATRONES

def construir_arbol(linea):
    resultado_lexico = analizar_lexico(
        linea
    )

    tokens = resultado_lexico[
        "tokens"
    ]

    operacion = tokens[0][
        "token"
    ]

    patron = PATRONES[
        operacion
    ]

    hijos = []

    for i in range(
        len(patron)
    ):
        hijos.append({

            "simbolo":
            patron[i],

            "lexema":
            tokens[i][
                "lexema"
            ]
        })

    return {
        "raiz": "S",

        "operacion":
        operacion,

        "hijos":
        hijos
    }

