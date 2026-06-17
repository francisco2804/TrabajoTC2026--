#aqui entran los archivos en excel

CATALOGO_PRODUCTOS = {

    "PROD-FRU-001": {
        "nombre": "Manzana",
        "categoria": "Fruta"
    },

    "PROD-LAC-001": {
        "nombre": "Leche",
        "categoria": "Lácteo"
    },

    "PROD-BEB-001": {
        "nombre": "Agua",
        "categoria": "Bebida"
    }

}

def transformar(operacion):

    producto = CATALOGO_PRODUCTOS[
        operacion["producto"]
    ]

    # INGRESAR

    if operacion["operacion"] == "INGRESAR":

        return {

            "tipo_operacion":
            "Ingreso de producto",

            "producto":
            producto["nombre"],

            "categoria":
            producto["categoria"],

            "cantidad":
            operacion["cantidad"]

        }

    # RETIRAR

    if operacion["operacion"] == "RETIRAR":

        return {

            "tipo_operacion":
            "Salida de producto",

            "producto":
            producto["nombre"],

            "categoria":
            producto["categoria"],

            "cantidad":
            operacion["cantidad"]

        }

    # CONSULTAR

    if operacion["operacion"] == "CONSULTAR":

        return {

            "tipo_operacion":
            "Consulta de stock",

            "producto":
            producto["nombre"],

            "categoria":
            producto["categoria"]

        }

    # AJUSTAR

    if operacion["operacion"] == "AJUSTAR":

        return {

            "tipo_operacion":
            "Ajuste de inventario",

            "producto":
            producto["nombre"],

            "categoria":
            producto["categoria"],

            "cantidad":
            operacion["cantidad"]

        }

    # TRANSFERIR

    if operacion["operacion"] == "TRANSFERIR":

        return {

            "tipo_operacion":
            "Transferencia",

            "producto":
            producto["nombre"],

            "categoria":
            producto["categoria"],

            "origen":
            operacion["origen"],

            "destino":
            operacion["destino"],

            "cantidad":
            operacion["cantidad"]

        }

    # RECIBIR_LOTE

    if operacion["operacion"] == "RECIBIR_LOTE":

        proveedor = CATALOGO_PROVEEDORES[
            operacion["proveedor"]
        ]

        return {

            "tipo_operacion":
            "Recepción de lote",

            "producto":
            producto["nombre"],

            "categoria":
            producto["categoria"],

            "proveedor":
            proveedor["nombre"],

            "lote":
            operacion["lote"],

            "cantidad":
            operacion["cantidad"]

        }
    

    #im so done