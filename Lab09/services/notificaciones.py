"""
Servicio de Notificaciones - LogiFresh S.A.
Puerto: 5005
Simula: retrasos en confirmaciones por correo electronico.
"""
from flask import Flask, request, jsonify
import random
import uuid
import time
import threading
from datetime import datetime

app = Flask(__name__)

notificaciones = []
retraso_counter = 0

@app.route('/notificacion', methods=['POST'])
def enviar_notificacion():
    global retraso_counter
    retraso_counter += 1

    data = request.get_json()
    notif_id = f"NTF-{uuid.uuid4().hex[:8].upper()}"

    # Simular retraso en notificaciones (cada 4 notificaciones tiene retraso)
    enviado = True
    delay = 0
    if retraso_counter % 4 == 0:
        delay = random.uniform(3, 8)  # 3-8 segundos de retraso
        # En un sistema real, esto seria un delay en el envio del correo
        time.sleep(delay)
        enviado = True

    notificacion = {
        "notificacion_id": notif_id,
        "pedido_id": data.get("pedido_id"),
        "cliente": data.get("cliente"),
        "email": data.get("email"),
        "mensaje": data.get("mensaje"),
        "enviado": enviado,
        "fecha": datetime.now().isoformat(),
        "retraso_segundos": round(delay, 2) if delay > 0 else 0,
        "tipo": "EMAIL"
    }
    notificaciones.append(notificacion)

    return jsonify(notificacion), 201

@app.route('/notificaciones', methods=['GET'])
def listar_notificaciones():
    return jsonify(notificaciones)

@app.route('/notificacion/<notificacion_id>', methods=['GET'])
def obtener_notificacion(notificacion_id):
    for n in notificaciones:
        if n["notificacion_id"] == notificacion_id:
            return jsonify(n)
    return jsonify({"error": "Notificacion no encontrada"}), 404

@app.route('/notificaciones/retrasadas', methods=['GET'])
def listar_retrasadas():
    retrasadas = [n for n in notificaciones if n.get("retraso_segundos", 0) > 0]
    return jsonify(retrasadas)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "servicio": "notificaciones"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005, debug=False, threaded=True)
