# 💬 Chat Distribuido Cliente-Servidor con Envío de Archivos en Python

## 📌 Descripción General

Este proyecto implementa un sistema de chat distribuido Cliente-Servidor utilizando Python, sockets TCP y multithreading, incorporando una interfaz gráfica desarrollada con Tkinter.

El sistema permite:

- Comunicación entre múltiples clientes.
- Mensajes públicos.
- Mensajes privados.
- Lista de usuarios conectados.
- Envío de archivos.
- Detección de usuarios duplicados.
- Interfaz gráfica para servidor y clientes.
- Comunicación segura mediante paquetes con longitud prefijada.

---

# 🏗️ Arquitectura del Sistema

```text
+--------------------------------------------------+
|                  SERVER GUI                      |
|--------------------------------------------------|
| - Socket TCP                                     |
| - Broadcast                                      |
| - Mensajes privados                              |
| - Transferencia de archivos                      |
| - Lista de usuarios                              |
| - Logs                                           |
+--------------------------------------------------+
                     ^
                     |
               TCP/IP SOCKETS
                     |
       +-------------+-------------+
       |                           |
       v                           v

+-------------------+     +-------------------+
|   CLIENT GUI 1    |     |   CLIENT GUI 2    |
+-------------------+     +-------------------+
```

---

# 📂 Estructura del Proyecto

```text
chat_project/
│
├── server_gui.py
├── client_gui.py
├── chat_message.py
└── README.md
```

---

# ⚙️ Tecnologías Utilizadas

## Lenguaje

- Python 3

## Librerías estándar

- socket
- threading
- pickle
- struct
- tkinter
- datetime
- os

No se requieren librerías externas.

---

# 🚀 Ejecución del Sistema

## 1️⃣ Ejecutar el servidor

```bash
python server_gui.py
```

---

## 2️⃣ Ejecutar clientes

```bash
python client_gui.py
```

Puede abrir múltiples clientes simultáneamente.

---

# 🌐 Comunicación de Red

## Protocolo

TCP/IP

## Tipo de socket

```python
socket.AF_INET
socket.SOCK_STREAM
```

---

# 📦 Protocolo de Comunicación

El sistema implementa un protocolo con prefijo de longitud para evitar fragmentación de mensajes TCP.

## Envío de paquetes

```python
def send_packet(sock, data: bytes):
    sock.sendall(struct.pack(">I", len(data)) + data)
```

---

## Recepción de paquetes

```python
def recv_packet(sock) -> bytes:
```

Esto garantiza:

- recepción completa
- integridad del mensaje
- soporte para archivos binarios

---

# 🧵 Concurrencia

El sistema utiliza:

```python
threading.Thread
```

para:

- servidor principal
- clientes conectados
- escucha de mensajes

Cada cliente conectado posee un hilo independiente.

---

# 🖥️ Interfaz Gráfica

El sistema posee GUI tanto para:

## Cliente

- área de chat
- lista de usuarios
- envío de mensajes
- envío de archivos
- mensajes privados

## Servidor

- logs del sistema
- clientes conectados
- control de inicio/parada

---

# 📄 Archivo: chat_message.py

## Descripción

Define los tipos de mensajes intercambiados entre cliente y servidor.

## Código

```python
class ChatMessage:

    WHOISIN = 0
    MESSAGE = 1
    LOGOUT = 2

    PRIVATE = 3
    FUNCTION = 4
    FILE = 5

    def __init__(self, msg_type, message, extra=None):
        self.type = msg_type
        self.message = message
        self.extra = extra

    def get_type(self):
        return self.type

    def get_message(self):
        return self.message

    def get_extra(self):
        return self.extra
```

---

# 📡 Tipos de Mensajes

| Tipo | Descripción |
|---|---|
| WHOISIN | Solicita lista de usuarios |
| MESSAGE | Mensaje público |
| LOGOUT | Desconexión |
| PRIVATE | Mensaje privado |
| FUNCTION | Función matemática |
| FILE | Transferencia de archivos |

---

# 💬 Mensajes Públicos

Los mensajes enviados son visibles para todos los clientes conectados.

## Ejemplo

```text
Juan: Hola a todos
```

---

# 🔒 Mensajes Privados

Los mensajes privados utilizan el formato:

```text
@usuario mensaje
```

## Ejemplo

```text
@Pedro Hola Pedro
```

