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

    if partes[0] == "RETIRAR":

        return {

            "operacion": "RETIRAR",

            "producto": partes[1],

            "cantidad": int(partes[2])

    }

    elif partes[0] == "CONSULTAR":

        return {

            "operacion": "CONSULTAR",

            "producto": partes[1]

    }

    elif partes[0] == "AJUSTAR":

        return {

            "operacion": "AJUSTAR",

            "producto": partes[1],

            "cantidad": int(partes[2])

    }

    elif partes[0] == "TRANSFERIR":

        return {

            "operacion": "TRANSFERIR",

            "producto": partes[1],

            "origen": partes[3],

            "destino": partes[5],

            "cantidad": int(partes[6])

    }

    elif partes[0] == "RECIBIR_LOTE":

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
