from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from datetime import datetime

from lexer import analizar_lexico
from parser import validar_sintaxis
from interpreter import interpretar
from transformador import transformar
from afd import AFD_PRODUCTO
from arbol import construir_arbol

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

inventario = {}
historial_ops = []
operaciones_count = 0

GRAMATICAS = {
    "INGRESAR": "INGRESAR → INGRESAR PRODUCTO NUM_INT",
    "RETIRAR": "RETIRAR → RETIRAR PRODUCTO NUM_INT",
    "CONSULTAR": "CONSULTAR → CONSULTAR PRODUCTO",
    "AJUSTAR": "AJUSTAR → AJUSTAR PRODUCTO NUM_INT",
    "TRANSFERIR": "TRANSFERIR → TRANSFERIR PRODUCTO DESDE UBICACION HACIA UBICACION NUM_INT",
    "RECIBIR_LOTE": "RECIBIR_LOTE → RECIBIR_LOTE PRODUCTO LOTE PROVEEDOR NUM_INT"
}


def aplicar_operacion(interpretacion):
    global operaciones_count

    op = interpretacion.get("operacion")
    prod = interpretacion.get("producto")
    cant = interpretacion.get("cantidad", 0)

    if not prod:
        return

    if prod not in inventario:
        inventario[prod] = 0

    if op == "INGRESAR":
        inventario[prod] += cant

    elif op == "RETIRAR":
        inventario[prod] = max(0, inventario[prod] - cant)

    elif op == "AJUSTAR":
        inventario[prod] = cant

    elif op == "RECIBIR_LOTE":
        inventario[prod] += cant

    operaciones_count += 1

    historial_ops.append({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "accion": op,
        "producto": prod,
        "cantidad": cant
    })


def procesar_linea(linea):
    lexico = analizar_lexico(linea)
    sintaxis = validar_sintaxis(linea)

    if lexico.get("errores"):
        return {
            "entrada": linea,
            "tokens_detalle": lexico["tokens"],
            "gramatica": "—",
            "json": "Error léxico",
            "valido": False,
            "error": ", ".join(lexico["errores"])
        }

    if not sintaxis.get("valido"):
        op = linea.split()[0] if linea else ""

        return {
            "entrada": linea,
            "tokens_detalle": lexico["tokens"],
            "gramatica": GRAMATICAS.get(op, "—"),
            "json": "Error sintáctico",
            "valido": False,
            "error": sintaxis.get("error", "Error sintáctico")
        }

    interpretacion = interpretar(linea)
    aplicar_operacion(interpretacion)

    return {
        "entrada": linea,
        "tokens_detalle": lexico["tokens"],
        "gramatica": GRAMATICAS.get(
            interpretacion.get("operacion"), "—"
        ),
        "json": transformar(interpretacion),
        "valido": True
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compilar", methods=["POST"])
def compilar():
    try:
        data = request.get_json()
        codigo = data.get("codigo", "").strip()

        if not codigo:
            return jsonify({
                "ok": False,
                "error": "Código vacío"
            })

        lineas = [
            l.strip()
            for l in codigo.splitlines()
            if l.strip()
        ]

        registros = [procesar_linea(l) for l in lineas]

        return jsonify({
            "ok": True,
            "registros": registros,
            "resultado": "Procesado correctamente",
            "simbolos": inventario
        })

    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        })


@app.route("/procesar_excel", methods=["POST"])
def procesar_excel():
    try:
        archivo = request.files["archivo"]

        ruta = os.path.join(
            app.config["UPLOAD_FOLDER"],
            archivo.filename
        )

        archivo.save(ruta)

        df = pd.read_excel(ruta)
        registros = []

        for _, fila in df.iterrows():
            operacion = str(fila["operacion"]).upper()

            if operacion == "INGRESAR":
                linea = f"INGRESAR {fila['producto']} {int(fila['cantidad'])}"

            elif operacion == "RETIRAR":
                linea = f"RETIRAR {fila['producto']} {int(fila['cantidad'])}"

            elif operacion == "CONSULTAR":
                linea = f"CONSULTAR {fila['producto']}"

            elif operacion == "AJUSTAR":
                linea = f"AJUSTAR {fila['producto']} {int(fila['cantidad'])}"

            elif operacion == "TRANSFERIR":
                linea = (
                    f"TRANSFERIR {fila['producto']} "
                    f"DESDE {fila['origen']} "
                    f"HACIA {fila['destino']} "
                    f"{int(fila['cantidad'])}"
                )

            elif operacion == "RECIBIR_LOTE":
                linea = (
                    f"RECIBIR_LOTE {fila['producto']} "
                    f"{fila['lote']} "
                    f"{fila['proveedor']} "
                    f"{int(fila['cantidad'])}"
                )

            else:
                continue

            registros.append(procesar_linea(linea))

        return jsonify({
            "ok": True,
            "registros": registros,
            "simbolos": inventario
        })

    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        })


