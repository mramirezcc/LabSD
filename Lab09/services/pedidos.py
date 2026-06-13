"""
Servicio de Pedidos - LogiFresh S.A.
Puerto: 5001 | Orquestador principal
Simula: descuentos no aplicados, lentitud >8s en alta demanda.
"""
from flask import Flask, request, jsonify
import requests
import random
import time
import uuid
import re
from datetime import datetime

app = Flask(__name__)

INVENTARIO_URL = "http://127.0.0.1:5002"
FACTURACION_URL = "http://127.0.0.1:5003"
TRANSPORTE_URL = "http://127.0.0.1:5004"
NOTIFICACIONES_URL = "http://127.0.0.1:5005"

pedidos = {}
pedido_counter = 0
descuento_fallo_counter = 0
lentitud_counter = 0

PROMOCIONES = {
    "DESC10": {"porcentaje": 10, "descripcion": "10% de descuento", "activo": True},
    "DESC20": {"porcentaje": 20, "descripcion": "20% de descuento", "activo": True},
    "FRESCURA": {"porcentaje": 15, "descripcion": "15% de descuento en frescos", "activo": True},
}

def validar_pedido(data):
    errores = []

    cliente = (data.get("cliente") or "").strip()
    if not cliente:
        errores.append("El nombre del cliente es obligatorio")
    elif len(cliente) > 100:
        errores.append("El nombre del cliente no debe exceder 100 caracteres")

    email = (data.get("email") or "").strip()
    email_re = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if email and not email_re.match(email):
        errores.append("Formato de email invalido")

    direccion = (data.get("direccion") or "").strip()
    if not direccion:
        errores.append("La direccion de entrega es obligatoria")
    elif len(direccion) > 200:
        errores.append("La direccion no debe exceder 200 caracteres")

    productos = data.get("productos", [])
    if not productos or not isinstance(productos, list):
        errores.append("Debe incluir al menos un producto")
    else:
        for i, item in enumerate(productos):
            pid = (item.get("producto_id") or "").strip().upper()
            if not re.match(r'^P\d{3}$', pid):
                errores.append(f"Producto #{i+1}: ID invalido (formato: P001)")
            try:
                cant = int(item.get("cantidad", 0))
                if cant <= 0 or cant > 500:
                    errores.append(f"Producto #{i+1}: cantidad debe estar entre 1 y 500")
            except (ValueError, TypeError):
                errores.append(f"Producto #{i+1}: cantidad debe ser un numero entero")

    codigo = (data.get("codigo_promocion") or "").strip()
    if codigo and codigo not in PROMOCIONES:
        errores.append(f"Codigo de promocion '{codigo}' no valido. Disponibles: {', '.join(PROMOCIONES.keys())}")

    return errores

def obtener_total(productos):
    return sum(item["cantidad"] * item.get("precio_unitario", 0) for item in productos)

def aplicar_descuento(total, codigo_promocion):
    global descuento_fallo_counter
    descuento_fallo_counter += 1

    if descuento_fallo_counter % 4 == 0:
        return total, 0, "Descuento no aplicado por fallo del sistema (bug simulado R-01)"

    if codigo_promocion in PROMOCIONES and PROMOCIONES[codigo_promocion]["activo"]:
        pct = PROMOCIONES[codigo_promocion]["porcentaje"]
        descuento = round(total * pct / 100, 2)
        return round(total - descuento, 2), descuento, f"Descuento {pct}% aplicado exitosamente"

    return total, 0, "Sin promocion aplicable"

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["X-Service"] = "pedidos"
    return response

