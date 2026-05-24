# Laboratorio 06: REST vs. RESTful — Diseño e Implementación de Servicios Distribuidos

Este repositorio contiene la implementación de la Guía de Laboratorio Nro. 06 para la asignatura de **Sistemas Distribuidos**. El objetivo es comprender las diferencias entre REST y RESTful, y aplicarlas diseñando e implementando una API funcional con arquitectura en capas usando Java + Spring Boot.

---

## 📋 Información Básica

| Campo | Detalle |
|-------|---------|
| **Institución** | Universidad Nacional de San Agustín (UNSA) |
| **Facultad** | Ingeniería de Producción y Servicios |
| **Escuela** | Ingeniería de Sistemas |
| **Semestre** | 2026A |
| **Docente** | Mg. Maribel Molina Barriga |
| **Tipo** | Grupal |

---

## 👥 Integrantes — Grupo N

- Mamani Anahua Victor Narciso
- Maldonado Vilca Victor Gonzalo
- Larico Rodriguez Bryan Larico
- Quispe Madariaga Jeferson Jofre
- Ramirez Ccahuana, Max Edu

---

## 🚀 Contenido del Proyecto

### Ejercicio: API RESTful de Biblioteca

Implementación de una API completa para gestionar libros, siguiendo los principios RESTful: recursos nombrados correctamente, verbos HTTP semánticos, respuestas uniformes con códigos de estado apropiados y arquitectura sin estado.

**Tecnologías usadas:**
- `Java 17` + `Spring Boot 3.2`
- `Spring Data JPA` + Base de datos `H2` (en memoria)
- `Lombok` para reducir código repetitivo
- `Bean Validation` para validaciones automáticas
- `HTML5 + Fetch API` como cliente web

---

## 🗂️ Estructura del Proyecto

```
Ejercicio01/
│
├── pom.xml                                          ← Dependencias Maven
├── cliente.html                                     ← Cliente web (abrir en navegador)
│
└── src/
    └── main/
        ├── java/com/biblioteca/
        │   ├── BibliotecaApiApplication.java        ← Punto de entrada + datos iniciales
        │   │
        │   ├── model/
        │   │   └── Libro.java                       ← Entidad / Tabla en BD
        │   │
        │   ├── dto/
        │   │   ├── LibroDTO.java                    ← Objeto de transferencia de datos
        │   │   └── ApiResponse.java                 ← Envuelve todas las respuestas
        │   │
        │   ├── repository/
        │   │   └── LibroRepository.java             ← Acceso a datos (JPA)
        │   │
        │   ├── service/
        │   │   └── LibroService.java                ← Lógica de negocio
        │   │
        │   ├── controller/
        │   │   └── LibroController.java             ← Endpoints REST
        │   │
        │   └── exception/
        │       ├── LibroNotFoundException.java      ← Error 404
        │       ├── IsbnDuplicadoException.java      ← Error 409
        │       └── GlobalExceptionHandler.java      ← Manejo global de errores
        │
        └── resources/
            └── application.properties               ← Configuración del servidor y BD
```

---

## 🧱 Arquitectura en Capas

El proyecto implementa el patrón de **arquitectura en capas**, donde cada capa tiene una responsabilidad específica y se comunica solo con la capa inmediata:

```
  ┌─────────────────────────────────────┐
  │         Cliente (HTML / Postman)    │  ← Hace peticiones HTTP
  └──────────────────┬──────────────────┘
                     │ HTTP Request
  ┌──────────────────▼──────────────────┐
  │         CONTROLLER                  │  ← Recibe la petición, delega al Service
  │         LibroController.java        │
  └──────────────────┬──────────────────┘
                     │
  ┌──────────────────▼──────────────────┐
  │         SERVICE                     │  ← Lógica de negocio y validaciones
  │         LibroService.java           │
  └──────────────────┬──────────────────┘
                     │
  ┌──────────────────▼──────────────────┐
  │         REPOSITORY                  │  ← Consultas a la base de datos (JPA)
  │         LibroRepository.java        │
  └──────────────────┬──────────────────┘
                     │
  ┌──────────────────▼──────────────────┐
  │         BASE DE DATOS H2            │  ← Almacenamiento en memoria RAM
  └─────────────────────────────────────┘
```

---

## 🌐 Endpoints de la API

| Método | URL | Descripción | Código Esperado |
|--------|-----|-------------|-----------------|
| `GET`    | `/api/libros`                      | Listar todos los libros       | `200 OK`        |
| `GET`    | `/api/libros/{id}`                 | Buscar libro por ID           | `200 OK`        |
| `GET`    | `/api/libros/isbn/{isbn}`          | Buscar por ISBN               | `200 OK`        |
| `GET`    | `/api/libros/buscar?q=termino`     | Buscar por título o autor     | `200 OK`        |
| `GET`    | `/api/libros/genero/{genero}`      | Filtrar por género            | `200 OK`        |
| `GET`    | `/api/libros/estado/{estado}`      | Filtrar por estado            | `200 OK`        |
| `GET`    | `/api/libros/estadisticas`         | Ver estadísticas generales    | `200 OK`        |
| `POST`   | `/api/libros`                      | Registrar nuevo libro         | `201 Created`   |
| `PUT`    | `/api/libros/{id}`                 | Actualizar libro completo     | `200 OK`        |
| `PATCH`  | `/api/libros/{id}/stock?cantidad=` | Actualizar solo el stock      | `200 OK`        |
| `DELETE` | `/api/libros/{id}`                 | Eliminar libro                | `200 OK`        |

---

## ⚙️ Requisitos Previos

