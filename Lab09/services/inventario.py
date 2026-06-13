"""
Servicio de Inventario - LogiFresh S.A.
Puerto: 5002
Simula inconsistencias ocasionales de inventario.
"""
from flask import Flask, request, jsonify
import random
import time

app = Flask(__name__)

# Inventario inicial
inventario = {
    "P001": {"nombre": "Leche fresca 1L",    "stock": 500, "precio": 4.50},
    "P002": {"nombre": "Queso fresco 500g",  "stock": 150, "precio": 12.00},
    "P003": {"nombre": "Yogurt natural 1L",  "stock": 300, "precio": 6.80},
    "P004": {"nombre": "Mantequilla 250g",   "stock": 200, "precio": 8.50},
    "P005": {"nombre": "Pollo refrigerado 1kg", "stock": 80, "precio": 15.00},
    "P006": {"nombre": "Carne de res 1kg",   "stock": 60, "precio": 22.00},
    "P007": {"nombre": "Pescado fresco 1kg", "stock": 45, "precio": 18.00},
    "P008": {"nombre": "Huevos 30un",        "stock": 400, "precio": 10.50},
    "P009": {"nombre": "Jugo de naranja 1L", "stock": 250, "precio": 7.20},
    "P010": {"nombre": "Helado 1L",          "stock": 100, "precio": 16.00},
}

# Contador para simular inconsistencia
fallo_counter = 0

@app.route('/inventario', methods=['GET'])
def listar_inventario():
    return jsonify(inventario)

@app.route('/inventario/<producto_id>', methods=['GET'])
def consultar_stock(producto_id):
    global fallo_counter
    fallo_counter += 1

    if producto_id not in inventario:
        return jsonify({"error": "Producto no encontrado"}), 404

    producto = inventario[producto_id]

    # Simular inconsistencia de inventario (cada 5 consultas)
    if fallo_counter % 5 == 0:
        producto_inconsistente = dict(producto)
        producto_inconsistente["stock"] = max(0, producto["stock"] - random.randint(1, 20))
        producto_inconsistente["_inconsistente"] = True
        return jsonify(producto_inconsistente)

    return jsonify(producto)

@app.route('/inventario/<producto_id>/reducir', methods=['POST'])
def reducir_stock(producto_id):
    global fallo_counter
    data = request.get_json()
    cantidad = data.get("cantidad", 1)

    if producto_id not in inventario:
        return jsonify({"error": "Producto no encontrado"}), 404

    producto = inventario[producto_id]
    if producto["stock"] < cantidad:
        return jsonify({"error": f"Stock insuficiente. Disponible: {producto['stock']}"}), 409

    # A veces la reduccion no se registra bien (simulacion de inconsistencia)
    fallo_counter += 1
    if fallo_counter % 7 == 0:
        # No reduce el stock correctamente
        reduccion_real = cantidad - random.randint(1, min(3, cantidad))
        producto["stock"] -= reduccion_real
        return jsonify({"mensaje": "Stock reducido parcialmente (inconsistencia simulada)",
                        "stock_actual": producto["stock"],
                        "_inconsistente": True})

    producto["stock"] -= cantidad
    return jsonify({"mensaje": "Stock reducido correctamente",
                    "stock_actual": producto["stock"]})

@app.route('/inventario/<producto_id>/aumentar', methods=['POST'])
def aumentar_stock(producto_id):
    data = request.get_json()
    cantidad = data.get("cantidad", 1)

    if producto_id not in inventario:
        return jsonify({"error": "Producto no encontrado"}), 404

    inventario[producto_id]["stock"] += cantidad
    return jsonify({"mensaje": "Stock aumentado correctamente",
                    "stock_actual": inventario[producto_id]["stock"]})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "servicio": "inventario"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=False, threaded=True)
