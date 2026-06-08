import pandas as pd
from werkzeug.utils import secure_filename
import os

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pandas as pd

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# =========================
# Estructuras Globales
# =========================

tabla_simbolos = {}
inventario = {}
historial = []

# =========================
# Generar código producto
# =========================

def generar_codigo(nombre):

    letra = nombre[0].upper()

    contador = 1

    while f"{letra}{contador}" in tabla_simbolos.values():
        contador += 1

    return f"{letra}{contador}"

# =========================
# Registrar historial
# =========================

def registrar_historial(
    accion,
    producto,
    cantidad
):

    historial.append({

        "fecha":
        datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        ),

        "accion":
        accion,

        "producto":
        producto,

        "cantidad":
        cantidad

    })

# =========================
# Procesar comando DSL
# =========================

def procesar_linea(linea):

    tokens = ""
    gramatica = ""
    sql = ""
    resultado = ""

    partes = linea.lower().split()

    comando = partes[0]

    # -------------------
    # CREAR
    # -------------------

    if comando == "crear":

        producto = partes[1]
        stock = int(partes[2])

        if producto not in tabla_simbolos:

            codigo_producto = generar_codigo(
                producto
            )

            tabla_simbolos[
                producto
            ] = codigo_producto

            inventario[
                codigo_producto
            ] = stock

        tokens = (
            f"CREAR "
            f"ID({producto}) "
            f"NUMERO({stock})"
        )

        gramatica = (
            "COMANDO → "
            "CREAR ID NUMERO"
        )

        sql = (
            "INSERT INTO PRODUCTOS "
            "(CODIGO,NOMBRE,STOCK) VALUES "
            f"('{tabla_simbolos[producto]}',"
            f"'{producto}',"
            f"{stock});"
        )

        resultado = (
            f"Producto {producto} creado"
        )

        registrar_historial(
            "CREAR",
            producto,
            stock
        )

    # -------------------
    # AGREGAR
    # -------------------

    elif comando == "agregar":

        producto = partes[1]
        cantidad = int(partes[2])

        codigo = tabla_simbolos[producto]

        inventario[codigo] += cantidad

        tokens = (
            f"AGREGAR "
            f"ID({producto}) "
            f"NUMERO({cantidad})"
        )

        gramatica = (
            "COMANDO → "
            "AGREGAR ID NUMERO"
        )

        sql = (
            "UPDATE PRODUCTOS "
            f"SET STOCK=STOCK+{cantidad} "
            f"WHERE CODIGO='{codigo}';"
        )

        resultado = (
            f"Stock agregado a "
            f"{producto}"
        )

        registrar_historial(
            "AGREGAR",
            producto,
            cantidad
        )

    # -------------------
    # VENDER
    # -------------------

    elif comando == "vender":

        producto = partes[1]
        cantidad = int(partes[2])

        codigo = tabla_simbolos[producto]

        inventario[codigo] -= cantidad

        tokens = (
            f"VENDER "
            f"ID({producto}) "
            f"NUMERO({cantidad})"
        )

        gramatica = (
            "COMANDO → "
            "VENDER ID NUMERO"
        )

        sql = (
            "UPDATE PRODUCTOS "
            f"SET STOCK=STOCK-{cantidad} "
            f"WHERE CODIGO='{codigo}';"
        )

        resultado = (
            f"Venta registrada "
            f"de {producto}"
        )

        registrar_historial(
            "VENDER",
            producto,
            cantidad
        )

    # -------------------
    # CONSULTAR
    # -------------------

    elif comando == "consultar":

        producto = partes[1]

        codigo = tabla_simbolos[producto]

        stock = inventario[codigo]

        tokens = (
            f"CONSULTAR "
            f"ID({producto})"
        )

        gramatica = (
            "COMANDO → "
            "CONSULTAR ID"
        )

        sql = (
            "SELECT * "
            "FROM PRODUCTOS "
            f"WHERE CODIGO='{codigo}';"
        )

        resultado = (
            f"Stock actual: {stock}"
        )

        registrar_historial(
            "CONSULTAR",
            producto,
            0
        )

    else:

        raise Exception(
            f"Comando desconocido: "
            f"{comando}"
        )

    return {
        "entrada": linea,
        "tokens": tokens,
        "gramatica": gramatica,
        "sql": sql,
        "resultado": resultado
    }

# =========================
# Página principal
# =========================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )

# =========================
# Compilar
# =========================

@app.route(
    "/compilar",
    methods=["POST"]
)
def compilar():

    try:

        datos = request.get_json()

        resultado = procesar_linea(
            datos["codigo"]
        )

        return jsonify({

            "ok": True,

            **resultado,

            "simbolos":
            tabla_simbolos,

            "inventario":
            inventario,

            "historial":
            historial

        })

    except Exception as e:

        return jsonify({

            "ok": False,

            "error": str(e)

        })

# =========================
# Estadísticas
# =========================

@app.route("/estadisticas")
def estadisticas():

    total_productos = len(
        tabla_simbolos
    )

    total_stock = sum(
        inventario.values()
    )

    total_operaciones = len(
        historial
    )

    return jsonify({

        "productos":
        total_productos,

        "stock":
        total_stock,

        "operaciones":
        total_operaciones

    })

# =========================
# Historial
# =========================

@app.route("/historial")
def ver_historial():

    return jsonify(historial)



#--------------------------
#Importar TXT
#--------------------------
@app.route(
    "/importar_txt",
    methods=["POST"]
)
def importar_txt():

    try:

        archivo = request.files["archivo"]

        contenido = archivo.read().decode(
            "utf-8"
        )

        resultados = []

        for linea in contenido.splitlines():

            linea = linea.strip()

            if linea == "":
                continue

            resultado = procesar_linea(
                linea
            )

            resultados.append(resultado)

        return jsonify({

            "ok": True,

            "registros":
            resultados

        })

    except Exception as e:

        return jsonify({

            "ok": False,

            "error": str(e)

        })
# =========================
# Importar Excel
# =========================

@app.route(
    "/importar_excel",
    methods=["POST"]
)
def importar_excel():

    try:

        archivo = request.files["archivo"]

        ruta = os.path.join(

            app.config[
                "UPLOAD_FOLDER"
            ],

            secure_filename(
                archivo.filename
            )

        )

        archivo.save(ruta)

        df = pd.read_excel(ruta)

        resultados = []

        for _, fila in df.iterrows():

            accion = str(
                fila["accion"]
            ).lower()

            producto = str(
                fila["producto"]
            ).lower()

            cantidad = int(
                fila["cantidad"]
            )

            comando = (
                f"{accion} "
                f"{producto} "
                f"{cantidad}"
            )

            resultado = procesar_linea(
                comando
            )

            resultados.append(
                resultado
            )

        return jsonify({

            "ok": True,

            "registros":
            resultados

        })

    except Exception as e:

        return jsonify({

            "ok": False,

            "error": str(e)

        })


# =========================
# Ejecutar
# =========================

if __name__ == "__main__":

    app.run(debug=True)
