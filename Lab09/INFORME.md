# Informe Tecnico de Calidad y Pruebas - LogiFresh S.A.

## Evaluacion Integral de Calidad para Sistema Distribuido de Distribucion de Alimentos Refrigerados

---

**Curso:** Sistemas Distribuidos  
**Universidad:** Universidad Nacional de San Agustin (UNSA)  
**Semestre:** 2026A  
**Docente:** Mg. Maribel Molina Barriga  
**Grupo:** 3  

**Integrantes:**
- Victor Narciso Mamani Anahua
- Victor Gonzalo Maldonado Vilca
- Bryan Larico Rodriguez
- Jeferson Jofre Quispe Madariaga
- Max Edu Ramirez Ccahuana

**Fecha:** 13 de Junio de 2026

---

## Tabla de Contenidos

1. [Introduccion](#1-introduccion)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Actividad 1: Identificacion de Riesgos (Matriz)](#3-actividad-1-identificacion-de-riesgos)
4. [Actividad 2: Diseno de Casos de Prueba Funcionales](#4-actividad-2-diseno-de-casos-de-prueba-funcionales)
5. [Actividad 3: Pruebas de Integracion](#5-actividad-3-pruebas-de-integracion)
6. [Actividad 4: Prueba de Rendimiento con k6](#6-actividad-4-prueba-de-rendimiento)
7. [Actividad 5: Estrategia de Mejora](#7-actividad-5-estrategia-de-mejora)
8. [Conclusiones y Recomendaciones](#8-conclusiones-y-recomendaciones)

---

## 1. Introduccion

LogiFresh S.A. es una empresa peruana especializada en la distribucion de alimentos refrigerados a supermercados nacionales. La compania ha adoptado una arquitectura de microservicios para modernizar su plataforma. Sin embargo, durante campanas de alta demanda, se han identificado problemas criticos que afectan la calidad del servicio y la satisfaccion del cliente.

### 1.1 Problemas Identificados

| # | Problema | Impacto |
|---|----------|---------|
| 1 | Pedidos registrados sin descuento aplicado | Perdida de confianza del cliente, reclamos |
| 2 | Inventario inconsistente | Ruptura de stock, sobreventa |
| 3 | Facturas duplicadas | Problemas contables, doble cobro |
| 4 | Retrasos en confirmaciones por correo | Mala experiencia de usuario |
| 5 | Lentitud > 8 segundos al registrar pedidos | Abandono de pedidos, perdida de ventas |

### 1.2 Objetivo

Realizar una evaluacion integral de calidad que identifique riesgos, ejecute pruebas funcionales, de integracion y de rendimiento, y proponga estrategias de mejora antes de la expansion nacional.

---

## 2. Arquitectura del Sistema

### 2.1 Diagrama de Microservicios

```
                    +---------------------------+
                    |     INTERFAZ GRAFICA      |
                    |        (Tkinter)          |
                    +---------------------------+
                                |
                    +---------------------------+
                    |    ORQUESTADOR (main.py)  |
                    +---------------------------+
                                |
          +-----------+---------+---------+-----------+
          |           |         |         |           |
    +--------+  +--------+ +--------+ +--------+ +-----------+
    |Pedidos |  |Invent. | |Factura.| |Transp. | |Notificac. |
    | :5001  |  | :5002  | | :5003  | | :5004  | | :5005     |
    +--------+  +--------+ +--------+ +--------+ +-----------+
          |           |         |         |           |
          +-----------+---------+---------+-----------+
                              |
                   Comunicacion HTTP/REST
```

### 2.2 Tecnologias Utilizadas

| Componente | Tecnologia |
|------------|-----------|
| Lenguaje | Python 3 |
| Framework REST | Flask |
| GUI | Tkinter |
| Comunicacion | HTTP/REST (requests) |
| Concurrencia | Threading |
| Pruebas funcionales/integracion | Python + requests |
| Pruebas de rendimiento | k6 (Grafana) |
| Control de versiones | Git/GitHub |

### 2.3 Servicios y Puertos

| Servicio | Puerto | Responsabilidad |
|----------|--------|-----------------|
| Pedidos | 5001 | Registro, consulta y cancelacion de pedidos |
| Inventario | 5002 | Gestion de stock de productos refrigerados |
| Facturacion | 5003 | Generacion de facturas automaticas |
| Transporte | 5004 | Programacion y seguimiento de entregas |
| Notificaciones | 5005 | Envio de confirmaciones por correo electronico |

### 2.4 Bugs Simulados

El sistema implementa bugs controlados para simular los problemas reportados:

| Bug | Servicio | Comportamiento |
|-----|----------|----------------|
| Inconsistencia de inventario | Inventario | Cada 5 consultas devuelve stock erroneo |
| Reduccion parcial de stock | Inventario | Cada 7 reducciones aplica cantidad incorrecta |
| Descuento no aplicado | Pedidos | Cada 4 pedidos con promocion falla el descuento |
| Lentitud > 8s | Pedidos | Cada 6 pedidos experimenta 8-12s de retraso |
| Factura duplicada | Facturacion | Cada 5 facturas genera un duplicado |
| Retraso en email | Notificaciones | Cada 4 notificaciones experimenta 3-8s de retraso |
| Retraso en transporte | Transporte | Cada 5 solicitudes no asigna conductor/vehiculo |

---

## 3. Actividad 1: Identificacion de Riesgos

### 3.1 Matriz de Riesgos de Calidad

| ID | Riesgo | Servicio Afectado | Impacto | Probabilidad | Accion de Mitigacion |
|----|--------|-------------------|---------|-------------|----------------------|
| R-01 | **Aplicacion inconsistente de descuentos:** Los codigos promocionales no se aplican en todos los pedidos debido a condiciones de carrera en la validacion | Pedidos, Facturacion | **Alto** - Perdida de confianza del cliente, reclamos, posible infraccion a normativas de proteccion al consumidor | **Alta** (25%) - Ocurre en 1 de cada 4 pedidos con promocion | Implementar validacion sincrona con bloqueo distribuido (Redis). Agregar logs de auditoria para trazabilidad. Aplicar patron SAGA para compensacion automatica |
| R-02 | **Inventario inconsistente:** El stock reportado no refleja la cantidad real disponible, provocando sobreventa o rechazo injustificado | Inventario, Pedidos | **Critico** - Ruptura de cadena de frio, productos perecibles no entregados, perdida economica | **Alta** (20%) - Ocurre en 1 de cada 5 consultas | Implementar transacciones ACID con base de datos relacional. Agregar verificacion de doble entrada. Usar patron Event Sourcing para trazabilidad de cambios de inventario |
| R-03 | **Facturas duplicadas:** Se generan multiples facturas para un mismo pedido, causando problemas contables y legales | Facturacion | **Alto** - Problemas con SUNAT, doble facturacion, auditorias fallidas | **Media** (20%) - Ocurre en 1 de cada 5 facturas | Implementar idempotencia mediante request-id unico. Agregar constraint UNIQUE en base de datos. Usar colas de mensajes con garantia exactly-once |
| R-04 | **Retraso en notificaciones:** Los correos de confirmacion llegan con demora, afectando la experiencia del cliente | Notificaciones | **Medio** - Insatisfaccion del cliente, llamadas a soporte | **Alta** (25%) - Ocurre en 1 de cada 4 envios | Implementar procesamiento asincrono con cola de mensajes (RabbitMQ). Agregar workers dedicados para envio de emails. Implementar politica de retry con backoff exponencial |
| R-05 | **Lentitud en registro de pedidos:** Tiempos de respuesta superiores a 8 segundos en alta demanda | Pedidos (orquestador) | **Alto** - Abandono de carrito, perdida de ventas, mala experiencia | **Media** (16.7%) - Ocurre en 1 de cada 6 pedidos | Implementar procesamiento asincrono: aceptar pedido inmediatamente, procesar en background. Usar Cache (Redis) para datos de inventario. Balanceo de carga con Nginx |
| R-06 | **Caida de servicio de inventario:** El servicio de inventario deja de responder durante picos de carga | Pedidos, Inventario | **Critico** - Imposibilidad de registrar nuevos pedidos | **Media** | Implementar Circuit Breaker con Hystrix/resilience4j. Configurar health checks y auto-recuperacion. Tener cache local de inventario para operaciones criticas |
| R-07 | **Retraso en asignacion de transporte:** No se asigna conductor/vehiculo en tiempo oportuno | Transporte, Pedidos | **Medio** - Retrasos en entregas, productos perecibles en riesgo | **Media** (20%) - Ocurre en 1 de cada 5 solicitudes | Implementar sistema de colas con prioridad. Monitoreo proactivo de flota disponible. Notificaciones tempranas al area de logistica |
| R-08 | **Perdida de mensajes entre servicios:** Fallos de red causan que operaciones queden incompletas | Todos | **Critico** - Inconsistencia general del sistema, datos corruptos | **Baja** | Implementar patron Outbox para garantizar publicacion de eventos. Usar colas de mensajes persistentes (Kafka). Implementar reconciliation jobs periodicos |

### 3.2 Mapa de Calor de Riesgos

```
Impacto
  ^
Critico |        R-06         R-02
        |                  R-08
  Alto  |   R-05   R-01
        |        R-03
 Medio  |   R-07   R-04
        |
  Bajo  |
        +------------------------------------> Probabilidad
           Baja    Media    Alta
```

**Interpretacion:** Los riesgos R-01, R-02 y R-03 se encuentran en la zona de mayor criticidad (Alto Impacto + Alta/Media Probabilidad), requiriendo acciones inmediatas. R-04 y R-07 estan en zona de monitoreo activo. R-06 y R-08, aunque menos probables, tienen impacto critico y requieren planes de contingencia.

---

## 4. Actividad 2: Diseno de Casos de Prueba Funcionales

### 4.1 Tabla de Casos de Prueba (Ejecutados - 10/10 PASARON)

| ID | Objetivo | Datos de Entrada | Resultado Esperado | Resultado Obtenido | Estado |
|----|----------|-----------------|-------------------|-------------------|--------|
| **CP-01** | Registro correcto de pedido | Cliente: Supermercado El Sol, P001 x5, sin promo | Pedido REGISTRADO, pedido_id no nulo, total > 0 | PED-0001, Total: S/. 22.50, Estado: REGISTRADO | **PASO** |
| **CP-02** | Pedido con inventario insuficiente (cantidad > 500) | P007 x9999 (validacion: max 500) | Error 400 por validacion | Error 400: "cantidad debe estar entre 1 y 500" | **PASO** |
| **CP-03** | Cancelacion de pedido | Crear P003 x2, luego cancelar | Pedido CANCELADO, stock devuelto | PED-0002 cancelado, stock reintegrado | **PASO** |
| **CP-04** | Aplicacion de promocion DESC10 | P001 x10 + DESC10 | Total con 10% descuento (S/. 40.50) | Total: S/. 40.50, Desc: S/. 4.50. Descuento 10% aplicado exitosamente | **PASO** |
| **CP-05** | Generacion automatica de factura | P005 x3 | factura_id asignado automaticamente | Factura FAC-CAE60CB0 generada | **PASO** |
| **CP-06** | Envio de notificacion por email | Pedido con email valido | notificacion_enviada = true | Notificacion enviada correctamente | **PASO** |
| **CP-07** | Consulta de pedido por ID | GET /pedido/PED-0001 | 200 OK con datos del pedido | Datos retornados correctamente | **PASO** |
| **CP-08** | Listado completo de inventario | GET /inventario | Lista con 10 productos | 10 productos listados | **PASO** |
| **CP-09** | Producto inexistente P999 | GET /inventario/P999 | 404 Producto no encontrado | 404 retornado correctamente | **PASO** |
| **CP-10** | Listado de facturas | GET /facturas | Lista de facturas con posibles duplicadas | 6 facturas, 1 duplicada detectada | **PASO** |

**Tasa de exito: 100% (10/10)**

### 4.2 Analisis de Resultados

**Casos que pasan consistentemente (estables):** CP-01, CP-02, CP-03, CP-07, CP-08, CP-09

**Casos con comportamiento variable (bugs simulados):**
- **CP-04 (Promociones):** Aproximadamente 25% de los pedidos no reciben descuento. Esto refleja el bug R-01.
- **CP-06 (Notificaciones):** Aproximadamente 25% de las notificaciones experimentan retraso. Refleja el bug R-04.
- **CP-10 (Facturas):** Aproximadamente 20% de facturas aparecen duplicadas. Refleja el bug R-03.

**Hallazgo critico:** Los casos CP-04 y CP-06 exponen fallos intermitentes que en produccion serian dificiles de diagnosticar sin observabilidad adecuada.

---

## 5. Actividad 3: Pruebas de Integracion

### 5.1 Flujo 1: Pedido <-> Inventario

#### Descripcion de la Interaccion

Cuando se crea un pedido, el servicio de Pedidos consulta el servicio de Inventario para:
1. Verificar disponibilidad de stock
2. Obtener precios unitarios
3. Reducir el stock despues de confirmar el pedido

#### Fallos Detectados

| Tipo de Fallo | Descripcion | Frecuencia | Impacto |
|--------------|-------------|------------|---------|
| **Inconsistencia de stock** | El inventario reporta stock erroneo (desfasado en 1-20 unidades) | 20% de consultas | Sobreventa o rechazo injustificado |
| **Reduccion parcial** | Al reducir stock, se descuenta una cantidad menor a la solicitada | ~14% de reducciones | Stock fantasma, discrepancias contables |
| **Desconexion** | Servicio de inventario no responde | Simulado | Pedido no se puede crear (error 503) |
| **Timeout** | Respuesta lenta del servicio | Bajo carga | Aumento en tiempo total del pedido |

#### Mecanismo de Recuperacion Propuesto

```
[CIRCUIT BREAKER]
    |
    v
[Pedido] --> [Intentar consultar inventario]
    |              |
    |         [Exito] --> Continuar
    |         [Fallo] --> [Retry x3 con backoff 1s, 2s, 4s]
    |                        |
    |                   [Exito] --> Continuar
    |                   [Fallo] --> [Circuit Breaker OPEN]
    |                                  |
    |                             [Usar cache local de inventario]
    |                             [Marcar pedido como "pendiente verificacion"]
    |                             [Notificar a operaciones]
```

### 5.2 Flujo 2: Pedido <-> Facturacion

#### Descripcion de la Interaccion

Al confirmar un pedido, el servicio de Pedidos solicita al servicio de Facturacion que genere una factura automatica con los datos del pedido, subtotal, descuento y total.

#### Fallos Detectados

| Tipo de Fallo | Descripcion | Frecuencia | Impacto |
|--------------|-------------|------------|---------|
| **Factura duplicada** | Se generan 2 facturas para un mismo pedido | 20% de pedidos | Problemas contables, doble facturacion |
| **Factura no generada** | El servicio de facturacion no responde | Por desconexion | Pedido sin factura, inconsistencia |
| **Datos inconsistentes** | La factura tiene montos diferentes al pedido | Bajo | Discrepancia en libros contables |

#### Mecanismo de Recuperacion Propuesto

```
[Pedido] --> [Generar request-id unico (UUID)]
    |
    v
[Facturacion] --> [Verificar si request-id ya fue procesado]
    |                    |
    |               [Ya procesado] --> [Retornar factura existente (IDEMPOTENCIA)]
    |               [Nuevo] --> [Generar factura con request-id]
    |                              |
    |                         [Exito] --> [Almacenar + Responder]
    |                         [Fallo] --> [Retry con mismo request-id]
    |
    v
[Patron OUTBOX]: Guardar evento "factura_solicitada" en BD local
    |
    v
[Publicador] --> [Enviar evento a cola de mensajes]
                     |
                [Consumidor Facturacion] --> [Procesar con garantia at-least-once]
```

### 5.3 Flujo 3: Pedido <-> Transporte

#### Descripcion de la Interaccion

Al crear un pedido, se solicita al servicio de Transporte que programe una entrega, asignando conductor y vehiculo.

#### Fallos Detectados

| Tipo de Fallo | Descripcion | Frecuencia | Impacto |
|--------------|-------------|------------|---------|
| **Retraso en asignacion** | No se asigna conductor/vehiculo inmediatamente | 20% de solicitudes | Pedido sin logistica asignada |
| **Transporte no programado** | El servicio no responde | Por desconexion | Pedido sin programacion de entrega |
| **Cancelacion no propagada** | Al cancelar pedido, el transporte no se actualiza | Bajo | Recursos de transporte reservados innecesariamente |

#### Mecanismo de Recuperacion Propuesto

```
[SAGA Pattern - Orquestacion]

Paso 1: Crear Pedido (PENDIENTE)
Paso 2: Reservar Inventario
Paso 3: Generar Factura
Paso 4: Programar Transporte
    |
[Fallo en Paso 4]
    |
    v
[Compensacion]:
    - Cancelar Factura (Paso 3)
    - Liberar Inventario (Paso 2)
    - Marcar Pedido como FALLIDO (Paso 1)
```

### 5.4 Prueba de Concurrencia

Se ejecutaron 10 pedidos simultaneos para evaluar el comportamiento bajo concurrencia.

| Metrica | Valor |
|---------|-------|
| Pedidos concurrentes | 10 |
| Exitosos | 8-10 (variable segun bugs simulados) |
| Fallidos | 0-2 |
| Tasa de exito | 80-100% |

**Observaciones:** Bajo concurrencia moderada, el sistema mantiene funcionalidad aceptable. Los fallos se deben principalmente a los bugs simulados (descuentos no aplicados, lentitud), no a condiciones de carrera fatales.

---

## 6. Actividad 4: Prueba de Rendimiento

### 6.1 Configuracion de la Prueba

| Parametro | Valor |
|-----------|-------|
| Herramienta | k6 (Grafana) |
| Usuarios virtuales | 100 |
| Duracion total | 5 minutos |
| Ramp-up | Gradual: 0 -> 20 -> 50 -> 80 -> 100 (en 2 min) |
| Carga sostenida | 2 minutos a 100 VUs |
| Ramp-down | 30 segundos a 0 |
| Escenario | Crear pedidos, consultar inventario, listar pedidos/facturas |

### 6.2 Script de Prueba (k6)

```javascript
// Configuracion clave del script
export const options = {
  vus: 100,
  duration: '5m',
  stages: [
    { duration: '30s', target: 20 },
    { duration: '30s', target: 50 },
    { duration: '30s', target: 80 },
    { duration: '30s', target: 100 },
    { duration: '2m',  target: 100 },
    { duration: '30s', target: 0 },
  ],
};
```

### 6.3 Metricas Obtenidas (Resultados Reales de Ejecucion)

| Metrica | Valor Real | Interpretacion |
|---------|-----------|----------------|
| **Iteraciones completadas** | 3,097 | Todas las iteraciones finalizaron sin interrupciones |
| **Total de requests HTTP** | 5,266 | Promedio de ~1.7 requests por iteracion |
| **Tiempo promedio de respuesta** | 1,706.89 ms | ACEPTABLE: Por debajo de 3 segundos |
| **Tiempo maximo de respuesta** | 17,047.22 ms (~17s) | CRITICO: Refleja el bug de lentitud simulado |
| **Percentil 90 (p90)** | 5,106.44 ms (~5.1s) | ALTO: 10% de usuarios > 5 segundos |
| **Percentil 95 (p95)** | 10,868.69 ms (~10.9s) | CRITICO: Umbral excedido (threshold <5s) |
| **Percentil 99 (p99)** | 15,085.10 ms (~15.1s) | INACEPTABLE: 1% de usuarios > 15 segundos |
| **Throughput (req/s)** | 18.36 req/s | MODERADO: El sistema procesa ~18 req/s con 100 VUs |
| **Pedidos exitosos** | 3,097 (100%) | Todos los pedidos se crearon sin errores |
| **Tasa de errores** | 0% | No hubo errores de conexion durante la prueba |
| **Tiempo promedio creacion pedido** | 2,899.49 ms | ACEPTABLE pero cercano al limite |
| **Tiempo maximo creacion pedido** | 17,047 ms | CRITICO: Coincide con el sleep simulado de 8-12s |
| **p95 creacion pedido** | 11,871.60 ms | ALTO: El 5% de pedidos tarda > 11 segundos |
| **Threshold cruzado** | p(95) < 5000ms | **FALLIDO**: p95=10.9s supera el umbral de 5s |

### 6.4 Comando de Ejecucion

```bash
# Requiere k6 instalado
# Windows: choco install k6  o descargar de https://k6.io
# Linux: sudo apt install k6

k6 run tests/rendimiento/k6_script.js
```

### 6.5 Interpretacion de Resultados (Basado en datos reales)

**Tiempo de respuesta:**
- El tiempo promedio (1,707ms) es aceptable y esta por debajo del umbral critico de 3 segundos para e-commerce.
- El p90 elevado (5.1s) indica que 1 de cada 10 usuarios experimenta lentitud notable.
- El p95 critico (10.9s) confirma el problema de lentitud reportado: el 5% de usuarios espera mas de 10 segundos.
- El p99 (15.1s) es inaceptable para un sistema en produccion.

**Throughput:**
- 18.36 req/s con 100 usuarios concurrentes es un rendimiento moderado. Para expansion nacional se requiere optimizar.
- Sin los sleeps simulados, el throughput seria significativamente mayor.

**Tasa de errores:**
- 0% de errores de red gracias al modo `threaded=True` en Flask.
- La primera ejecucion sin threaded fallo completamente. Esto demuestra la importancia de configurar servidores web para concurrencia.

**Cuellos de botella confirmados:**
1. Sleeps simulados cada 6 pedidos (8-12s) - responsable del p95 y p99 elevados
2. Comunicacion sincrona encadenada (4+ llamadas HTTP por pedido)
3. Retrasos simulados en Notificaciones (3-8s cada 4 notificaciones)
4. Procesamiento secuencial de la cadena Pedido->Inventario->Facturacion->Transporte->Notificaciones

---

## 7. Actividad 5: Estrategia de Mejora

### 7.1 Cinco Acciones para Mejorar la Calidad del Sistema

#### Accion 1: Automatizacion de Pruebas

| Aspecto | Propuesta |
|---------|-----------|
| **Pruebas unitarias** | Implementar pytest para cada microservicio. Cobertura minima: 80% |
| **Pruebas de integracion** | Automatizar con pytest + requests. Ejecutar en CI/CD |
| **Pruebas end-to-end** | Selenium/Playwright para flujos completos desde GUI |
| **Pruebas de contrato** | Pact para validar contratos entre servicios (Pedidos-Inventario, etc.) |
| **Ejecucion** | Integrar en GitHub Actions: ejecutar en cada PR y nightly |

```
Pipeline CI/CD:
[Push/PR] --> [Unit Tests] --> [Integration Tests] --> [Contract Tests]
                                                           |
                                                      [Pass] --> [Deploy Staging]
                                                      [Fail] --> [Notificar + Bloquear merge]
```

#### Accion 2: Observabilidad

| Componente | Herramienta | Proposito |
|-----------|-------------|-----------|
| **Logging centralizado** | ELK Stack (Elasticsearch, Logstash, Kibana) o Grafana Loki | Agregar logs de todos los servicios con trace-id correlacionado |
| **Metrics** | Prometheus + Grafana | Monitorear latencia, throughput, errores por servicio |
| **Tracing distribuido** | Jaeger o Zipkin | Trazar una solicitud a traves de todos los microservicios |
| **Alerting** | Alertmanager | Alertas por: latencia > 3s, tasa de error > 1%, servicio caido |
| **Health checks** | Endpoints /health en cada servicio | Deteccion temprana de fallos |

```
[Pedidos] --trace-id--> [Inventario] --trace-id--> [Facturacion]
    |                       |                        |
    v                       v                        v
[Jaeger Collector] <-- [Spans con trace-id correlacionado]
    |
    v
[UI: Visualizar waterfall de llamadas entre servicios]
```

#### Accion 3: Balanceo de Carga

| Componente | Propuesta |
|-----------|-----------|
| **Load Balancer** | Nginx como reverse proxy para distribuir trafico |
| **Escalado horizontal** | Multiple instancias de cada microservicio detras del balanceador |
| **Algoritmo** | Round-robin con least-connections para servicios con estado |
| **Health checks** | Nginx verifica /health cada 5s, remueve instancias no saludables |
| **Configuracion** | Docker Compose con replicas: `docker-compose up --scale pedidos=3` |

```
                       [NGINX :80]
                           |
          +----------------+----------------+
          |                |                |
    [Pedidos-1]      [Pedidos-2]      [Pedidos-3]
    :5001            :5011            :5021
          |                |                |
          +----------------+----------------+
                           |
                    [Redis Cache]
```

#### Accion 4: Circuit Breaker y Monitoreo Continuo

| Patron | Implementacion | Beneficio |
|--------|---------------|-----------|
| **Circuit Breaker** | pybreaker o resilience4j (via sidecar) | Evita llamadas en cascada a servicios fallidos |
| **Retry con backoff** | Exponencial: 1s, 2s, 4s, 8s (max 3 intentos) | Recuperacion de fallos transitorios |
| **Bulkhead** | Thread pools separados por servicio | Aisla fallos: inventario lento no afecta facturacion |
| **Timeout** | 5s maximo por llamada entre servicios | Evita bloqueos indefinidos |
| **Fallback** | Respuesta degradada (cache, default) | Sistema sigue funcionando parcialmente |

```
Estados del Circuit Breaker:

[CLOSED] --(fallos > umbral)--> [OPEN] --(timeout)--> [HALF_OPEN]
    ^                                                       |
    |                                               (exito) |
    +-------------------------------------------------------+
                           (fallo)
                               |
                           [OPEN]
```

#### Accion 5: Integracion Continua (CI/CD)

| Fase | Herramienta | Actividad |
|------|------------|-----------|
| **Code** | GitHub | Repositorio central, branching strategy (GitFlow) |
| **Build** | GitHub Actions | Instalar dependencias, verificar sintaxis |
| **Test** | GitHub Actions + pytest | Unitarias, integracion, cobertura (min 80%) |
| **Analysis** | SonarQube | Analisis estatico, code smells, vulnerabilidades |
| **Deploy** | Docker + Docker Compose | Desplegar en ambiente staging automatico |
| **Release** | Manual approval | Promover a produccion previa aprobacion |

```
Pipeline CI/CD Completo:

[Git Push] --> [GitHub Actions Trigger]
    |
    v
[1. Build] --> Instalar dependencias Python
    |
    v
[2. Lint] --> flake8, black, isort
    |
    v
[3. Unit Tests] --> pytest --cov
    |
    v
[4. Integration Tests] --> Levantar servicios, ejecutar tests/integracion.py
    |
    v
[5. SAST] --> Bandit (security), SonarQube
    |
    v
[6. Build Docker] --> docker build
    |
    v
[7. Deploy Staging] --> docker-compose up
    |
    v
[8. Smoke Tests] --> k6 con 10 VUs por 1 min
    |
    v
[9. Manual Approval] --> [Deploy Production]
```

### 7.2 Priorizacion de Acciones

| Prioridad | Accion | Justificacion |
|-----------|--------|---------------|
| **1 (Inmediata)** | Circuit Breaker + Timeout | Mitiga el riesgo de fallos en cascada y lentitud |
| **2 (Inmediata)** | Observabilidad (logs + metrics) | Sin visibilidad no se pueden diagnosticar los bugs intermitentes |
| **3 (Corto plazo)** | Balanceo de carga | Necesario para expansion nacional y picos de demanda |
| **4 (Corto plazo)** | Automatizacion de pruebas | Previene regresiones y acelera desarrollo |
| **5 (Mediano plazo)** | CI/CD completo | Estandariza el proceso de despliegue y reduce errores humanos |

---

## 8. Conclusiones y Recomendaciones

### 8.1 Conclusiones

1. **La arquitectura de microservicios es adecuada** para el negocio de LogiFresh, permitiendo escalar servicios independientemente segun la demanda. Sin embargo, la implementacion actual carece de mecanismos de resiliencia.

2. **Se identificaron 8 riesgos de calidad**, de los cuales 3 son criticos (Inventario inconsistente, Caida de servicio, Perdida de mensajes) y requieren atencion inmediata antes de la expansion nacional.

3. **Las pruebas funcionales revelaron que 6 de 10 casos pasan consistentemente**, mientras que 3 casos (promociones, notificaciones, facturas duplicadas) presentan fallos intermitentes que reflejan los bugs simulados del sistema.

4. **Las pruebas de integracion** demostraron que la comunicacion sincrona entre servicios es el principal punto de fallo, requiriendo patrones de resiliencia como Circuit Breaker, Retry y Timeout.

5. **La prueba de rendimiento con k6** proyecta que con 100 usuarios concurrentes, el sistema mantiene un rendimiento aceptable (promedio <3s), pero el p95 elevado (5-7s) y p99 critico (8-12s) indican que no esta listo para expansion nacional sin optimizaciones.

6. **La GUI desarrollada en Tkinter** proporciona una interfaz funcional para monitorear el sistema en tiempo real y facilita la demostracion de los bugs simulados.

### 8.2 Recomendaciones

1. **Implementar Circuit Breaker inmediatamente** en todas las llamadas entre servicios para evitar fallos en cascada.

2. **Migrar a procesamiento asincrono** usando colas de mensajes (RabbitMQ/Kafka) para las operaciones de notificacion, facturacion y asignacion de transporte.

3. **Agregar cache de inventario** (Redis) con TTL corto para reducir llamadas al servicio de inventario y mejorar tiempos de respuesta.

4. **Implementar idempotencia** en facturacion usando request-id unico para eliminar facturas duplicadas.

5. **Establecer un pipeline CI/CD** con pruebas automatizadas para garantizar calidad en cada despliegue.

6. **Realizar pruebas de estres adicionales** con 500+ usuarios concurrentes antes de la expansion nacional para validar la capacidad del sistema.

7. **Implementar APM (Application Performance Monitoring)** con tracing distribuido antes del go-live nacional.

### 8.3 Proximos Pasos

| Plazo | Actividad |
|-------|-----------|
| Semana 1-2 | Implementar Circuit Breaker y health checks en todos los servicios |
| Semana 2-3 | Configurar ELK + Prometheus + Grafana para observabilidad |
| Semana 3-4 | Implementar balanceo de carga con Nginx y Docker |
| Semana 4-5 | Migrar notificaciones y facturacion a procesamiento asincrono |
| Semana 5-6 | Pipeline CI/CD con GitHub Actions |
| Semana 6-7 | Pruebas de estres con 500+ usuarios |
| Semana 8 | Go/No-Go para expansion nacional |

---

## Anexos

### Anexo A: Estructura del Proyecto

```
Lab09/
├── main.py                          # Launcher principal
├── requirements.txt                 # Dependencias Python
├── INFORME.md                       # Este informe
├── services/
│   ├── __init__.py
│   ├── pedidos.py                   # Servicio de Pedidos (:5001)
│   ├── inventario.py                # Servicio de Inventario (:5002)
│   ├── facturacion.py               # Servicio de Facturacion (:5003)
│   ├── transporte.py                # Servicio de Transporte (:5004)
│   └── notificaciones.py            # Servicio de Notificaciones (:5005)
├── gui/
│   └── app.py                       # Interfaz grafica Tkinter
├── tests/
│   ├── funcionales.py               # 10 casos de prueba funcionales
│   ├── integracion.py               # Pruebas de integracion (4 flujos)
│   ├── resultados_funcionales.json  # Resultados (generado al ejecutar)
│   ├── resultados_integracion.json  # Resultados (generado al ejecutar)
│   └── rendimiento/
│       ├── k6_script.js             # Script de prueba k6
│       ├── resultados_k6.json       # Resultados (generado al ejecutar)
│       └── resultados_k6_detallado.json  # Resultados detallados
└── evidencias/                      # Capturas de pantalla (a completar)
```

### Anexo B: Comandos de Ejecucion

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Iniciar el sistema (servicios + GUI)
python main.py

# 3. Ejecutar pruebas funcionales (en otra terminal, con servicios corriendo)
python tests/funcionales.py

# 4. Ejecutar pruebas de integracion
python tests/integracion.py

# 5. Ejecutar prueba de rendimiento (requiere k6 instalado)
& "C:\Program Files\k6\k6.exe" run tests/rendimiento/k6_script.js
```

### Anexo C: Endpoints API por Servicio

#### Pedidos (:5001)
| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| POST | /pedido | Crear nuevo pedido |
| GET | /pedido/{id} | Consultar pedido |
| POST | /pedido/{id}/cancelar | Cancelar pedido |
| GET | /pedidos | Listar todos los pedidos |
| GET | /promociones | Listar promociones disponibles |

#### Inventario (:5002)
| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | /inventario | Listar todo el inventario |
| GET | /inventario/{id} | Consultar stock de producto |
| POST | /inventario/{id}/reducir | Reducir stock |
| POST | /inventario/{id}/aumentar | Aumentar stock |

#### Facturacion (:5003)
| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| POST | /factura | Generar factura |
| GET | /factura/{id} | Consultar factura |
| GET | /facturas | Listar facturas |
| GET | /facturas/duplicadas | Listar facturas duplicadas |

#### Transporte (:5004)
| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| POST | /transporte | Programar transporte |
| GET | /transporte/{id} | Consultar estado |
| PUT | /transporte/{id} | Actualizar estado |
| GET | /transportes | Listar transportes |

#### Notificaciones (:5005)
| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| POST | /notificacion | Enviar notificacion |
| GET | /notificacion/{id} | Consultar notificacion |
| GET | /notificaciones | Listar notificaciones |
| GET | /notificaciones/retrasadas | Listar notificaciones con retraso |

---

**Fin del Informe**
