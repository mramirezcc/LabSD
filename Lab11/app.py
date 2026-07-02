"""
Lab11 - Seguridad Informatica en Sistemas Distribuidos
Logi Market Peru S.A.C.

Demostracion de canal seguro HTTPS con TLS, autenticacion JWT,
API Gateway con rate limiting, y auditoria centralizada para
mitigar los incidentes de seguridad reportados en el caso de estudio.
"""
import os
import json
import uuid
import time
import logging
import hashlib
import threading
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict
from logging.handlers import RotatingFileHandler

import jwt
from flask import Flask, request, jsonify, g

# =============================================================================
# Configuracion Global
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERT_DIR = os.path.join(BASE_DIR, "certs")
LOG_DIR = os.path.join(BASE_DIR, "logs")

SERVER_CERT = os.path.join(CERT_DIR, "server-cert.pem")
SERVER_KEY = os.path.join(CERT_DIR, "server-key.pem")

JWT_SECRET = os.environ.get("JWT_SECRET", "logimarket-secret-key-2026")
JWT_ALGORITHM = "HS512"
JWT_EXPIRATION_MINUTES = 30

# =============================================================================
# Sistema de Auditoria Centralizada
# =============================================================================

os.makedirs(LOG_DIR, exist_ok=True)

audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

