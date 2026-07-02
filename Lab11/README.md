# Seguridad Informatica en Sistemas Distribuidos - Lab 11

## Logi Market Peru S.A.C. - Demostracion de Canal Seguro TLS, Autenticacion JWT y Auditoria

---

**Curso:** Sistemas Distribuidos
**Universidad:** Universidad Nacional de San Agustin (UNSA)
**Semestre:** 2026A
**Grupo:** B

---

## Tabla de Contenidos

1. [Requisitos Previos](#1-requisitos-previos)
2. [Estructura del Proyecto](#2-estructura-del-proyecto)
3. [Instalacion y Ejecucion](#3-instalacion-y-ejecucion)
4. [Interfaz Grafica Tkinter](#4-interfaz-grafica-tkinter)
5. [Verificacion del Canal Seguro](#5-verificacion-del-canal-seguro)
6. [Endpoints de la API](#6-endpoints-de-la-api)
7. [Pruebas con curl y Postman](#7-pruebas-con-curl-y-postman)
8. [Guia de Capturas de Pantalla (Evidencias)](#8-guia-de-capturas-de-pantalla-evidencias)
9. [Estructura de los Logs](#9-estructura-de-los-logs)
10. [Notas de Seguridad](#10-notas-de-seguridad)

---

## 1. Requisitos Previos

| Herramienta | Version Minima | Proposito |
|-------------|---------------|-----------|
| Python | 3.9+ | Ejecucion del servidor |
| OpenSSL | 1.1.1+ | Generacion de certificados (opcional, ver Python) |
| pip | 21.0+ | Gestion de dependencias |
| curl | 7.0+ | Verificacion del canal HTTPS |
| Git | 2.0+ | Clonacion del repositorio |

---

## 2. Estructura del Proyecto

```
Lab11/
├── main.py                 # Lanzador: inicia API Gateway HTTPS + GUI Tkinter
├── app.py                  # API Gateway seguro (Flask + TLS + JWT + RBAC + Auditoria)
├── requirements.txt        # Dependencias Python
├── generate_certs.sh       # Script OpenSSL (Linux/Mac)
├── generate_certs.bat      # Script OpenSSL (Windows, requiere OpenSSL)
├── generate_certs.py       # Script Python (multiplataforma, no requiere OpenSSL)
├── README.md               # Este archivo (guia de instalacion y ejecucion)
├── INFORME.md              # Informe tecnico del laboratorio
├── gui/
│   ├── __init__.py         # Marcador de paquete Python
│   └── app.py              # Interfaz grafica Tkinter (7 pestañas)
├── certs/                  # Certificados generados (automatico)
│   ├── ca-key.pem
│   ├── ca-cert.pem
│   ├── server-key.pem
│   ├── server.csr
│   ├── server-cert.pem
│   └── server-ext.cnf
└── logs/                   # Logs de auditoria y seguridad (automatico)
    ├── audit.log
    └── security.log
```

---

## 3. Instalacion y Ejecucion

### 3.1 Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd Lab11
```

### 3.2 Crear Entorno Virtual (Recomendado)

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3.3 Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3.4 Generar Certificados SSL

Python (recomendado, multiplataforma):**

```bash
python generate_certs.py
```

No requiere OpenSSL instalado. Usa la libreria `cryptography` (incluida en `requirements.txt`).


> **Nota:** Si los certificados no existen al iniciar `app.py`, se generan automaticamente usando la Opcion A.

Esto genera en `./certs/`:
- Una CA raiz local (`ca-cert.pem`, `ca-key.pem`)
- Un certificado de servidor firmado por la CA (`server-cert.pem`, `server-key.pem`)
- Valido para `localhost`, `127.0.0.1`, `::1`

### 3.5 Iniciar el Servidor HTTPS (solo backend)

```bash
python app.py
```

El servidor inicia en `https://localhost:8443`.

### 3.6 Iniciar con Interfaz Grafica (Recomendado)

```bash
python main.py
```

Esto inicia automaticamente:
1. Verifica/genera los certificados SSL en `./certs/`
2. Libera el puerto 8443 si esta ocupado
3. Lanza el API Gateway HTTPS en segundo plano
4. Una vez que el servidor responde, abre la GUI Tkinter

> **Nota:** Al cerrar la ventana de la GUI, el servidor se detiene automaticamente.

**Usuarios de prueba precargados:**

| Usuario | Contrasena | Rol |
|---------|-----------|-----|
| `admin` | `Admin@2026!` | admin |
| `operador` | `Oper@dor#2026` | operador |
| `cliente` | `Client3$2026` | cliente |

El codigo MFA simulado acepta cualquier numero de 6 digitos (ej. `123456`).

---

## 4. Interfaz Grafica Tkinter

### 4.1 Pestanas de la GUI

Al ejecutar `python main.py` se abre una ventana con las siguientes pestanas:

| Pestana | Actividad Relacionada | Descripcion |
|---------|----------------------|-------------|
| **Dashboard** | Actividad 1 - Matriz de Riesgos | Tarjetas de estado del sistema y tabla de matriz de riesgos con colores por nivel (Critico/Alto/Medio) |
| **Login / Auth** | Actividad 2 - Autenticacion Segura | Formulario de inicio de sesion con MFA (usuario + contrasena + codigo 6 digitos), diagrama de arquitectura de autenticacion, tabla de roles RBAC |
| **Inventario** | Actividad 4 - Proteccion de APIs | Listado de productos del microservicio de inventario, consulta protegida por JWT y RBAC |
| **Pagos** | Actividad 4 - Proteccion de APIs | Formulario para procesar pagos (monto + metodo), historial de pagos, rate limit de 20 req/min |
| **Logistica** | Actividad 4 - Proteccion de APIs | Formulario para crear envios (destino + productos), listado de envios programados |
| **Auditoria** | Actividad 5 - Sistema de Auditoria | Visualizacion de logs de auditoria y seguridad en tiempo real, tabla de eventos auditables criticos con tiempos de retencion |
| **Seguridad TLS** | Actividad 3 - Comunicaciones Seguras | Informacion del certificado TLS, arquitectura de seguridad integral, boton de verificacion de health check y comandos curl |

### 4.2 Flujo de Uso Recomendado

1. Ejecutar `python main.py`
2. En la pestana **Login / Auth**, ingresar credenciales y hacer clic en "Iniciar Sesion (MFA)"
3. Una vez autenticado, explorar:
   - **Inventario** - clic en "Actualizar Listado" para ver productos via API protegida
   - **Pagos** - ingresar monto y procesar pago
   - **Logistica** - ingresar destino y programar envio
   - **Auditoria** - clic en "Logs Auditoria" y "Logs Seguridad" para ver registros
   - **Seguridad TLS** - clic en "Verificar Health Check" para confirmar canal seguro
4. Para probar control de acceso: iniciar sesion como `cliente` e intentar usar **Auditoria** (debe denegar)
5. Cerrar sesion con el boton "Cerrar Sesion" al finalizar

---

### 5.1 Verificar que el servidor responde por HTTPS

```bash
curl -k https://localhost:8443/api/health
```

Respuesta esperada:

```json
{"estado":"operativo","servicio":"api-gateway-seguro","tls":"activo","timestamp":"..."}
```

### 5.2 Verificar los detalles del certificado TLS

```bash
openssl s_client -connect localhost:8443 -showcerts 2>&1 | openssl x509 -text -noout | grep -E "Subject:|Issuer:|Not Before|Not After|DNS:"
```

### 5.3 Verificar que HTTP sin TLS es rechazado

```bash
curl http://localhost:8443/api/health
# Debe retornar error o conexion rechazada (el servidor solo escucha HTTPS)
```

### 5.4 Verificar que endpoints requieren autenticacion

```bash
curl -k https://localhost:8443/api/inventory
# Respuesta: 401 - Token de autorizacion requerido
```

---

## 6. Endpoints de la API

### 6.1 Autenticacion

| Metodo | Endpoint | Descripcion | Rate Limit |
|--------|----------|-------------|------------|
| POST | `/api/auth/login` | Iniciar sesion con MFA | 10 req/min |
| POST | `/api/auth/logout` | Cerrar sesion (revoca token) | - |

### 6.2 Inventario

| Metodo | Endpoint | Descripcion | Rol Requerido | Rate Limit |
|--------|----------|-------------|---------------|------------|
| GET | `/api/inventory` | Listar todos los productos | admin, operador, cliente | 60 req/min |
| GET | `/api/inventory/<id>` | Consultar producto por ID | admin, operador, cliente | 60 req/min |

### 6.3 Pagos

| Metodo | Endpoint | Descripcion | Rol Requerido | Rate Limit |
|--------|----------|-------------|---------------|------------|
| GET | `/api/payments` | Listar pagos | admin, operador | 60 req/min |
| POST | `/api/payments` | Procesar un pago | admin, operador | 20 req/min |

### 6.4 Logistica

| Metodo | Endpoint | Descripcion | Rol Requerido | Rate Limit |
|--------|----------|-------------|---------------|------------|
| GET | `/api/logistics` | Listar envios | admin, operador, cliente | 60 req/min |
| POST | `/api/logistics` | Crear un envio | admin, operador | 30 req/min |

### 6.5 Auditoria

| Metodo | Endpoint | Descripcion | Rol Requerido | Rate Limit |
|--------|----------|-------------|---------------|------------|
| GET | `/api/audit/logs` | Consultar logs de auditoria | admin | 20 req/min |
| GET | `/api/audit/security` | Consultar logs de seguridad | admin | 20 req/min |

### 6.6 Health Check

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/api/health` | Estado del servicio (publico) |

---

## 7. Pruebas con curl y Postman

### 7.1 Flujo Completo con curl

```bash
# Variable para el token
TOKEN=""

# 1. Health check (no requiere autenticacion)
curl -k https://localhost:8443/api/health

# 2. Login como admin
curl -k -X POST https://localhost:8443/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"usuario":"admin","password":"Admin@2026!","mfa_code":"123456"}'

# 3. Guardar el token de la respuesta y consultar inventario
TOKEN="<access_token_de_la_respuesta>"
curl -k https://localhost:8443/api/inventory \
  -H "Authorization: Bearer $TOKEN"

# 4. Consultar un producto especifico
curl -k https://localhost:8443/api/inventory/P001 \
  -H "Authorization: Bearer $TOKEN"

# 5. Procesar un pago
curl -k -X POST https://localhost:8443/api/payments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"monto":150.00,"metodo":"tarjeta"}'

# 6. Listar pagos
curl -k https://localhost:8443/api/payments \
  -H "Authorization: Bearer $TOKEN"

# 7. Crear envio en logistica
curl -k -X POST https://localhost:8443/api/logistics \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"destino":"Av. Ejercito 123, Arequipa","productos":["P001","P003"]}'

# 8. Ver logs de auditoria (solo admin)
curl -k https://localhost:8443/api/audit/logs \
  -H "Authorization: Bearer $TOKEN"

# 9. Verificar que cliente no puede acceder a endpoint admin
# (loguearse como cliente y probar /api/audit/logs)
curl -k -X POST https://localhost:8443/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"usuario":"cliente","password":"Client3$2026","mfa_code":"123456"}'
# Usar el token de cliente para intentar acceder a /api/audit/logs

# 10. Cerrar sesion
curl -k -X POST https://localhost:8443/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

### 7.2 Probar Rate Limiting

```bash
# Realizar mas de 10 intentos de login en menos de 1 minuto
for i in $(seq 1 12); do
  curl -k -X POST https://localhost:8443/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"usuario":"admin","password":"Admin@2026!","mfa_code":"123456"}' &
done
# El request 11 y 12 retornaran 429 Too Many Requests
```

### 7.3 Probar Bloqueo por Intentos Fallidos

```bash
# Realizar 5+ intentos fallidos de login
for i in $(seq 1 6); do
  curl -k -X POST https://localhost:8443/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"usuario":"admin","password":"password_incorrecta","mfa_code":"123456"}'
done
# Despues del 5to intento, la cuenta se bloquea (HTTP 423 Locked)
```

### 7.4 Configuracion en Postman

1. **Deshabilitar verificacion SSL:** Settings > General > SSL certificate verification: OFF
2. **Login:**
   - Method: `POST`
   - URL: `https://localhost:8443/api/auth/login`
   - Body (raw JSON):
     ```json
     {"usuario":"admin","password":"Admin@2026!","mfa_code":"123456"}
     ```
3. **Usar el token:** Copiar `access_token` de la respuesta
4. **Autorizar requests subsiguientes:** Tab Authorization > Type: Bearer Token > Pegar token

---

## 8. Guia de Capturas de Pantalla (Evidencias)

Para el informe academico, se recomienda capturar las siguientes pantallas como evidencia de cada actividad. Las imagenes deben guardarse en `Lab11/evidencias/` con los nombres sugeridos.

| Actividad | Pestana / Accion | Captura Sugerida | Nombre de Archivo |
|-----------|-----------------|-----------------|-------------------|
| **1** | Dashboard | Ventana completa mostrando la matriz de riesgos con las 6 filas coloreadas (Critico rojo, Alto naranja, Medio azul) y las tarjetas de estado en la parte superior | `evidencias/actividad1_matriz_riesgos.png` |
| **2** | Login / Auth | Ventana de autenticacion despues de hacer login exitoso como admin, mostrando el token JWT en el panel izquierdo, el diagrama de flujo OAuth 2.0 + MFA en el panel derecho, y la tabla RBAC con los 3 roles | `evidencias/actividad2_login_mfa.png` |
| **2** | Login / Auth | Intento de login fallido (contrasena incorrecta) mostrando el mensaje de error 401 y el indicador rojo de "Error de autenticacion" | `evidencias/actividad2_login_fallido.png` |
| **3** | Seguridad TLS | Pestana Seguridad TLS completa mostrando informacion del certificado, beneficios TLS, arquitectura de seguridad integral, y resultado del health check exitoso | `evidencias/actividad3_tls_certificado.png` |
| **3** | Terminal | Captura de terminal ejecutando `openssl s_client` o `curl -k` contra `https://localhost:8443/api/health` mostrando la respuesta JSON | `evidencias/actividad3_curl_health.png` |
| **3** | Terminal | Captura de terminal ejecutando `curl http://localhost:8443/api/health` (sin TLS) mostrando que el servidor lo rechaza | `evidencias/actividad3_http_rechazado.png` |
| **4** | Inventario | Pestana Inventario con el listado de 5 productos cargados exitosamente mediante el API protegida con JWT | `evidencias/actividad4_inventario.png` |
| **4** | Pagos | Pestana Pagos mostrando un pago procesado exitosamente en el panel izquierdo y el historial de pagos en el panel derecho | `evidencias/actividad4_pagos.png` |
| **4** | Logistica | Pestana Logistica mostrando un envio programado y el listado de envios | `evidencias/actividad4_logistica.png` |
| **4** | Login / Auth | Iniciar sesion como `cliente`, luego intentar acceder a la pestana Auditoria (debe denegar con 403), capturar el error | `evidencias/actividad4_rbac_denegado.png` |
| **4** | Terminal | Prueba de rate limit: ejecutar 12 login requests y capturar el error 429 "Too Many Requests" | `evidencias/actividad4_rate_limit.png` |
| **5** | Auditoria | Pestana Auditoria mostrando los logs de auditoria (audit.log) y logs de seguridad (security.log) con eventos registrados, mas la tabla de eventos auditables criticos | `evidencias/actividad5_logs_auditoria.png` |
| **5** | Terminal | Captura del contenido de `logs/audit.log` y `logs/security.log` mostrando el formato JSON estructurado | `evidencias/actividad5_archivos_log.png` |
| **5** | Dashboard | Ventana completa de Dashboard con la matriz de riesgos y las tarjetas de estado del sistema | `evidencias/actividad5_dashboard_general.png` |
| **General** | Explorer | Captura del explorador de archivos mostrando la estructura completa del proyecto `Lab11/` | `evidencias/estructura_proyecto.png` |
| **General** | GUI completa | Ventana completa de la GUI Tkinter con las 7 pestanas visibles en la parte superior | `evidencias/gui_completa.png` |

### 8.1 Estructura de la Carpeta de Evidencias

```
Lab11/evidencias/
├── actividad1_matriz_riesgos.png
├── actividad2_login_mfa.png
├── actividad2_login_fallido.png
├── actividad3_tls_certificado.png
├── actividad3_curl_health.png
├── actividad3_http_rechazado.png
├── actividad4_inventario.png
├── actividad4_pagos.png
├── actividad4_logistica.png
├── actividad4_rbac_denegado.png
├── actividad4_rate_limit.png
├── actividad5_logs_auditoria.png
├── actividad5_archivos_log.png
├── actividad5_dashboard_general.png
├── estructura_proyecto.png
└── gui_completa.png
```

---

## 9. Estructura de los Logs

### 9.1 audit.log

Registra todas las operaciones de negocio:

```json
{"timestamp":"2026-07-02T12:00:00","level":"INFO","message":{"evento":"LOGIN_EXITOSO","usuario":"admin","detalle":"Inicio de sesion con MFA desde 127.0.0.1","direccion_ip":"127.0.0.1","exitoso":true,"timestamp_utc":"2026-07-02T17:00:00Z"}}
```

### 9.2 security.log

Registra eventos de seguridad (intentos fallidos, rate limiting, tokens invalidos):

```json
{"timestamp":"2026-07-02T12:00:00","event":{"tipo":"AUTH_FAILED","direccion_ip":"127.0.0.1","detalle":"Contrasena incorrecta","timestamp_utc":"2026-07-02T17:00:00Z"}}
```

---

## 10. Notas de Seguridad

- Los certificados generados son para entorno de desarrollo local. En produccion se deben usar certificados emitidos por una CA publica confiable (ej. Let's Encrypt, DigiCert).
- La clave `JWT_SECRET` debe configurarse como variable de entorno en produccion.
- Las contrasenas en este demo estan hasheadas con SHA-256. En produccion se debe usar bcrypt o Argon2.
- El MFA esta simulado. En produccion se integraria con TOTP (Google Authenticator) o WebAuthn.
