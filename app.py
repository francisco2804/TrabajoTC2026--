from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from lexer import analizar_lexico
from parser import validar_sintaxis
from interpreter import interpretar
from transformador import transformar
from afd import AFD_PRODUCTO
from arbol import construir_arbol
from json_gen import generar_json

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")

def index():

    return render_template(
        "index.html"
    )

@app.route(
    "/procesar_excel",
    methods=["POST"]
)
def procesar_excel():

    try:

        archivo = request.files["archivo"]

        ruta = os.path.join(
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

            json_operacion = generar_json(
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

    
if __name__ == "__main__":

    app.run(
        debug=True
    )

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