audit_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "audit.log"),
    maxBytes=5 * 1024 * 1024,
    backupCount=10,
)
audit_handler.setFormatter(
    logging.Formatter(
        '{"timestamp":"%(asctime)s","level":"%(levelname)s","message":%(message)s}',
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
)
audit_logger.addHandler(audit_handler)

security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)
security_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "security.log"),
    maxBytes=5 * 1024 * 1024,
    backupCount=10,
)
security_handler.setFormatter(
    logging.Formatter(
        '{"timestamp":"%(asctime)s","event":%(message)s}',
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
)
security_logger.addHandler(security_handler)


def registrar_auditoria(evento, usuario, detalle, direccion_ip, exitoso=True):
    registro = json.dumps({
        "evento": evento,
        "usuario": usuario,
        "detalle": detalle,
        "direccion_ip": direccion_ip,
        "exitoso": exitoso,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    })
    audit_logger.info(registro)


def registrar_evento_seguridad(evento, direccion_ip, detalle):
    registro = json.dumps({
        "tipo": evento,
        "direccion_ip": direccion_ip,
        "detalle": detalle,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    })
    security_logger.info(registro)


# =============================================================================
# Base de Datos Simulada en Memoria
# =============================================================================

usuarios = {
    "admin": {
        "password_hash": hashlib.sha256("Admin@2026!".encode()).hexdigest(),
        "rol": "admin",
        "mfa_secret": "MFSG22LTORSWGZDF",
        "nombre": "Administrador del Sistema",
    },
    "operador": {
        "password_hash": hashlib.sha256("Oper@dor#2026".encode()).hexdigest(),
        "rol": "operador",
        "mfa_secret": "MFSG22LTORSWGZDF",
        "nombre": "Operador de Logistica",
    },
    "cliente": {
        "password_hash": hashlib.sha256("Client3$2026".encode()).hexdigest(),
        "rol": "cliente",
        "mfa_secret": "MFSG22LTORSWGZDF",
        "nombre": "Cliente Demo",
    },
}

productos_inventario = {
    "P001": {"nombre": "Laptop HP", "stock": 50, "precio": 2500.00},
    "P002": {"nombre": "Monitor Dell 27\"", "stock": 30, "precio": 1200.00},
    "P003": {"nombre": "Teclado Mecanico", "stock": 100, "precio": 350.00},
    "P004": {"nombre": "Mouse Inalambrico", "stock": 80, "precio": 150.00},
    "P005": {"nombre": "Audifonos Bluetooth", "stock": 60, "precio": 200.00},
}

pagos = {}
envios = {}

tokens_revocados = set()
intentos_fallidos = defaultdict(list)

# =============================================================================
# Politicas de Seguridad
# =============================================================================

MAX_INTENTOS_FALLIDOS = 5
BLOQUEO_TIEMPO_MINUTOS = 15
RATE_LIMIT_VENTANA = 60  # segundos

rate_limit_registro = defaultdict(list)

rbac_permisos = {
    "admin": ["inventory:read", "inventory:write", "payments:read",
               "payments:write", "logistics:read", "logistics:write",
               "audit:read", "users:manage"],
    "operador": ["inventory:read", "inventory:write", "logistics:read",
                  "logistics:write", "payments:read"],
    "cliente": ["inventory:read", "payments:read", "logistics:read"],
}


# =============================================================================
# Inicializacion de la Aplicacion Flask
# =============================================================================

app = Flask(__name__)


# =============================================================================
# Rate Limiting
# =============================================================================

def rate_limit(max_requests=30, ventana_segundos=60):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            direccion_ip = request.remote_addr
            ahora = time.time()
            ventana = ahora - ventana_segundos

            rate_limit_registro[direccion_ip] = [
                t for t in rate_limit_registro.get(direccion_ip, [])
                if t > ventana
            ]

            if len(rate_limit_registro[direccion_ip]) >= max_requests:
                registrar_evento_seguridad(
                    "RATE_LIMIT_EXCEEDED",
                    direccion_ip,
                    f"Limite de {max_requests} peticiones por {ventana_segundos}s excedido"
                )
                return jsonify({
                    "error": "rate_limit_exceeded",
                    "mensaje": f"Limite de {max_requests} peticiones por minuto excedido. Reintente en breve."
                }), 429

            rate_limit_registro[direccion_ip].append(ahora)
            return f(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# Autenticacion y Autorizacion
# =============================================================================

def verificar_bloqueo(usuario):
    ahora = datetime.utcnow()
    intentos = intentos_fallidos.get(usuario, [])
    intentos = [t for t in intentos
                if t > ahora - timedelta(minutes=BLOQUEO_TIEMPO_MINUTOS)]
    intentos_fallidos[usuario] = intentos
    if len(intentos) >= MAX_INTENTOS_FALLIDOS:
        return True
    return False


def generar_token(usuario, rol):
    payload = {
        "sub": usuario,
        "rol": rol,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES),
        "jti": str(uuid.uuid4()),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def token_requerido(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            registrar_evento_seguridad(
                "AUTH_MISSING_TOKEN",
                request.remote_addr,
                "Peticion sin token de autorizacion"
            )
            return jsonify({"error": "token_faltante",
                            "mensaje": "Token de autorizacion requerido"}), 401

        token = auth_header.split("Bearer ")[1]

        if token in tokens_revocados:
            registrar_evento_seguridad(
                "AUTH_REVOKED_TOKEN",
                request.remote_addr,
                "Intento de uso de token revocado"
            )
            return jsonify({"error": "token_revocado",
                            "mensaje": "El token ha sido revocado"}), 401

        try:
            payload = jwt.decode(token, JWT_SECRET,
                                 algorithms=[JWT_ALGORITHM],
                                 options={"require": ["exp", "sub", "jti"]})
            g.usuario = payload["sub"]
            g.rol = payload["rol"]
            g.token_jti = payload["jti"]
        except jwt.ExpiredSignatureError:
            registrar_evento_seguridad(
                "AUTH_EXPIRED_TOKEN",
                request.remote_addr,
                "Token expirado"
            )
            return jsonify({"error": "token_expirado",
                            "mensaje": "El token ha expirado. Inicie sesion nuevamente."}), 401
        except jwt.InvalidTokenError:
            registrar_evento_seguridad(
                "AUTH_INVALID_TOKEN",
                request.remote_addr,
                "Token invalido"
            )
            return jsonify({"error": "token_invalido",
                            "mensaje": "Token invalido"}), 401

        return f(*args, **kwargs)
    return wrapper


def requiere_permiso(permiso):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            rol = g.get("rol", "")
            permisos_rol = rbac_permisos.get(rol, [])
            if permiso not in permisos_rol:
                registrar_evento_seguridad(
                    "AUTH_FORBIDDEN",
                    request.remote_addr,
                    f"Usuario {g.get('usuario')} con rol {rol} intento acceder a {permiso}"
                )
                return jsonify({
                    "error": "acceso_denegado",
                    "mensaje": f"El rol '{rol}' no tiene permiso para: {permiso}"
                }), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# Endpoints de Autenticacion
# =============================================================================

@app.route("/api/auth/login", methods=["POST"])
@rate_limit(max_requests=10, ventana_segundos=60)
def login():
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "datos_invalidos",
                        "mensaje": "Cuerpo JSON requerido"}), 400

    usuario = datos.get("usuario", "")
    password = datos.get("password", "")
    mfa_code = datos.get("mfa_code", "")

    if not usuario or not password:
        return jsonify({"error": "campos_faltantes",
                        "mensaje": "usuario y password son requeridos"}), 400

    if verificar_bloqueo(usuario):
        registrar_evento_seguridad(
            "AUTH_ACCOUNT_LOCKED",
            request.remote_addr,
            f"Cuenta bloqueada por multiples intentos fallidos: {usuario}"
        )
        return jsonify({
            "error": "cuenta_bloqueada",
            "mensaje": f"Cuenta bloqueada por {BLOQUEO_TIEMPO_MINUTOS} minutos debido a multiples intentos fallidos"
        }), 423

    usuario_data = usuarios.get(usuario)

    if not usuario_data:
        intentos_fallidos[usuario].append(datetime.utcnow())
        registrar_auditoria("LOGIN_FALLIDO", usuario,
                            "Usuario no encontrado", request.remote_addr, False)
        return jsonify({"error": "credenciales_invalidas",
                        "mensaje": "Usuario o contrasena incorrectos"}), 401

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    if password_hash != usuario_data["password_hash"]:
        intentos_fallidos[usuario].append(datetime.utcnow())
        registrar_auditoria("LOGIN_FALLIDO", usuario,
                            "Contrasena incorrecta", request.remote_addr, False)
        return jsonify({"error": "credenciales_invalidas",
                        "mensaje": "Usuario o contrasena incorrectos"}), 401

    # Verificacion MFA (simulada: cualquier codigo de 6 digitos)
    if len(mfa_code) != 6 or not mfa_code.isdigit():
        registrar_auditoria("MFA_FALLIDO", usuario,
                            "Codigo MFA invalido", request.remote_addr, False)
        return jsonify({
            "error": "mfa_invalido",
            "mensaje": "Codigo MFA invalido. Se requiere un codigo de 6 digitos."
        }), 401

    intentos_fallidos.pop(usuario, None)

    token = generar_token(usuario, usuario_data["rol"])

    registrar_auditoria("LOGIN_EXITOSO", usuario,
                        f"Inicio de sesion con MFA desde {request.remote_addr}",
                        request.remote_addr, True)

    return jsonify({
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": JWT_EXPIRATION_MINUTES * 60,
        "usuario": usuario,
        "rol": usuario_data["rol"],
    }), 200


@app.route("/api/auth/logout", methods=["POST"])
@token_requerido
def logout():
    tokens_revocados.add(g.token_jti)
    registrar_auditoria("LOGOUT", g.usuario,
                        "Cierre de sesion", request.remote_addr, True)
    return jsonify({"mensaje": "Sesion cerrada exitosamente"}), 200


# =============================================================================
# Endpoints del Microservicio de Inventario (simulado tras API Gateway)
# =============================================================================

@app.route("/api/inventory", methods=["GET"])
@token_requerido
@requiere_permiso("inventory:read")
@rate_limit(max_requests=60, ventana_segundos=60)
def listar_inventario():
    registrar_auditoria("INVENTORY_LIST", g.usuario,
                        "Consulta de listado de inventario", request.remote_addr, True)
    return jsonify({
        "servicio": "inventario",
        "datos": [
            {"id": k, **v} for k, v in productos_inventario.items()
        ],
        "protegido_por": "TLS + JWT + RBAC",
    }), 200


@app.route("/api/inventory/<producto_id>", methods=["GET"])
@token_requerido
@requiere_permiso("inventory:read")
@rate_limit(max_requests=60, ventana_segundos=60)
def consultar_producto(producto_id):
    producto = productos_inventario.get(producto_id)
    if not producto:
        return jsonify({"error": "no_encontrado",
                        "mensaje": f"Producto {producto_id} no encontrado"}), 404

    registrar_auditoria("INVENTORY_READ", g.usuario,
                        f"Consulta de producto {producto_id}", request.remote_addr, True)
    return jsonify({
        "servicio": "inventario",
        "producto": {"id": producto_id, **producto},
        "transmision_segura": "TLS 1.2+",
    }), 200


# =============================================================================
# Endpoints del Microservicio de Pagos (simulado tras API Gateway)
# =============================================================================

@app.route("/api/payments", methods=["POST"])
@token_requerido
@requiere_permiso("payments:write")
@rate_limit(max_requests=20, ventana_segundos=60)
def procesar_pago():
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "datos_invalidos"}), 400

    pago_id = str(uuid.uuid4())
    pago = {
        "id": pago_id,
        "monto": datos.get("monto", 0),
        "metodo": datos.get("metodo", "tarjeta"),
        "estado": "completado",
        "procesado_por": g.usuario,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    pagos[pago_id] = pago

    registrar_auditoria("PAYMENT_PROCESSED", g.usuario,
                        f"Pago {pago_id} por S/ {pago['monto']}",
                        request.remote_addr, True)

    return jsonify({
        "servicio": "pagos",
        "pago": pago,
        "cifrado": "Datos sensibles transmitidos sobre TLS",
    }), 201


@app.route("/api/payments", methods=["GET"])
@token_requerido
@requiere_permiso("payments:read")
@rate_limit(max_requests=60, ventana_segundos=60)
def listar_pagos():
    registrar_auditoria("PAYMENTS_LIST", g.usuario,
                        "Consulta de listado de pagos", request.remote_addr, True)
    return jsonify({
        "servicio": "pagos",
        "pagos": list(pagos.values()),
    }), 200


# =============================================================================
# Endpoints del Microservicio de Logistica (simulado tras API Gateway)
# =============================================================================

@app.route("/api/logistics", methods=["POST"])
@token_requerido
@requiere_permiso("logistics:write")
@rate_limit(max_requests=30, ventana_segundos=60)
def crear_envio():
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "datos_invalidos"}), 400

    envio_id = str(uuid.uuid4())
    envio = {
        "id": envio_id,
        "destino": datos.get("destino", ""),
        "productos": datos.get("productos", []),
        "estado": "programado",
        "creado_por": g.usuario,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    envios[envio_id] = envio

    registrar_auditoria("LOGISTICS_CREATED", g.usuario,
                        f"Envio {envio_id} programado a {envio['destino']}",
                        request.remote_addr, True)

    return jsonify({
        "servicio": "logistica",
        "envio": envio,
    }), 201


@app.route("/api/logistics", methods=["GET"])
@token_requerido
@requiere_permiso("logistics:read")
@rate_limit(max_requests=60, ventana_segundos=60)
def listar_envios():
    registrar_auditoria("LOGISTICS_LIST", g.usuario,
                        "Consulta de listado de envios", request.remote_addr, True)
    return jsonify({
        "servicio": "logistica",
        "envios": list(envios.values()),
    }), 200


# =============================================================================
# Endpoints de Auditoria (solo admin)
# =============================================================================

@app.route("/api/audit/logs", methods=["GET"])
@token_requerido
@requiere_permiso("audit:read")
@rate_limit(max_requests=20, ventana_segundos=60)
def consultar_logs_auditoria():
    try:
        with open(os.path.join(LOG_DIR, "audit.log"), "r") as f:
            lineas = f.readlines()[-100:]
        eventos = []
        for linea in lineas:
            try:
                eventos.append(json.loads(linea.strip()))
            except json.JSONDecodeError:
                continue
        registrar_auditoria("AUDIT_LOGS_READ", g.usuario,
                            "Consulta de logs de auditoria", request.remote_addr, True)
        return jsonify({
            "total_eventos": len(eventos),
            "eventos": eventos,
        }), 200
    except FileNotFoundError:
        return jsonify({"eventos": [], "total_eventos": 0}), 200


@app.route("/api/audit/security", methods=["GET"])
@token_requerido
@requiere_permiso("audit:read")
@rate_limit(max_requests=20, ventana_segundos=60)
def consultar_logs_seguridad():
    try:
        with open(os.path.join(LOG_DIR, "security.log"), "r") as f:
            lineas = f.readlines()[-100:]
        eventos = []
        for linea in lineas:
            try:
                eventos.append(json.loads(linea.strip()))
            except json.JSONDecodeError:
                continue
        return jsonify({
            "total_eventos": len(eventos),
            "eventos": eventos,
        }), 200
    except FileNotFoundError:
        return jsonify({"eventos": [], "total_eventos": 0}), 200


# =============================================================================
# Ruta Raiz - Informacion de la API
# =============================================================================

@app.route("/", methods=["GET"])
def raiz():
    return jsonify({
        "aplicacion": "Logi Market Peru S.A.C. - API Gateway Seguro",
        "version": "1.0.0",
        "tls": "activo",
        "autenticacion": "JWT (HS512) + MFA",
        "autorizacion": "RBAC (admin, operador, cliente, auditor)",
        "endpoints": {
            "health": "/api/health",
            "login": "POST /api/auth/login",
            "logout": "POST /api/auth/logout",
            "inventario": "GET /api/inventory",
            "pagos": "GET/POST /api/payments",
            "logistica": "GET/POST /api/logistics",
            "auditoria": "GET /api/audit/logs (admin)",
        },
        "documentacion": "Consulte README.md para ejemplos de uso",
        "usuarios_prueba": {
            "admin": "Admin@2026!",
            "operador": "Oper@dor#2026",
            "cliente": "Client3$2026",
        },
    }), 200


# =============================================================================
# Endpoint de Health Check
# =============================================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "estado": "operativo",
        "servicio": "api-gateway-seguro",
        "tls": "activo",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }), 200