El servidor reenvía únicamente al destinatario.

---

# 📂 Transferencia de Archivos

## Funcionalidad

El sistema permite enviar archivos mediante interfaz gráfica.

## Proceso

1. Seleccionar archivo.
2. Leer contenido binario.
3. Serializar mediante `pickle`.
4. Enviar al servidor.
5. Reenviar al destinatario.

---

# 📁 Límite de Archivos

El sistema restringe archivos mayores a:

```text
50 MB
```

para evitar saturación de red.

---

# 📤 Envío de Archivo

## Broadcast

Archivo enviado a todos:

```text
[Archivo enviado a todos]
```

---

## Privado

Archivo enviado a un usuario específico:

```text
@Pedro
```

---

# 📥 Recepción de Archivos

Cuando un cliente recibe un archivo:

- aparece notificación en el chat
- se abre ventana para guardar

## Ejemplo

```text
[Archivo recibido de Juan] documento.pdf
```

---

# 👥 Lista de Usuarios

## WHOISIN

Permite visualizar usuarios conectados.

## Ejemplo

```text
1) Juan since 2026-05-09
2) Pedro since 2026-05-09
```

---

# 🚫 Control de Usuarios Duplicados

El servidor valida nombres repetidos.

## Si el usuario existe

El cliente recibe:

```text
USERNAME_TAKEN
```

y la conexión es rechazada.

---

# 🧠 Lógica del Servidor

## Funciones principales

### ✔ Broadcast

Envía mensajes a todos los clientes.

---

### ✔ Mensajes privados

Envía mensajes a un único usuario.

---

### ✔ Transferencia de archivos

Reenvía archivos binarios.

---

### ✔ Gestión de clientes

- conexión
- desconexión
- lista de usuarios

---

# 🧠 Lógica del Cliente

## Funciones principales

### ✔ Conexión al servidor

---

### ✔ Recepción asíncrona

Mediante hilo listener.

---

### ✔ Envío de mensajes

---

### ✔ Envío de archivos

---

### ✔ Descarga de archivos

---

# 🔄 Flujo de Comunicación

## Mensaje Público

```text
Cliente
   ↓
Servidor
   ↓
Broadcast
   ↓
Clientes
```

---

## Mensaje Privado

```text
Cliente
   ↓
Servidor
   ↓
Usuario específico
```

---

## Transferencia de Archivo

```text
Cliente
   ↓
Servidor
   ↓
Reenvío binario
   ↓
Cliente receptor
```

---

# 📦 Serialización

Se utiliza:

```python
pickle.dumps()
pickle.loads()
```

para enviar:

- objetos
- mensajes
- archivos binarios

---

# ⚠️ Consideraciones Técnicas

## TCP es un stream

Por ello se implementó:

```python
struct.pack(">I", len(data))
```

para manejar longitud de paquetes.

---

# ⚠️ Limitaciones del Sistema

## ❌ Uso de pickle

Puede ser inseguro en producción.

---

## ❌ Sin cifrado

No se utiliza SSL/TLS.

---

## ❌ Sin persistencia

Los mensajes no se almacenan.

---

# 🚀 Mejoras Futuras

- Base de datos
- Historial de mensajes
- Cifrado SSL/TLS
- JSON en lugar de pickle
- AsyncIO
- Salas de chat
- Emojis
- Videollamadas
- Transferencia fragmentada de archivos
- Autenticación real

---

# 📚 Conceptos de Sistemas Distribuidos Aplicados

✅ Arquitectura Cliente-Servidor  
✅ TCP/IP  
✅ Comunicación distribuida  
✅ Multithreading  
✅ Sockets  
✅ Broadcast  
✅ Mensajes privados  
✅ Serialización  
✅ Transferencia binaria  
✅ Concurrencia  
✅ Sincronización  
✅ Comunicación asíncrona  

---

# 👨‍🎓 Conclusión

El proyecto implementa un sistema de chat distribuido robusto utilizando Python y sockets TCP, incorporando:

- concurrencia mediante hilos
- interfaz gráfica
- mensajes públicos y privados
- transferencia de archivos
- validación de usuarios
- protocolo seguro de paquetes

La aplicación demuestra conceptos fundamentales de:

- Sistemas Distribuidos
- Redes
- Comunicación Cliente-Servidor
- Concurrencia
- Transferencia de datos binarios
- Programación de sockets
- Interfaces gráficas en Python