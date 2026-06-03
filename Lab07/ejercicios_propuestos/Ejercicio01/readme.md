# 🛒 Laboratorio 07: Sistemas Distribuidos - Servicios Web SOAP

Este proyecto contiene el desarrollo práctico de servicios distribuidos utilizando el protocolo SOAP (*Simple Object Access Protocol*) y la API nativa de Java **JAX-WS**. Se presentan dos soluciones corporativas con interfaces gráficas asíncronas desarrolladas en **Swing** bajo una arquitectura **Cliente-Servidor**.

---

# 📋 Contenido del Repositorio

El laboratorio está compuesto por dos sistemas independientes basados en contratos estrictos WSDL:

## Ejercicio 01: Conversor de Temperatura SOAP

Servidor que expone operaciones de conversión bidireccional de escalas termométricas (**°C ↔ °F**).

Características:

* Conversión Celsius → Fahrenheit.
* Conversión Fahrenheit → Celsius.
* Uso de SOAP mediante JAX-WS.
* Solución al problema de mapeo XML utilizando `@WebParam`.

---

## Ejercicio 02: Portal de Ventas de Productos en Línea

Sistema transaccional que simula una base de datos en memoria con control de concurrencia mediante `synchronized`.

Características:

* Manejo de estructuras complejas (`Producto` y `VentaResponse`).
* Consulta de productos mediante SOAP.
* Procesamiento de ventas.
* Generación de comprobantes únicos mediante UUID.
* Control seguro de stock.

---

# 🛠️ Prerrequisitos e Infraestructura

Antes de ejecutar cualquiera de los sistemas, asegúrese de contar con:

* Java Development Kit (JDK) 11 o superior.

  * Recomendado: JDK 17 o JDK 21.
* Apache Maven 3.8 o superior.
* Sistema Operativo:

  * Windows 10
  * Windows 11

---

# 🚀 Instrucciones de Ejecución

## 🔄 Fase Inicial: Limpieza y Compilación

Abrir una terminal en la raíz del proyecto y ejecutar:

```bash
mvn clean compile
```

---

# 🌡️ Sistema 1: Conversor de Temperatura SOAP

El servicio se publicará en el puerto **8080**.

## Levantar el Servidor

```bash
mvn exec:java
```

### URL del servicio

```text
http://localhost:8080/ConversorSOAP?wsdl
```

---

## Levantar el Cliente GUI

Abrir una segunda terminal y ejecutar:

```bash
mvn exec:java -Pcliente-gui
```

---

# 🛒 Sistema 2: Portal de Ventas en Línea

El servicio se publicará en el puerto **8085**.

## Levantar el Servidor de Ventas

```bash
mvn exec:java -Dexec.mainClass=server.PublicadorVentas
```

Deberá mostrarse:

```text
📌 Servicio SOAP publicado exitosamente en:
http://localhost:8085/VentaOnlineSOAP?wsdl
```

---

## Levantar el Cliente GUI

Abrir una segunda terminal y ejecutar:

```bash
mvn exec:java -Dexec.mainClass=consumer.ClienteVentasGUI
```

---

# 🧪 Casos de Prueba Diseñados

## Consulta de Catálogo

Ingresar alguno de los siguientes códigos:

```text
PROD01
PROD02
PROD03
```

Luego presionar **Buscar**.

El sistema obtendrá mediante SOAP:

* Nombre del producto
* Precio
* Stock disponible

---

## Procesamiento de Venta

Ingresar:

* Nombre del cliente
* Cantidad solicitada

Ejemplo:

```text
Cliente: Juan Pérez
Cantidad: 2
```

Presionar:

```text
Procesar Transacción
```

El sistema:

* Valida el stock.
* Registra la venta.
* Descuenta existencias.
* Genera un ticket:

```text
TX-XXXXXX
```

---

## Validación de Reglas de Negocio

Intentar comprar una cantidad superior al stock disponible.

Ejemplo:

```text
Stock actual: 10
Cantidad solicitada: 20
```

Resultado esperado:

```text
Transacción rechazada
Motivo: Stock insuficiente
```

La respuesta se devuelve mediante una estructura SOAP/XML.

---

# 📝 Solución de Errores Comunes

## Error: Unknown lifecycle phase

### Causa

Uso incorrecto de comillas en PowerShell.

### Solución

Ejecutar exactamente:

```bash
mvn exec:java -Dexec.mainClass=server.PublicadorVentas
```

Sin comillas adicionales.

---

## Parámetros Vacíos o arg0

### Problema

SOAP genera parámetros:

```text
arg0
arg1
```

y los datos llegan vacíos.

### Solución

Definir explícitamente:

```java
@WebParam(name = "idProducto")
```

Esto obliga a que SOAP preserve correctamente los nombres dentro del XML.

---

## Interfaz Congelada

### Problema

Las llamadas SOAP bloquean el hilo principal de Swing.

### Solución

Uso de:

```java
SwingWorker
```

para ejecutar operaciones de red en segundo plano y mantener la interfaz responsiva.

---

# 🏗️ Arquitectura Implementada

```text
+------------------+
| Cliente Swing    |
+------------------+
         |
         | SOAP/XML
         ▼
+------------------+
| Servicio SOAP    |
| (JAX-WS)         |
+------------------+
         |
         ▼
+------------------+
| Lógica Negocio   |
+------------------+
         |
         ▼
+------------------+
| Datos en Memoria |
+------------------+
```

---

# 🎯 Tecnologías Utilizadas

* Java 11+
* JAX-WS
* SOAP
* XML
* Maven
* Swing
* UUID
* Collections Framework
* Programación Concurrente (`synchronized`)

---

# ✅ Resultados Obtenidos

* Implementación exitosa de servicios SOAP con contratos WSDL.
* Comunicación Cliente-Servidor mediante XML.
* Consumo de servicios desde interfaces gráficas Swing.
* Manejo de objetos complejos serializados.
* Control seguro de concurrencia.
* Generación de comprobantes únicos.
* Validación de reglas de negocio en tiempo real.

---

# 👨‍💻 Universidad Nacional de San Agustín (UNSA)

**Escuela Profesional de Ingeniería de Sistemas**

**Curso:** Sistemas Distribuidos

**Año:** 2026