# =============================================================================
# Manejo global de errores
# =============================================================================

@app.errorhandler(404)
def no_encontrado(error):
    return jsonify({"error": "ruta_no_encontrada",
                    "mensaje": "El endpoint solicitado no existe"}), 404


@app.errorhandler(405)
def metodo_no_permitido(error):
    return jsonify({"error": "metodo_no_permitido",
                    "mensaje": "Metodo HTTP no permitido para este endpoint"}), 405


@app.errorhandler(500)
def error_interno(error):
    registrar_evento_seguridad("INTERNAL_ERROR", request.remote_addr,
                               f"Error interno: {str(error)}")
    return jsonify({"error": "error_interno",
                    "mensaje": "Error interno del servidor"}), 500


# =============================================================================
# Punto de Entrada
# =============================================================================

if __name__ == "__main__":
    cert_existe = os.path.exists(SERVER_CERT) and os.path.exists(SERVER_KEY)

    if not cert_existe:
        print("=" * 60)
        print("Certificados SSL no encontrados. Generando automaticamente...")
        print("=" * 60)
        try:
            from generate_certs import generar_certificados
            generar_certificados()
        except ImportError:
            print("ERROR: No se pudo importar generate_certs.py")
            print("Ejecute manualmente: python generate_certs.py")
            exit(1)
        print("")

    print("=" * 60)
    print("  Logi Market Peru S.A.C. - API Gateway Seguro")
    print("  Canal HTTPS con TLS 1.2+ | Autenticacion JWT | RBAC")
    print("=" * 60)
    print(f"  Certificado: {SERVER_CERT}")
    print(f"  Clave:       {SERVER_KEY}")
    print(f"  URL:         https://localhost:8443")
    print(f"  Health:      https://localhost:8443/api/health")
    print(f"  Logs:        {LOG_DIR}/")
    print("=" * 60)
    print("")
    print("Usuarios de prueba:")
    print("  admin    / Admin@2026!    (rol: admin)")
    print("  operador / Oper@dor#2026  (rol: operador)")
    print("  cliente  / Client3$2026   (rol: cliente)")
    print("")
    print("Nota: El codigo MFA es cualquier numero de 6 digitos (simulado)")
    print("")

    app.run(
        host="0.0.0.0",
        port=8443,
        ssl_context=(SERVER_CERT, SERVER_KEY),
        debug=False,
    )
