from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# -------------------------
# Tabla de símbolos
# -------------------------

tabla_simbolos = {}
inventario = {}

# -------------------------
# Generar código producto
# -------------------------

def generar_codigo(nombre):

    letra = nombre[0].upper()

    contador = 1

    while f"{letra}{contador}" in tabla_simbolos.values():
        contador += 1

    return f"{letra}{contador}"

# -------------------------
# Compilador DSL
# -------------------------

def compilar(codigo):

    tokens = []
    intermedio = []
    resultado = []

    lineas = codigo.splitlines()

    for linea in lineas:

        linea = linea.strip()

        if linea == "":
            continue

        partes = linea.lower().split()

        comando = partes[0]

        # CREAR

        if comando == "crear":

            producto = partes[1]
            stock = int(partes[2])

            if producto not in tabla_simbolos:

                codigo_producto = generar_codigo(producto)

                tabla_simbolos[producto] = codigo_producto

                inventario[codigo_producto] = stock

            tokens.append(
                f"CREAR ID({producto}) NUMERO({stock})"
            )

            intermedio.append(
                f"CREATE_PRODUCT {tabla_simbolos[producto]} {stock}"
            )

        # AGREGAR

        elif comando == "agregar":

            producto = partes[1]
            cantidad = int(partes[2])

            if producto not in tabla_simbolos:
                raise Exception(
                    f"Producto no registrado: {producto}"
                )

            codigo_producto = tabla_simbolos[producto]

            inventario[codigo_producto] += cantidad

            tokens.append(
                f"AGREGAR ID({producto}) NUMERO({cantidad})"
            )

            intermedio.append(
                f"ADD_STOCK {codigo_producto} {cantidad}"
            )

        # VENDER

        elif comando == "vender":

            producto = partes[1]
            cantidad = int(partes[2])

            if producto not in tabla_simbolos:
                raise Exception(
                    f"Producto no registrado: {producto}"
                )

            codigo_producto = tabla_simbolos[producto]

            if inventario[codigo_producto] < cantidad:
                raise Exception(
                    f"Stock insuficiente para {producto}"
                )

            inventario[codigo_producto] -= cantidad

            tokens.append(
                f"VENDER ID({producto}) NUMERO({cantidad})"
            )

            intermedio.append(
                f"REMOVE_STOCK {codigo_producto} {cantidad}"
            )

        # CONSULTAR

        elif comando == "consultar":

            producto = partes[1]

            if producto not in tabla_simbolos:
                raise Exception(
                    f"Producto no registrado: {producto}"
                )

            codigo_producto = tabla_simbolos[producto]

            stock = inventario[codigo_producto]

            tokens.append(
                f"CONSULTAR ID({producto})"
            )

            intermedio.append(
                f"CHECK_STOCK {codigo_producto}"
            )

            resultado.append(
                f"{producto.upper()} ({codigo_producto}) = {stock}"
            )

        else:

            raise Exception(
                f"Comando desconocido: {comando}"
            )

    return {
        "tokens": "\n".join(tokens),
        "intermedio": "\n".join(intermedio),
        "resultado": "\n".join(resultado),
        "simbolos": tabla_simbolos
    }

# -------------------------
# Página principal
# -------------------------

@app.route("/")
def index():

    return render_template("index.html")

# -------------------------
# API compilador
# -------------------------

@app.route("/compilar", methods=["POST"])
def compilar_api():

    try:

        datos = request.get_json()

        resultado = compilar(
            datos["codigo"]
        )

        return jsonify(resultado)

    except Exception as e:

        return jsonify({
            "tokens": "",
            "intermedio": "",
            "resultado": str(e),
            "simbolos": tabla_simbolos
        })

# -------------------------
# Ejecutar Flask
# -------------------------

if __name__ == "__main__":

    app.run(debug=True)