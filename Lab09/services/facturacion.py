"""
Servicio de Facturacion - LogiFresh S.A.
Puerto: 5003
Simula: facturas duplicadas ocasionalmente.
"""
from flask import Flask, request, jsonify
import random
import uuid
from datetime import datetime

app = Flask(__name__)

facturas = {}
duplicado_counter = 0

@app.route('/factura', methods=['POST'])
def generar_factura():
    global duplicado_counter
    duplicado_counter += 1

    data = request.get_json()
    factura_id = f"FAC-{uuid.uuid4().hex[:8].upper()}"
    pedido_id = data.get("pedido_id")

    factura = {
        "factura_id": factura_id,
        "pedido_id": pedido_id,
        "cliente": data.get("cliente"),
        "productos": data.get("productos"),
        "subtotal": data.get("subtotal"),
        "descuento": data.get("descuento"),
        "total": data.get("total"),
        "fecha": datetime.now().isoformat(),
        "estado": "EMITIDA"
    }
    facturas[factura_id] = factura

    # Simular factura duplicada (cada 5 facturas se genera un duplicado)
    if duplicado_counter % 5 == 0:
        factura_dup_id = f"FAC-{uuid.uuid4().hex[:8].upper()}"
        factura_dup = dict(factura)
        factura_dup["factura_id"] = factura_dup_id
        factura_dup["_duplicada"] = True
        factura_dup["_factura_original"] = factura_id
        facturas[factura_dup_id] = factura_dup

    return jsonify(factura), 201

@app.route('/factura/<factura_id>', methods=['GET'])
def obtener_factura(factura_id):
    if factura_id not in facturas:
        return jsonify({"error": "Factura no encontrada"}), 404
    return jsonify(facturas[factura_id])

@app.route('/facturas', methods=['GET'])
def listar_facturas():
    return jsonify(list(facturas.values()))

@app.route('/facturas/duplicadas', methods=['GET'])
def listar_duplicadas():
    dups = {k: v for k, v in facturas.items() if v.get("_duplicada")}
    return jsonify(list(dups.values()))

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "servicio": "facturacion"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5003, debug=False, threaded=True)
