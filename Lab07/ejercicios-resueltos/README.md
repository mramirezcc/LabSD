# Servicio SOAP de Suma - Calculadora

## Descripción
Ejemplo de un servicio web SOAP en Java que expone un método `sumar(int a, int b)` 
y un cliente que lo consume. Proyecto Maven con manejo automático de dependencias.

## Estructura del proyecto
```
ejercicios-resueltos/
├── pom.xml                          # Configuración Maven y dependencias
├── README.md
└── src/main/java/calculadora/
    ├── ICalculadora.java            # Interfaz del servicio (contrato WSDL)
    ├── CalculadoraSOAP.java         # Implementación del servicio
    ├── Publicador.java              # Publica el servicio en localhost:8080
    └── ClienteSOAP.java             # Cliente que consume el servicio
```

## Requisitos
- **Java 17** (o superior)
- **Maven 3.8+**

## Cómo Ejecutar

### 1. Compilar
```bash
mvn compile
```

### 2. Iniciar el servicio (Terminal 1)
```bash
mvn exec:java -Dexec.mainClass="calculadora.Publicador"
```
Verás:
```
Servicio SOAP activo en http://localhost:8080/calculadora
WSDL disponible en http://localhost:8080/calculadora?wsdl
```

### 3. Verificar el WSDL
Abre en el navegador: http://localhost:8080/calculadora?wsdl

### 4. Ejecutar el cliente (Terminal 2)
```bash
mvn exec:java -Dexec.mainClass="calculadora.ClienteSOAP"
```
Verás:
```
Resultado de sumar(10, 20): 30
```

### 5. Detener el servicio
Presiona `Ctrl+C` en la Terminal 1.

## Notas
- El Publicador debe estar corriendo antes de ejecutar el Cliente.
- Maven descarga las dependencias JAX-WS automáticamente la primera vez.
- En Java 8 las librerías JAX-WS venían incluidas en el JDK; en Java 11+ se requieren como dependencias externas.