@app.route("/historial")
def historial():
    return jsonify(historial_ops[-50:])


@app.route("/estadisticas")
def estadisticas():
    return jsonify({
        "productos": len(inventario),
        "stock": sum(inventario.values()),
        "operaciones": operaciones_count
    })


@app.route("/afd")
def mostrar_afd():
    return render_template(
        "afd.html",
        tabla=AFD_PRODUCTO
    )


@app.route("/arbol")
def mostrar_arbol():
    linea = (
        "RECIBIR_LOTE "
        "PROD-FRU-001 "
        "LOT-TAC-202505 "
        "PROV-AGRO-001 "
        "50"
    )

    arbol = construir_arbol(linea)

    return render_template(
        "arbol.html",
        arbol=arbol
    )


if __name__ == "__main__":
    app.run(debug=True)        ruta = os.path.join(
            app.config["UPLOAD_FOLDER"],
            archivo.filename
        )

        archivo.save(ruta)

        df = pd.read_excel(ruta)

        resultados = []

        for _, fila in df.iterrows():

            operacion = str(
                fila["operacion"]
            ).upper()

            if operacion == "INGRESAR":

                linea = (
                    f"INGRESAR "
                    f"{fila['producto']} "
                    f"{int(fila['cantidad'])}"
                )

            elif operacion == "RETIRAR":

                linea = (
                    f"RETIRAR "
                    f"{fila['producto']} "
                    f"{int(fila['cantidad'])}"
                )

            elif operacion == "CONSULTAR":

                linea = (
                    f"CONSULTAR "
                    f"{fila['producto']}"
                )

            elif operacion == "AJUSTAR":

                linea = (
                    f"AJUSTAR "
                    f"{fila['producto']} "
                    f"{int(fila['cantidad'])}"
                )

            elif operacion == "TRANSFERIR":

                linea = (
                    f"TRANSFERIR "
                    f"{fila['producto']} "
                    f"DESDE "
                    f"{fila['origen']} "
                    f"HACIA "
                    f"{fila['destino']} "
                    f"{int(fila['cantidad'])}"
                )

            elif operacion == "RECIBIR_LOTE":

                linea = (
                    f"RECIBIR_LOTE "
                    f"{fila['producto']} "
                    f"{fila['lote']} "
                    f"{fila['proveedor']} "
                    f"{int(fila['cantidad'])}"
                )

            tokens = analizar_lexico(
                linea
            )

            sintaxis = validar_sintaxis(
                linea
            )

            interpretacion = interpretar(
                linea
            )

            json_operacion = transformar(
    interpretacion
)

            resultados.append({

                "linea_dsl": linea,

                "tokens": tokens,

                "sintaxis": sintaxis,

                "interpretacion": interpretacion,

                "json": json_operacion

            })

        return jsonify({

            "ok": True,

            "resultados": resultados

        })

    except Exception as e:

        return jsonify({

            "ok": False,

            "error": str(e)

        })

    


@app.route("/afd")
def mostrar_afd():

    return render_template(
        "afd.html",
        tabla=AFD_PRODUCTO
    )
 
@app.route("/arbol")
def mostrar_arbol():

    linea = (

        "RECIBIR_LOTE "
        "PROD-FRU-001 "
        "LOT-TAC-202505 "
        "PROV-AGRO-001 "
        "50"

    )

    arbol = construir_arbol(linea)

    return render_template(
        "arbol.html",
        arbol=arbol
    )

if __name__ == "__main__":

    app.run(
        debug=True
    )
