# Lab 07 — SOAP Web Services
**Sistemas Distribuidos · UNSA 2026A · Grupo B**

---

## Archivos del proyecto

```
Lab07/
├── cliente_soap.py       # Ejercicio 2: cliente SOAP directo con Python
├── proxy_soap.py         # Servidor proxy para el frontend HTML
└── calculadora_soap.html # Frontend visual (requiere proxy activo)
```

---

## Ejercicio 2 — Cliente SOAP con Python

Consume directamente el servicio SOAP público `dneonline.com/calculator.asmx`.

### 1. Instalar dependencia

```bash
pip install zeep
```

### 2. Ejecutar

```bash
python cliente_soap.py
```

### Salida esperada

```
Conectando al servicio SOAP...
Conexión exitosa.

==================================================
  CALCULADORA SOAP - Resultados
==================================================
  Add(5, 8)       = 13
  Subtract(20, 7) = 13
  Multiply(6, 9)  = 54
  Divide(100, 4)  = 25
==================================================
  Resultado esperado Add(5,8): 13
  Resultado obtenido:          13
==================================================
```

---

## Actividad adicional — Frontend HTML con Proxy

El navegador no puede llamar directamente a servicios SOAP externos
por la **política CORS**. Se usa un proxy Python intermedio:

```
calculadora_soap.html  →  proxy_soap.py (:5000)  →  dneonline.com
     (fetch JSON)            (zeep / SOAP)            (XML)
```

### 1. Instalar dependencias

```bash
pip install flask flask-cors zeep
```

### 2. Iniciar el proxy (déjalo corriendo en esta terminal)

```bash
python proxy_soap.py
```

Deberías ver:
```
=======================================================
  Proxy SOAP iniciado en http://localhost:5000
  Abre calculadora_soap.html en tu navegador
=======================================================
```

### 3. Abrir el frontend

Abre `calculadora_soap.html` directamente en tu navegador
(doble clic sobre el archivo).

El punto de estado en la esquina superior derecha del panel
se pondrá **verde** cuando el proxy esté activo.

### 4. Usar la calculadora

- Ingresa los valores A y B
- Selecciona la operación (+, −, ×, ÷)
- Pulsa **SEND SOAP REQUEST**
- El resultado aparece en pantalla y en el log

---

## Requisitos

| Herramienta | Versión mínima |
|-------------|---------------|
| Python      | 3.8+          |
| zeep        | cualquiera    |
| flask       | cualquiera    |
| flask-cors  | cualquiera    |

---

## Troubleshooting

**"Proxy no detectado" / punto rojo en el HTML**
→ El proxy no está corriendo. Ejecuta `python proxy_soap.py` primero.

**Error 403 en `cliente_soap.py`**
→ El servidor externo bloqueó la petición desde ese entorno (ocurre
en algunas redes universitarias). Prueba desde tu red personal.

**`ModuleNotFoundError: No module named 'zeep'`**
→ Ejecuta `pip install zeep` (o `pip3 install zeep`).

**`ModuleNotFoundError: No module named 'flask'`**
→ Ejecuta `pip install flask flask-cors`.
