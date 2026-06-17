from parser import validar_sintaxis

#operaciones internas
def interpretar(linea):

    resultado = validar_sintaxis(linea)

    if not resultado["valido"]:

        return resultado

    partes = linea.split()

    if partes[0] == "INGRESAR":

        return {

            "operacion": "INGRESAR",

            "producto": partes[1],

            "cantidad": int(partes[2])

    }

    #una hora peleando con esto y era la sangría

    if partes[0] == "RETIRAR":

        return {

            "operacion": "RETIRAR",

            "producto": partes[1],

            "cantidad": int(partes[2])

    }

    if partes[0] == "CONSULTAR":

        return {

            "operacion": "CONSULTAR",

            "producto": partes[1]

    }

    if partes[0] == "AJUSTAR":

        return {

            "operacion": "AJUSTAR",

            "producto": partes[1],

            "cantidad": int(partes[2])

    }

    if partes[0] == "TRANSFERIR":

        return {

            "operacion": "TRANSFERIR",

            "producto": partes[1],

            "origen": partes[3],

            "destino": partes[5],

            "cantidad": int(partes[6])

    }

    if partes[0] == "RECIBIR_LOTE":

        return {

            "operacion": "RECIBIR_LOTE",

            "producto": partes[1],

            "lote": partes[2],

            "proveedor": partes[3],

            "cantidad": int(partes[4])

    }

    return {

        "error": "Operación no reconocida"

    }

#testing testing ヽ(｀Д´)ﾉ (prueba)

if __name__ == "__main__":

    linea = (
        "RECIBIR_LOTE "
        "PROD-FRU-001 "
        "LOT-TAC-202505 "
        "PROV-AGRO-001 "
        "50"
    )

    print(
    interpretar(
        "TRANSFERIR PROD-FRU-001 DESDE ALM-A01 HACIA ALM-B01 20"
    )
)