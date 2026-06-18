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

# Estado en memoria
inventario = {}   # producto_id -> stock
historial_ops = []
operaciones_count = 0


# ── helpers ──────────────────────────────────────────────

GRAMATICAS = {
    "INGRESAR":     "INGRESAR → INGRESAR PRODUCTO NUM_INT",
    "RETIRAR":      "RETIRAR → RETIRAR PRODUCTO NUM_INT",
    "CONSULTAR":    "CONSULTAR → CONSULTAR PRODUCTO",
    "AJUSTAR":      "AJUSTAR → AJUSTAR PRODUCTO NUM_INT",
    "TRANSFERIR":   "TRANSFERIR → TRANSFERIR PRODUCTO DESDE UBICACION HACIA UBICACION NUM_INT",
    "RECIBIR_LOTE": "RECIBIR_LOTE → RECIBIR_LOTE PRODUCTO LOTE PROVEEDOR NUM_INT",
}

CATALOGO_PRODUCTOS = {
    "PROD-FRU-001": {"nombre": "Manzana",  "categoria": "Fruta"},
    "PROD-LAC-001": {"nombre": "Leche",    "categoria": "Lácteo"},
    "PROD-BEB-001": {"nombre": "Agua",     "categoria": "Bebida"},
}

CATALOGO_PROVEEDORES = {
    "PROV-AGRO-001": {"nombre": "AgroPerú SAC"},
}


def generar_sql(interpretado):
    op = interpretado.get("operacion")
    prod = interpretado.get("producto", "")
    cant = interpretado.get("cantidad", 0)

    if op == "INGRESAR":
        return (
            f"INSERT INTO movimientos (tipo, producto_id, cantidad, fecha)\n"
            f"VALUES ('INGRESO', '{prod}', {cant}, GETDATE());"
        )
    if op == "RETIRAR":
        return (
            f"INSERT INTO movimientos (tipo, producto_id, cantidad, fecha)\n"
            f"VALUES ('SALIDA', '{prod}', {cant}, GETDATE());"
        )
    if op == "CONSULTAR":
        return (
            f"SELECT * FROM inventario\n"
            f"WHERE producto_id = '{prod}';"
        )
    if op == "AJUSTAR":
        return (
            f"UPDATE inventario\n"
            f"SET stock = {cant}\n"
            f"WHERE producto_id = '{prod}';"
        )
    if op == "TRANSFERIR":
        origen  = interpretado.get("origen", "")
        destino = interpretado.get("destino", "")
        return (
            f"UPDATE inventario SET ubicacion = '{destino}'\n"
            f"WHERE producto_id = '{prod}' AND ubicacion = '{origen}' AND stock >= {cant};"
        )
    if op == "RECIBIR_LOTE":
        lote  = interpretado.get("lote", "")
        prov  = interpretado.get("proveedor", "")
        return (
            f"INSERT INTO lotes (lote_id, producto_id, proveedor_id, cantidad, fecha)\n"
            f"VALUES ('{lote}', '{prod}', '{prov}', {cant}, GETDATE());"
        )
    return "-- Sin traducción"


def aplicar_operacion(interpretado):
    global operaciones_count
    op   = interpretado.get("operacion")
    prod = interpretado.get("producto", "")
    cant = interpretado.get("cantidad", 0)

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
        "fecha":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "accion":   op,
        "producto": prod,
        "cantidad": cant if op != "CONSULTAR" else inventario.get(prod, 0),
    })


def procesar_linea(linea):
    """Procesa una línea y devuelve el dict de registro para el frontend."""
    lexico     = analizar_lexico(linea)
    tokens_str = " | ".join(
        f"{t['lexema']}:{t['token']}" for t in lexico["tokens"]
    )
    errores_lex = lexico["errores"]

    sintaxis = validar_sintaxis(linea)

    if errores_lex:
        return {
            "entrada":        linea,
            "tokens":         f"ERROR LÉXICO: {', '.join(errores_lex)}",
            "tokens_detalle": lexico["tokens"],
            "gramatica":      "—",
            "sql":            "— (error léxico)",
            "valido":         False,
            "error":          f"Errores léxicos: {', '.join(errores_lex)}",
        }

    if not sintaxis["valido"]:
        op = linea.split()[0] if linea.split() else ""
        return {
            "entrada":        linea,
            "tokens":         tokens_str,
            "tokens_detalle": lexico["tokens"],
            "gramatica":      GRAMATICAS.get(op, "—"),
            "sql":            "— (error sintáctico)",
            "valido":         False,
            "error":          sintaxis.get("error") or sintaxis.get("motivo", "Error sintáctico"),
        }

    interpretado = interpretar(linea)
    op           = interpretado.get("operacion", "")
    sql          = generar_sql(interpretado)
    aplicar_operacion(interpretado)

    return {
        "entrada":        linea,
        "tokens":         tokens_str,
        "tokens_detalle": lexico["tokens"],
        "gramatica":      GRAMATICAS.get(op, "—"),
        "sql":            sql,
        "valido":         True,
    }


# ── rutas ─────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compilar", methods=["POST"])
def compilar():
    try:
        data   = request.get_json()
        codigo = data.get("codigo", "").strip()

        if not codigo:
            return jsonify({"ok": False, "error": "Código vacío"})

        lineas    = [l.strip() for l in codigo.splitlines() if l.strip()]
        registros = [procesar_linea(l) for l in lineas]

        simbolos = {k: v for k, v in inventario.items()}

        return jsonify({
            "ok":        True,
            "registros": registros,
            "resultado": "\n".join(
                r["sql"] if r["valido"] else f"Error: {r.get('error','')}"
                for r in registros
            ),
            "simbolos":  simbolos,
        })

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/importar_txt", methods=["POST"])
def importar_txt():
    try:
        archivo = request.files["archivo"]
        contenido = archivo.read().decode("utf-8")
        lineas    = [l.strip() for l in contenido.splitlines() if l.strip()]
        registros = [procesar_linea(l) for l in lineas]

        return jsonify({
            "ok":        True,
            "registros": registros,
            "simbolos":  dict(inventario),
        })

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/importar_excel", methods=["POST"])
def importar_excel():
    try:
        archivo = request.files["archivo"]
        ruta    = os.path.join(app.config["UPLOAD_FOLDER"], archivo.filename)
        archivo.save(ruta)

        df = pd.read_excel(ruta, header=None)

        # Toma la primera columna como instrucciones
        lineas    = [str(v).strip() for v in df.iloc[:, 0] if str(v).strip() and str(v) != "nan"]
        registros = [procesar_linea(l) for l in lineas]

        return jsonify({
            "ok":        True,
            "registros": registros,
            "simbolos":  dict(inventario),
        })

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/historial")
def historial():
    return jsonify(historial_ops[-50:])


@app.route("/estadisticas")
def estadisticas():
    return jsonify({
        "productos":   len(inventario),
        "stock":       sum(inventario.values()),
        "operaciones": operaciones_count,
    })


@app.route("/afd")
def mostrar_afd():
    return render_template("afd.html", tabla=AFD_PRODUCTO)

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
    app.run(debug=True)
