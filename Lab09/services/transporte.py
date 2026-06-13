"""
Servicio de Transporte - LogiFresh S.A.
Puerto: 5004
Simula: retrasos en asignacion de transporte.
"""
from flask import Flask, request, jsonify
import random
import uuid
import time
from datetime import datetime

app = Flask(__name__)

transportes = {}
retraso_counter = 0

ESTADOS = ["PENDIENTE", "ASIGNADO", "EN_RUTA", "ENTREGADO", "CANCELADO"]

@app.route('/transporte', methods=['POST'])
def programar_transporte():
    global retraso_counter
    retraso_counter += 1

    data = request.get_json()
    transporte_id = f"TRN-{uuid.uuid4().hex[:8].upper()}"

    # Simular retraso en asignacion cada 5 solicitudes
    estado_inicial = "PENDIENTE"
    delay_msg = ""
    if retraso_counter % 5 == 0:
        estado_inicial = "PENDIENTE"
        delay_msg = "Asignacion de transporte con retraso (simulado)"

    transporte = {
        "transporte_id": transporte_id,
        "pedido_id": data.get("pedido_id"),
        "cliente": data.get("cliente"),
        "destino": data.get("destino"),
        "estado": estado_inicial,
        "fecha_creacion": datetime.now().isoformat(),
        "observaciones": delay_msg,
        "conductor": None,
        "vehiculo": None
    }
    transportes[transporte_id] = transporte

    # Asignar conductor y vehiculo automaticamente (simulacion)
    if retraso_counter % 5 != 0:
        transporte["estado"] = "ASIGNADO"
        transporte["conductor"] = random.choice(["Carlos M.", "Luis R.", "Ana T.", "Miguel P."])
        transporte["vehiculo"] = random.choice(["CAM-101", "CAM-202", "CAM-303", "CAM-404"])

    return jsonify(transporte), 201

@app.route('/transporte/<transporte_id>', methods=['GET'])
def obtener_transporte(transporte_id):
    if transporte_id not in transportes:
        return jsonify({"error": "Transporte no encontrado"}), 404
    return jsonify(transportes[transporte_id])

@app.route('/transporte/<transporte_id>', methods=['PUT'])
def actualizar_transporte(transporte_id):
    if transporte_id not in transportes:
        return jsonify({"error": "Transporte no encontrado"}), 404

    data = request.get_json()
    nuevo_estado = data.get("estado")
    if nuevo_estado and nuevo_estado in ESTADOS:
        transportes[transporte_id]["estado"] = nuevo_estado
    if "conductor" in data:
        transportes[transporte_id]["conductor"] = data["conductor"]
    if "vehiculo" in data:
        transportes[transporte_id]["vehiculo"] = data["vehiculo"]

    return jsonify(transportes[transporte_id])

@app.route('/transportes', methods=['GET'])
def listar_transportes():
    return jsonify(list(transportes.values()))

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "servicio": "transporte"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5004, debug=False, threaded=True)