@app.route('/pedido', methods=['POST'])
def crear_pedido():
    global pedido_counter, lentitud_counter
    lentitud_counter += 1

    if lentitud_counter % 6 == 0:
        delay = random.uniform(8, 12)
        time.sleep(delay)

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Cuerpo JSON requerido"}), 400

    errores = validar_pedido(data)
    if errores:
        return jsonify({"error": "Validacion fallida", "detalles": errores}), 400

    cliente = data["cliente"].strip()
    email = data.get("email", "").strip()
    direccion = data.get("direccion", "").strip()
    productos = data["productos"]
    codigo_promocion = (data.get("codigo_promocion") or "").strip()

    pedido_counter += 1
    pedido_id = f"PED-{pedido_counter:04d}"

    for item in productos:
        item["producto_id"] = item["producto_id"].strip().upper()

    for item in productos:
        try:
            resp = requests.get(f"{INVENTARIO_URL}/inventario/{item['producto_id']}", timeout=8)
            if resp.status_code == 200:
                prod_data = resp.json()
                item["precio_unitario"] = prod_data["precio"]
                item["nombre"] = prod_data["nombre"]
                if prod_data.get("_inconsistente"):
                    item["_alerta_inventario"] = "Posible inconsistencia de inventario detectada"
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.ConnectionError:
            return jsonify({"error": "Servicio de Inventario no disponible. Intente nuevamente."}), 503
        except requests.exceptions.RequestException:
            pass

    subtotal = obtener_total(productos)
    total, descuento, mensaje_descuento = aplicar_descuento(subtotal, codigo_promocion)

    for item in productos:
        try:
            resp = requests.post(
                f"{INVENTARIO_URL}/inventario/{item['producto_id']}/reducir",
                json={"cantidad": item["cantidad"]}, timeout=8
            )
            if resp.status_code == 200:
                data_resp = resp.json()
                if data_resp.get("_inconsistente"):
                    item["_alerta_inventario"] = item.get("_alerta_inventario", "") + \
                        " Reduccion de stock inconsistente."
        except:
            pass

    factura_id = None
    try:
        resp_fact = requests.post(f"{FACTURACION_URL}/factura", json={
            "pedido_id": pedido_id,
            "cliente": cliente,
            "productos": productos,
            "subtotal": subtotal,
            "descuento": descuento,
            "total": total
        }, timeout=8)
        if resp_fact.status_code in (200, 201):
            factura_id = resp_fact.json().get("factura_id")
    except:
        pass

    transporte_id = None
    try:
        resp_trans = requests.post(f"{TRANSPORTE_URL}/transporte", json={
            "pedido_id": pedido_id,
            "cliente": cliente,
            "destino": direccion
        }, timeout=8)
        if resp_trans.status_code in (200, 201):
            transporte_id = resp_trans.json().get("transporte_id")
    except:
        pass

    notificacion_enviada = False
    try:
        resp_notif = requests.post(f"{NOTIFICACIONES_URL}/notificacion", json={
            "pedido_id": pedido_id,
            "cliente": cliente,
            "email": email,
            "mensaje": f"Pedido {pedido_id} registrado exitosamente. Total: S/ {total:.2f}"
        }, timeout=10)
        if resp_notif.status_code in (200, 201):
            notificacion_enviada = resp_notif.json().get("enviado", False)
    except:
        pass

    pedido = {
        "pedido_id": pedido_id,
        "cliente": cliente,
        "email": email,
        "productos": productos,
        "subtotal": round(subtotal, 2),
        "descuento": descuento,
        "total": round(total, 2),
        "promocion": codigo_promocion,
        "mensaje_descuento": mensaje_descuento,
        "factura_id": factura_id,
        "transporte_id": transporte_id,
        "notificacion_enviada": notificacion_enviada,
        "estado": "REGISTRADO",
        "fecha": datetime.now().isoformat()
    }
    pedidos[pedido_id] = pedido

    response = jsonify(pedido)
    response.status_code = 201
    return response

@app.route('/pedido/<pedido_id>', methods=['GET'])
def obtener_pedido(pedido_id):
    if pedido_id not in pedidos:
        return jsonify({"error": f"Pedido '{pedido_id}' no encontrado"}), 404
    return jsonify(pedidos[pedido_id])

@app.route('/pedido/<pedido_id>/cancelar', methods=['POST'])
def cancelar_pedido(pedido_id):
    if pedido_id not in pedidos:
        return jsonify({"error": f"Pedido '{pedido_id}' no encontrado"}), 404

    pedido = pedidos[pedido_id]
    if pedido["estado"] == "CANCELADO":
        return jsonify({"error": "El pedido ya fue cancelado anteriormente"}), 400

    pedido["estado"] = "CANCELADO"
    pedido["fecha_cancelacion"] = datetime.now().isoformat()

    for item in pedido["productos"]:
        try:
            requests.post(f"{INVENTARIO_URL}/inventario/{item['producto_id']}/aumentar",
                         json={"cantidad": item["cantidad"]}, timeout=8)
        except:
            pass

    if pedido.get("transporte_id"):
        try:
            requests.put(f"{TRANSPORTE_URL}/transporte/{pedido['transporte_id']}",
                        json={"estado": "CANCELADO"}, timeout=8)
        except:
            pass

    return jsonify({
        "mensaje": f"Pedido {pedido_id} cancelado exitosamente",
        "pedido": pedido
    })

@app.route('/pedidos', methods=['GET'])
def listar_pedidos():
    estado = request.args.get("estado")
    if estado:
        filtrados = [p for p in pedidos.values() if p["estado"] == estado.upper()]
        return jsonify(filtrados)
    return jsonify(list(pedidos.values()))

@app.route('/promociones', methods=['GET'])
def listar_promociones():
    return jsonify(PROMOCIONES)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "servicio": "pedidos",
        "pedidos_total": len(pedidos),
        "uptime": "active",
        "version": "2.0.0"
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=False, threaded=True)
