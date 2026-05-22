# Calculadora Distribuida con gRPC

Implementación de una calculadora distribuida usando **gRPC** en Java. El servidor expone un servicio `Calculator` con el método `Sum`, y el cliente se conecta para enviar dos números y recibir el resultado de la suma.

## Estructura del Proyecto

```
ejercicio-resuelto/
├── pom.xml
├── README.md
└── src/main/
    ├── proto/
    │   └── calculator.proto              # Definición del servicio gRPC
    └── java/com/example/calculator/
        ├── CalculatorService.java        # Implementación del servicio (Sum)
        ├── CalculatorServer.java         # Servidor gRPC (puerto 50051)
        └── CalculatorClient.java         # Cliente gRPC
```

## Requisitos Previos

- **Java JDK 11** o superior
- **Apache Maven 3.6+**

Verificar instalación:

```bash
java -version
mvn -version
```

## Compilar el Proyecto

Desde la raíz del proyecto (`ejercicio-resuelto/`), ejecutar:

```bash
mvn clean compile
```

Este comando descarga las dependencias, genera el código Java a partir del archivo `calculator.proto` y compila todo el proyecto.

## Ejecutar

### 1. Iniciar el Servidor

En una terminal, ejecutar:

```bash
mvn exec:java -Dexec.mainClass="com.example.calculator.CalculatorServer"
```

Salida esperada:

```
Servidor gRPC iniciado en el puerto 50051...
```

### 2. Ejecutar el Cliente

En **otra terminal** (sin cerrar el servidor), ejecutar:

```bash
mvn exec:java -Dexec.mainClass="com.example.calculator.CalculatorClient"
```

Salida esperada:

```
Resultado: 12
```

El cliente envía los valores `a = 8` y `b = 4`, el servidor calcula la suma y devuelve `12`.

## Archivo Proto

El servicio se define en `src/main/proto/calculator.proto`:

```protobuf
syntax = "proto3";

service Calculator {
  rpc Sum (Request) returns (Response);
}

message Request {
  int32 a = 1;
  int32 b = 2;
}

message Response {
  int32 result = 1;
}
```

## Notas

- El servidor escucha en `localhost:50051`.
- Para detener el servidor, presionar `Ctrl + C` en la terminal donde se está ejecutando.
- El código gRPC generado se encuentra en `target/generated-sources/protobuf/` después de compilar.
