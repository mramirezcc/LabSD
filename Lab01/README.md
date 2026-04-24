# Laboratorio 01: Programación Multihilo en Sistemas Distribuidos

Este repositorio contiene la implementación de la Guía de Laboratorio Nro. 01 para la asignatura de **Sistemas Distribuidos**. El objetivo es comprender y aplicar los conceptos de hilos (threads), monitores y sincronización en Java y Python.

## 📋 Información Básica
* **Institución:** Universidad Nacional de San Agustín (UNSA)
* **Facultad:** Ingeniería de Producción y Servicios
* **Escuela:** Ingeniería de Sistemas
* **Semestre:** 2026A
* **Docente:** Mg. Maribel Molina Barriga

## 👥 Integrantes - Grupo 3
* Larico Rodriguez, [Nombre]
* Maldonado Vilca, [Nombre]
* Quispe Huaman, [Nombre]
* Salas Aguilar, [Nombre]

---

## 🚀 Contenido del Proyecto

### 1. Caso de Estudio: Supermercado (Rendimiento)
Se analiza la diferencia entre un proceso secuencial y uno multihilo.
* **Clases:** `Cajera`, `Cliente`, `CajeraThread`.
* **Resultado:** La implementación multihilo permite procesar múltiples clientes en paralelo, reduciendo el tiempo total de ejecución de **26s a 15s** aproximadamente.

### 2. Caso de Estudio: Productor-Consumidor (Sincronización)
Implementación clásica del problema de comunicación entre hilos utilizando un monitor.
* **Componentes:**
    * `CubbyHole`: Actúa como el monitor sincronizado.
    * `Productor`: Genera datos (0-9) y los coloca en el monitor.
    * `Consumidor`: Recupera los datos del monitor.
* **Mecanismos:** Uso de `wait()`, `notifyAll()` y `synchronized` para evitar condiciones de carrera.

---

## 🛠️ Instrucciones de Ejecución

### Versión Java
Para compilar y ejecutar desde la terminal:
```bash
# Compilar todos los archivos
javac *.java

# Ejecutar la clase principal
java Demo