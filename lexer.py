import re

TOKENS = [

    # Operaciones

    ("INGRESAR", r"^INGRESAR$"),

    ("RETIRAR", r"^RETIRAR$"),

    ("CONSULTAR", r"^CONSULTAR$"),

    ("AJUSTAR", r"^AJUSTAR$"),

    ("TRANSFERIR", r"^TRANSFERIR$"),

    ("RECIBIR_LOTE", r"^RECIBIR_LOTE$"),

    ("DESDE", r"^DESDE$"),

    ("HACIA", r"^HACIA$"),


    # Identificadores del dominio

    ("PRODUCTO", r"^PROD-[A-Z]{3}-\d{3}$"),

    ("LOTE", r"^LOT-[A-Z]{3}-\d{6}$"),

    ("PROVEEDOR", r"^PROV-[A-Z-]+-\d{3}$"),

    ("UBICACION", r"^ALM-[A-Z]\d{2}$"),


    # Literales

    ("FECHA", r"^\d{4}-\d{2}-\d{2}$"),

    ("NUM_INT", r"^\d+$")

]

def reconocer_token(lexema):

    for nombre, patron in TOKENS:

        if re.match(patron, lexema):

            return nombre

    return "ERROR_LEXICO"

#kms
def analizar_lexico(linea):

    resultado = []

    errores = []

    elementos = linea.split()

    for elemento in elementos:

        token = reconocer_token(
            elemento
        )

        resultado.append({

            "lexema": elemento,

            "token": token

        })

        if token == "ERROR_LEXICO":

            errores.append(
                elemento
            )

    return {

        "tokens": resultado,

        "errores": errores

    }


#testing lol

if __name__ == "__main__":

    print("\nPRUEBA CORRECTA\n")

    prueba1 = (
        "RECIBIR_LOTE "
        "PROD-FRU-001 "
        "LOT-TAC-202505 "
        "PROV-AGRO-001 "
        "50"
    )

    print(
        analizar_lexico(prueba1)
    )

    print("\nPRUEBA CON ERROR\n")

    prueba2 = (
        "RECIBIR_LOTE "
        "PROD-FRU-001 "
        "LOTE_MALO "
        "PROV-AGRO-001 "
        "50"
    )

    print(
        analizar_lexico(prueba2)
    )

