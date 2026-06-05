# Laboratorio 08: Bases de Datos Distribuidas y Transacciones 2PC

Este repositorio contiene la implementación de la Guía de Laboratorio Nro. 08 para la asignatura de **Sistemas Distribuidos**. El objetivo es comprender, aplicar y evaluar los conceptos de transacciones distribuidas, propiedades ACID y el protocolo Two-Phase Commit (2PC) utilizando entornos contenedorizados y programación en Python.

## 📋 Información Básica
* **Institución:** Universidad Nacional de San Agustín (UNSA)
* **Facultad:** Ingeniería de Producción y Servicios
* **Escuela:** Ingeniería de Sistemas
* **Semestre:** 2026A
* **Docente:** Mg. Maribel Molina Barriga

## 👥 Integrantes
* Mamani Anahua Victor Narciso
* Maldonado Vilca Victor Gonzalo
* Larico Rodriguez Bryan Larico
* Quispe Madariaga Jeferson Jofre
* Ramirez Ccahuana, Max Edu

---

## 🚀 Contenido del Proyecto

El proyecto simula la infraestructura de la cadena farmacéutica **FarmaAndes S.A.**, la cual cuenta con almacenes independientes distribuidos en nodos de red. Se analizan dos escenarios fundamentales para la consistencia de datos:

### 1. Ejercicio 1: Transferencia Exitosa (Commit Global)
Se procesa el traslado de 20 unidades de medicamentos (Paracetamol) desde la sede origen hacia la sede destino.
* **Flujo:** El Coordinador verifica el stock en origen, descuenta las unidades de Arequipa e incrementa el inventario en Lima de manera segura.
* **Resultado:** Al no presentarse fallos de comunicación, el protocolo consolida un `COMMIT` en ambos nodos de manera unánime.
    * **Stock Arequipa:** Reduce de 100 a **80**.
    * **Stock Lima:** Incrementa de 50 a **70**.

### 2. Ejercicio 2: Simulación de Fallo de Red (Rollback Global)
Se simula una pérdida crítica de conectividad con el nodo destino a mitad del proceso de transferencia.
* **Mecanismos:** Se utiliza una interrupción controlada (`raise OperationalError`) inmediatamente después de alterar el nodo origen. El Coordinador intercepta la excepción en su bloque `except`.
* **Resultado:** Para asegurar la propiedad de **Atomicidad**, el Coordinador cancela la transacción en curso enviando una orden de `ROLLBACK` al nodo origen.
    * **Impacto:** Los datos vuelven a su último estado consistente válido (**Arequipa: 80**, **Lima: 70**), evitando la pérdida o duplicación fantasma de inventario.

---
## 📁 Estructura del Proyecto

El diseño modular del laboratorio se organiza de la siguiente manera:

```text
caso1/
├── docker-compose.yml          # Configuración de los contenedores Docker (PostgreSQL)
├── python/                     # Código fuente del Coordinador Distribuido
│   ├── app.py                  # Servidor Flask e implementación del protocolo 2PC
│   └── templates/
│       └── index.html          # Interfaz gráfica (Panel de control FarmaAndes S.A.)
└── scripts_sql/                # Scripts de inicialización y restauración de las BD
    ├── arequipa_init.sql       # Creación e inserción del stock inicial para Arequipa
    └── lima_init.sql           # Creación e inserción del stock inicial para Lima

```
---
## 🛠️ Instrucciones de Ejecución

### 1. Levantar la Infraestructura (Docker)
Asegúrate de estar en la raíz del proyecto donde se encuentra el archivo `docker-compose.yml` y ejecuta:
```bash
# Construir y activar los contenedores en segundo plano
docker-compose up -d
```
### 2. Inicializar las Bases de Datos (PowerShell)

Para poblar los esquemas e insertar los registros iniciales de Paracetamol usando los scripts locales desde Windows:

```powershell
# Inicializar Nodo Arequipa (Puerto 5433)
Get-Content scripts_sql/arequipa_init.sql | docker exec -i db_arequipa psql -U postgres -d almacen_arequipa

# Inicializar Nodo Lima (Puerto 5434)
Get-Content scripts_sql/lima_init.sql | docker exec -i db_lima psql -U postgres -d almacen_lima
```

---

### 3. Ejecutar el Coordinador Distribuidor (Python + Flask)

Instala las dependencias necesarias e inicia el servidor web que actúa como middleware del protocolo 2PC:

```powershell
# Instalar dependencias del sistema
pip install flask psycopg2-binary

# Cambiar al directorio del código fuente
cd python

# Iniciar la aplicación
python app.py
```

---

### 4. Acceso al Panel de Control

Abre tu navegador web e ingresa a la siguiente dirección para interactuar con la interfaz gráfica:

```text
http://localhost:5000
```
