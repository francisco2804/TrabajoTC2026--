from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from lexer import analizar_lexico
from parser import validar_sintaxis
from interpreter import interpretar
from transformador import transformar

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

        return jsonify({

            "ok": True,
            "mensaje":
            "Excel leído correctamente"

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