Verifica que tengas instalado lo siguiente antes de ejecutar:

| Herramienta | Versión mínima | Cómo verificar |
|-------------|---------------|----------------|
| Java JDK | 17 o superior | `java -version` |
| Apache Maven | 3.8 o superior | `mvn -version` |
| Postman | cualquier versión | — |
| Navegador web | Chrome / Firefox | — |

---

## 🛠️ Instrucciones de Ejecución

### Paso 1 — Ubicar el proyecto

Coloca la carpeta `Ejercicio01/` en tu máquina. Asegúrate de que la estructura de carpetas sea la mostrada arriba y que el archivo `pom.xml` esté en la raíz.

### Paso 2 — Abrir una terminal en la carpeta raíz

### Paso 3 — Compilar el proyecto

```bash
mvn clean package -DskipTests
```

La primera vez descargará dependencias (~1–2 minutos). Verás al final:

```
[INFO] BUILD SUCCESS
```

### Paso 4 — Ejecutar el servidor

```bash
mvn spring-boot:run
```

Cuando el servidor esté listo, la consola mostrará:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅  Biblioteca API iniciada correctamente
  🌐  URL:     http://localhost:8080/api/libros
  🗄️  Base de datos H2: http://localhost:8080/h2-console
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

> El servidor carga automáticamente **5 libros de ejemplo** al iniciar.

### Paso 5 — Abrir el cliente web

Abre el archivo `cliente.html` directamente en tu navegador (doble clic). La interfaz se conecta automáticamente al backend en `localhost:8080`.

### Paso 6 (Opcional) — Explorar la base de datos H2

1. Abre en el navegador: `http://localhost:8080/h2-console`
2. Completa los campos:
   - **JDBC URL:** `jdbc:h2:mem:bibliotecadb`
   - **User Name:** `sa`
   - **Password:** *(dejar vacío)*
3. Clic en **Connect** y ejecuta:

```sql
SELECT * FROM LIBROS;
```

---

## 🧪 Pruebas con Postman

### Listar todos los libros
```
GET http://localhost:8080/api/libros
```

### Buscar por ID
```
GET http://localhost:8080/api/libros/1
```

### Buscar por título o autor
```
GET http://localhost:8080/api/libros/buscar?q=Clean
```

### Registrar nuevo libro
```
POST http://localhost:8080/api/libros
Content-Type: application/json
```
```json
{
  "titulo": "El Señor de los Anillos",
  "autor": "J.R.R. Tolkien",
  "isbn": "978-0544003415",
  "genero": "Fantasía",
  "anioPublicacion": 1954,
  "stock": 3,
  "precio": 29.99,
  "estado": "DISPONIBLE"
}
```

### Actualizar libro completo
```
PUT http://localhost:8080/api/libros/1
Content-Type: application/json
```
```json
{
  "titulo": "Clean Code (Edición Actualizada)",
  "autor": "Robert C. Martin",
  "isbn": "978-0132350884",
  "genero": "Programación",
  "anioPublicacion": 2020,
  "stock": 10,
  "precio": 59.99,
  "estado": "DISPONIBLE"
}
```

### Actualizar solo el stock
```
PATCH http://localhost:8080/api/libros/1/stock?cantidad=20
```

### Eliminar libro
```
DELETE http://localhost:8080/api/libros/3
```

### Ver estadísticas
```
GET http://localhost:8080/api/libros/estadisticas
```

---

## 📦 Formato de Respuesta

Todos los endpoints devuelven el mismo formato JSON uniforme:

```json
{
  "exito": true,
  "mensaje": "Libro registrado exitosamente",
  "datos": {
    "id": 6,
    "titulo": "El Señor de los Anillos",
    "autor": "J.R.R. Tolkien",
    "isbn": "978-0544003415",
    "genero": "Fantasía",
    "anioPublicacion": 1954,
    "stock": 3,
    "precio": 29.99,
    "estado": "DISPONIBLE",
    "fechaRegistro": "2026-05-24"
  },
  "timestamp": "2026-05-24T10:30:00",
  "totalRegistros": 0
}
```

---

## ❌ Errores Comunes y Soluciones

| Error | Causa probable | Solución |
|-------|---------------|----------|
| `Port 8080 already in use` | Otro proceso usa el puerto | Ejecutar con: `mvn spring-boot:run -Dspring-boot.run.arguments=--server.port=9090` |
| `java: command not found` | JDK no instalado o no en PATH | Instalar JDK 17+ y configurar `JAVA_HOME` |
| `BUILD FAILURE` al compilar | Error de sintaxis en el código | Revisar el mensaje de error en la consola |
| Cliente HTML no conecta | Backend no está corriendo | Verificar que el Paso 4 esté activo |
| `409 Conflict` al hacer POST | ISBN ya existe en la BD | Usar un ISBN diferente |
| `404 Not Found` al buscar | El ID no existe | Verificar con `GET /api/libros` primero |

---

## 💡 REST vs RESTful — Diferencia Clave

Esta API demuestra la diferencia en la práctica:

| Criterio | No RESTful ❌ | RESTful ✅ (este proyecto) |
|----------|-------------|--------------------------|
| Nombrado de rutas | `GET /getLibros` | `GET /api/libros` |
| Crear recurso | `POST /crearLibro` | `POST /api/libros` |
| Eliminar recurso | `GET /eliminarLibro?id=3` | `DELETE /api/libros/3` |
| Respuesta de error | HTML o texto plano | JSON uniforme con código HTTP correcto |
| Actualización parcial | Solo PUT completo | PATCH para cambios específicos (`/stock`) |