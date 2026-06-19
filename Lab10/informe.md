# INFORME TÉCNICO - LABORATORIO 10

## Replicación de Datos en Sistemas Distribuidos
### Caso Empresarial: FedEx Perú

---

**Asignatura:** Sistemas Distribuidos  
**Docente:** Mg. Maribel Molina Barriga  
**Semestre:** 2026-A  
**Fecha:** 19 de junio de 2026

---

## ÍNDICE

1. [Actividad 1: Identificación de Necesidades](#actividad-1-identificación-de-necesidades)
2. [Actividad 2: Diseño Arquitectónico](#actividad-2-diseño-arquitectónico)
3. [Actividad 3: Selección del Tipo de Replicación](#actividad-3-selección-del-tipo-de-replicación)
4. [Actividad 4: Simulación de un Fallo](#actividad-4-simulación-de-un-fallo)
5. [Actividad 5: Evaluación Crítica](#actividad-5-evaluación-crítica)
6. [Tabla Comparativa de Estrategias](#tabla-comparativa-de-estrategias-de-replicación)
7. [Conclusiones](#conclusiones)
8. [Bibliografía](#bibliografía)

---

## ACTIVIDAD 1: IDENTIFICACIÓN DE NECESIDADES

### 1.1 Datos Críticos del Sistema

| Categoría | Datos | Criticidad |
|-----------|-------|------------|
| Inventarios | Stock de productos perecibles, fechas de caducidad, cantidades | **Crítica** |
| Pedidos | Órdenes de clientes, estados, montos | **Crítica** |
| Temperaturas | Registros de temperatura por almacén y vehículo | **Alta** |
| Estado de Envíos | Tracking en tiempo real, ubicación actual | **Alta** |
| Ubicación de Vehículos | GPS en tiempo real de flota de transporte | **Alta** |
| Clientes | Datos de contacto, direcciones de entrega | **Media** |
| Catálogo de Productos | Lista maestra de productos transportables | **Media** |

### 1.2 Datos Susceptibles de Replicación

| Dato | Susceptibilidad | Razón |
|------|----------------|-------|
| Inventarios | **ALTA** | Requiere consistencia global para evitar sobreventa |
| Pedidos | **ALTA** | Múltiples sedes consultan el mismo pedido |
| Envíos | **ALTA** | Clientes consultan desde cualquier país |
| Vehículos | **ALTA** | Visibilidad completa de la flota regional |
| Temperaturas | **MEDIA** | Auditoría regulatoria, no requiere consistencia inmediata |
| Reportes | **MEDIA** | Pueden generarse desde réplicas de solo lectura |

### 1.3 Riesgos Actuales

| Riesgo | Probabilidad | Impacto | Consecuencia |
|--------|-------------|---------|--------------|
| Caída del servidor principal | Media | **Crítico** | Sede completa inoperativa |
| Retrasos en actualización de inventario | Alta | **Alto** | Sobreventa, pérdida de productos perecibles |
| Inconsistencia en reportes | Alta | **Alto** | Decisiones erróneas de gerencia |
| Estados distintos según sucursal | Alta | **Alto** | Pérdida de confianza del cliente |
| Latencia en consultas transfronterizas | Media | **Medio** | Mala experiencia de usuario |
| Pérdida de datos por fallo de red | Baja | **Crítico** | Información irrecuperable |

### 1.4 Beneficios Esperados de la Replicación

| Beneficio | Descripción | Impacto en el Negocio |
|-----------|-------------|----------------------|
| Alta Disponibilidad | Servicio continúa aunque falle un nodo | 99.99% uptime objetivo |
| Recuperación ante Desastres | Datos replicados en múltiples ubicaciones | RPO < 5 minutos, RTO < 15 minutos |
| Balanceo de Carga | Consultas distribuidas entre réplicas | Reducción del 60% en latencia |
| Escalabilidad Geográfica | Réplicas cercanas a cada país | Mejor experiencia para clientes regionales |
| Continuidad Operativa | Failover automático ante fallos | Cero intervención manual en fallos |
| Consistencia Global | Datos uniformes en todas las sedes | Eliminación de discrepancias en reportes |

---

## ACTIVIDAD 2: DISEÑO ARQUITECTÓNICO

### 2.1 Diagrama de Arquitectura Distribuida

```
                        ┌──────────────────────────┐
                        │        CLIENTES           │
                        │   (Web / App Móvil / API) │
                        └────────────┬─────────────┘
                                     │
                        ┌────────────┴─────────────┐
                        │  BALANCEADOR DE CARGA     │
                        │  (DNS Geo-Routing)        │
                        └────────────┬─────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
┌─────────┴──────────┐   ┌──────────┴──────────┐   ┌──────────┴──────────┐
│  NODO PRIMARIO     │   │  RÉPLICA SECUNDARIA  │   │  RÉPLICA SECUNDARIA │
│  LIMA - PERÚ       │   │  BOGOTÁ - COLOMBIA   │   │  SANTIAGO - CHILE   │
│                    │   │                      │   │                     │
│  ┌──────────────┐  │   │  ┌──────────────┐    │   │  ┌──────────────┐   │
│  │ PostgreSQL   │  │   │  │ PostgreSQL   │    │   │  │ PostgreSQL   │   │
│  │ (Escritura)  │  │   │  │ (Solo Lectura)│    │   │  │ (Solo Lectura)│  │
│  └──────────────┘  │   │  └──────────────┘    │   │  └──────────────┘   │
│  ┌──────────────┐  │   │  ┌──────────────┐    │   │  ┌──────────────┐   │
│  │ Redis Cache  │  │   │  │ Redis Cache  │    │   │  │ Redis Cache  │   │
│  └──────────────┘  │   │  └──────────────┘    │   │  └──────────────┘   │
└─────────┬──────────┘   └──────────┬──────────┘   └──────────┬──────────┘
          │                          │                          │
          │      ┌───────────────────┼───────────────────┐      │
          │      │                   │                   │      │
          │      │   ┌───────────────┴───────────────┐   │      │
          │      │   │  RÉPLICA SECUNDARIA           │   │      │
          │      │   │  CDMX - MÉXICO                │   │      │
          │      │   │  ┌──────────────┐             │   │      │
          │      │   │  │ PostgreSQL   │             │   │      │
          │      │   │  │ (Solo Lectura)│            │   │      │
          │      │   │  └──────────────┘             │   │      │
          │      │   │  ┌──────────────┐             │   │      │
          │      │   │  │ Redis Cache  │             │   │      │
          │      │   │  └──────────────┘             │   │      │
          │      │   └───────────────────────────────┘   │      │
          │      │                                       │      │
          └──────┴───────────────────────────────────────┴──────┘
                 │                                               │
                 └─────────────── FLUJO DE ──────────────────────┘
                            SINCRONIZACIÓN
                    (Síncrona: Inventarios, Pedidos)
                    (Asíncrona: Tracking, Temperaturas)
```

### 2.2 Estrategia de Recuperación ante Fallos

```
     ┌─────────────────────────────────────────────────────┐
     │          PROTOCOLO DE RECUPERACIÓN                  │
     ├─────────────────────────────────────────────────────┤
     │  1. DETECCIÓN: Heartbeat cada 5s entre nodos       │
     │  2. CONFIRMACIÓN: 3 fallos consecutivos = CAÍDA    │
     │  3. FAILOVER: Nodo con > versión datos asume        │
     │  4. REDIRECCIÓN: DNS/Proxy actualiza ruta           │
     │  5. SINCRONIZACIÓN: Nodo recuperado recibe delta    │
     │  6. RESTAURACIÓN: Primario original retoma control  │
     └─────────────────────────────────────────────────────┘
```

### 2.3 Justificación de la Arquitectura

| Criterio | Decisión | Justificación |
|----------|----------|---------------|
| **Modelo de replicación** | Maestro-Réplica (Primary-Replica) | Un solo punto de escritura evita conflictos de concurrencia en datos críticos como inventarios perecibles. Las réplicas manejan lecturas, que constituyen el 80% de las operaciones. |
| **Número de réplicas** | 3 réplicas (BOG, STG, CDMX) | Una por cada país de operación. Suficientes para tolerancia a fallos (N-1) y cercanía geográfica a clientes. |
| **Ubicación geográfica** | Distribuida en 4 países | Reduce la latencia de consultas para clientes locales. Protege contra desastres regionales. |
| **Balanceador de carga** | DNS Geo-Routing | Redirige automáticamente a la réplica más cercana. En caso de fallo, excluye nodos caídos y redirige al primario activo. |
| **Failover** | Automático | El nodo con la versión de datos más reciente asume como primario. Sin intervención manual. Tiempo de recuperación < 30 segundos. |

---

## ACTIVIDAD 3: SELECCIÓN DEL TIPO DE REPLICACIÓN

### 3.1 Análisis por Tipo de Dato

| Dato | Estrategia Seleccionada | Consistencia | Disponibilidad | Rendimiento | Justificación |
|------|------------------------|--------------|----------------|-------------|---------------|
| **Inventarios** | **Síncrona** | Consistencia fuerte | Media (depende de réplicas) | Bajo (latencia de confirmación) | Productos perecibles con stock limitado. Una inconsistencia causaría sobreventa y pérdidas económicas. Se requiere que todas las réplicas reflejen el stock exacto. |
| **Seguimiento de Envíos** | **Asíncrona** | Consistencia eventual | Alta | Alto | Actualizaciones de GPS cada 5-30 segundos. Volumen masivo de escrituras. Consistencia eventual aceptable: el cliente ve la ubicación con máximo 2-3 segundos de retraso. |
| **Historial de Pedidos** | **Asíncrona** | Consistencia eventual | Alta | Alto | Consultas frecuentes de solo lectura. Los clientes verifican estados; un retraso de pocos segundos en la réplica no afecta la operación. Permite balancear la carga de lectura. |
| **Reportes Ejecutivos** | **Híbrida (Síncrona + Asíncrona)** | Consistencia fuerte (reportes financieros) / Eventual (dashboards) | Alta | Alto | Reportes diarios y financieros requieren exactitud (síncrona). Dashboards operativos en tiempo real priorizan velocidad (asíncrona). |

### 3.2 Aplicación del Teorema CAP

| Dato | Prioridad CAP | Explicación |
|------|---------------|-------------|
| Inventarios | **CP** (Consistencia + Partición) | En caso de partición de red, se sacrifica disponibilidad para garantizar que no haya doble venta. |
| Seguimiento de Envíos | **AP** (Disponibilidad + Partición) | Es preferible mostrar una ubicación ligeramente desactualizada que denegar el servicio. |
| Historial de Pedidos | **AP** (Disponibilidad + Partición) | Similar a tracking: mejor servir datos con leve retraso que no servir. |
| Reportes Ejecutivos | **CP** (Diario) / **AP** (Dashboard) | Varía según el tipo de reporte y su criticidad para decisiones de negocio. |

---

## ACTIVIDAD 4: SIMULACIÓN DE UN FALLO

### 4.1 Escenario: Caída del Centro de Datos Principal en Lima (20 minutos)

#### a) ¿Qué nodo debería asumir el servicio?

El nodo que debería asumir el servicio es **Bogotá (BOG)**, por las siguientes razones:

1. **Proximidad geográfica**: Es la réplica más cercana a Lima, lo que minimiza la latencia para clientes de la región andina.
2. **Versión de datos más reciente**: Al ser la réplica con menor latencia de red hacia Lima, típicamente tiene los datos más actualizados.
3. **Cobertura horaria**: Comparte zona horaria similar (UTC-5), facilitando la continuidad operativa del personal.

En caso de que Bogotá no esté disponible, el algoritmo de failover selecciona el nodo con la **mayor versión de datos** (mayor número de operaciones confirmadas), que en el código de simulación corresponde a:

```
candidato = max(réplicas_disponibles, key=lambda n: n.version_datos)
```

#### b) ¿Cómo se garantizaría la continuidad operativa?

| Mecanismo | Descripción |
|-----------|-------------|
| **Detección automática** | Sistema de heartbeats entre nodos cada 5 segundos. Tras 3 fallos consecutivos (15 segundos), se confirma la caída. |
| **Failover automático** | El gestor de replicación promueve automáticamente la réplica con datos más recientes a primario. Todas las escrituras se redirigen al nuevo primario. |
| **Redirección de clientes** | El balanceador DNS actualiza las rutas para que el tráfico de escritura apunte al nuevo primario. Tiempo de propagación DNS: 30-60 segundos. |
| **Operación degradada** | Las réplicas restantes siguen sirviendo consultas de lectura sin interrupción. Solo las escrituras requieren el nuevo primario. |
| **Cola de operaciones pendientes** | Las escrituras que no alcanzaron a replicarse desde Lima quedan registradas en el log del primario caído para reconciliación posterior. |
| **Notificación** | Alertas automáticas al equipo de operaciones vía Slack/Email para intervención manual si es necesario. |

#### c) ¿Qué información podría perderse si la replicación fuera asíncrona?

Con replicación asíncrona, la información en riesgo incluye:

| Tipo de Dato | Riesgo de Pérdida | Ejemplo Concreto |
|-------------|-------------------|------------------|
| **Pedidos nuevos** | Alto | Pedidos creados en Lima en los últimos 2-3 segundos antes de la caída que no alcanzaron a transmitirse a ninguna réplica. |
| **Actualizaciones de inventario** | Alto | Decrementos de stock por ventas recientes. Las réplicas mostrarían stock inflado, permitiendo sobreventa. |
| **Cambios de estado de envíos** | Medio | Envíos marcados como "entregado" que las réplicas aún muestran como "en tránsito". |
| **Registros de temperatura** | Bajo | Lecturas de sensores de los últimos segundos. Pueden reenviarse al recuperar el nodo. |
| **Ubicaciones GPS** | Bajo | Datos de alta frecuencia que se sobrescriben constantemente. |

**Estimación cuantitativa:** En un sistema con 100 operaciones/segundo y un retraso de replicación asíncrona de 2 segundos, se podrían perder aproximadamente **200 operaciones** que estaban en el buffer de replicación no confirmadas por ninguna réplica.

#### d) ¿Cómo afectaría una replicación síncrona?

| Aspecto | Impacto |
|---------|---------|
| **Pérdida de datos** | **CERO**: Ninguna operación se confirma sin que todas las réplicas la almacenen. La consistencia es absoluta. |
| **Disponibilidad durante el fallo** | **DEGRADADA**: Si Lima cae, el sistema habría detenido nuevas escrituras porque no se puede confirmar en todas las réplicas (una está caída). Se requiere failover para reanudar. |
| **Latencia** | **MAYOR**: Cada escritura debe esperar confirmación de 3 réplicas geográficamente distantes (RTT Lima-Bogotá: ~50ms, Lima-Santiago: ~80ms, Lima-CDMX: ~100ms). Latencia total de escritura: ~100-150ms adicionales. |
| **Tiempo de failover** | **MENOR**: Como todas las réplicas están 100% sincronizadas, el failover es inmediato. Cualquier réplica tiene los datos completos. |
| **Throughput** | **MENOR**: El sistema procesa menos escrituras por segundo debido a la espera de confirmaciones. |

**Conclusión de la simulación:** La replicación asíncrona proporciona mejor rendimiento y disponibilidad durante operación normal, pero con riesgo de pérdida de datos ante fallos. La replicación síncrona garantiza consistencia absoluta a costa de mayor latencia y posibles bloqueos. La estrategia recomendada es **híbrida**: síncrona para datos críticos (inventario) y asíncrona para datos de alta frecuencia (tracking).

---

## ACTIVIDAD 5: EVALUACIÓN CRÍTICA

### Mejoras Tecnológicas para Incrementar la Resiliencia

---

### Mejora 1: Sistema de Monitoreo Distribuido con Health Checks y Alertas

**Descripción:**
Implementar un stack de monitoreo completo que permita visibilidad en tiempo real del estado de todos los nodos del sistema distribuido.

**Componentes:**
| Componente | Función | Tecnología |
|------------|---------|------------|
| Recolección de métricas | CPU, memoria, latencia, throughput de replicación | Prometheus + Node Exporter |
| Health checks | Heartbeats entre nodos cada 5 segundos | Custom health endpoint + Consul |
| Visualización | Dashboards en tiempo real del estado del clúster | Grafana |
| Alertas | Notificaciones ante degradación o caída de nodos | AlertManager → Slack/Email |
| Trazabilidad | Seguimiento de operaciones de replicación | OpenTelemetry + Jaeger |

**Beneficios:**
- Detección temprana de fallos (antes de que afecten al usuario).
- Reducción del MTTR (Mean Time To Repair) de 20 minutos a < 5 minutos.
- Visibilidad completa del lag de replicación entre nodos.
- Dashboard ejecutivo para la gerencia con KPIs de disponibilidad.

---

### Mejora 2: Balanceador de Carga Global con Enrutamiento Geográfico

**Descripción:**
Desplegar un sistema de balanceo de carga inteligente que distribuya las solicitudes según la ubicación geográfica del cliente y el estado de los nodos.

**Arquitectura:**
```
Cliente en Colombia → DNS Geo-Routing → Réplica Bogotá (menor latencia)
Cliente en Chile    → DNS Geo-Routing → Réplica Santiago
Cliente en México   → DNS Geo-Routing → Réplica CDMX
Escrituras          → DNS Geo-Routing → Nodo Primario activo (failover-aware)
```

**Componentes:**
| Componente | Función |
|------------|---------|
| DNS Geo-Routing (Route 53 / Cloud DNS) | Resolver al nodo más cercano según IP del cliente |
| HAProxy / NGINX | Balanceo local con health checks, rate limiting, circuit breaker |
| Redis Cluster | Cache distribuido de consultas frecuentes |
| CDN (CloudFront / Cloud CDN) | Cache estático de catálogo de productos y recursos web |

**Beneficios:**
- Reducción del 60% en latencia de consultas para clientes regionales.
- Distribución equitativa de carga: réplicas no saturadas.
- Rate limiting evita que un cliente malintencionado afecte al sistema.
- Circuit Breaker aísla nodos fallidos sin afectar al resto.

---

### Mejora 3: Estrategia Híbrida de Replicación con Algoritmos de Consenso

**Descripción:**
Evolucionar de un modelo simple Maestro-Réplica a una arquitectura de replicación híbrida que aplique la estrategia óptima según la criticidad y frecuencia de cada tipo de dato.

**Estrategias por tipo de dato:**

| Tipo de Dato | Estrategia | Tecnología/Patrón |
|-------------|------------|-------------------|
| **Inventarios** | Replicación sincrona con quórum (Raft) | PostgreSQL con Patroni + etcd. Escritura confirmada cuando N/2+1 nodos responden. Mayor disponibilidad que síncrona pura. |
| **Seguimiento de Envíos** | Replicación asíncrona + CRDT | Apache Kafka para streaming de eventos + CRDT (Conflict-free Replicated Data Types) para reconciliación automática sin conflictos. |
| **Historial de Pedidos** | Event Sourcing + CQRS | Separar modelo de escritura (comandos) del de lectura (consultas). Las réplicas mantienen vistas materializadas actualizadas asíncronamente. |
| **Temperaturas** | Time-series con replicación por bucket | TimescaleDB o InfluxDB con replicación por particiones temporales. |
| **Configuración** | Replicación sincrona total | etcd/Consul con Raft. Datos de configuración que cambian poco pero requieren consistencia absoluta. |

**Patrones de resiliencia adicionales:**

| Patrón | Propósito |
|--------|-----------|
| **Circuit Breaker** | Aislar nodos fallidos. Si un nodo falla 3 veces en 60s, se excluye del pool por 30s. |
| **Retry con Backoff Exponencial** | Reintentar operaciones fallidas con espera creciente (1s, 2s, 4s, 8s...) |
| **Bulkhead** | Aislar recursos por tipo de operación para que un fallo en tracking no afecte pedidos. |
| **Graceful Degradation** | Si la replicación sincrona falla, degradar temporalmente a asíncrona con alerta. |

**Beneficios:**
- Balance óptimo entre consistencia, disponibilidad y rendimiento.
- Sin punto único de fallo para escrituras (modelo multi-master con quórum).
- Reconciliación automática de datos divergentes (CRDT).
- Escalabilidad independiente de escrituras y lecturas (CQRS).

---

## TABLA COMPARATIVA DE ESTRATEGIAS DE REPLICACIÓN

### Comparación General

| Característica | Maestro-Réplica (Primary-Replica) | Multi-Master | Peer-to-Peer | Híbrida (Recomendada) |
|---------------|----------------------------------|--------------|--------------|----------------------|
| **Escrituras** | 1 nodo | Todos los nodos | Todos los nodos | Variable según dato |
| **Lecturas** | Todas las réplicas | Todas las réplicas | Todos los nodos | Todas las réplicas |
| **Consistencia** | Fuerte (síncrona) / Eventual (asíncrona) | Conflictos posibles | Eventual | Configurable por dato |
| **Disponibilidad** | Alta (failover) | Muy alta | Muy alta | Muy alta |
| **Latencia escritura** | Baja (asíncrona) / Alta (síncrona) | Media (coordinación) | Baja | Optimizada por dato |
| **Complejidad** | Baja | Alta (resolución de conflictos) | Muy alta | Alta |
| **Escalabilidad escritura** | Baja (un solo nodo) | Alta | Muy alta | Alta (quórum) |
| **Tolerancia a fallos** | Media (requiere failover) | Alta | Muy alta | Alta |
| **Costo operativo** | Bajo | Medio | Alto | Medio-Alto |
| **Casos de uso** | ERP, e-commerce, banca | Colaboración (Google Docs) | P2P file sharing | Sistemas empresariales críticos |

### Aplicación al Caso FedEx

| Requisito FedEx | Estrategia Seleccionada | Justificación |
|-----------------|------------------------|---------------|
| Inventario consistente | Síncrona con quórum (Raft) | Evita sobreventa de perecibles |
| Tracking en tiempo real | Asíncrona con CRDT | Alta frecuencia, consistencia eventual aceptable |
| Pedidos multi-país | Event Sourcing + CQRS | Separa escrituras y lecturas para escalar |
| Reportes gerenciales | Síncrona diaria + Asíncrona dashboard | Exactitud para decisiones, velocidad para monitoreo |
| Recuperación ante fallos | Failover automático | RTO < 30 segundos |
| Balanceo de carga | DNS Geo-Routing + Redis Cache | 60% reducción de latencia |

---

## CONCLUSIONES

### Conclusiones Individuales

1. **Estudiante 1:** La replicación de datos es un pilar fundamental en sistemas distribuidos empresariales. El caso FedEx demuestra que sin replicación, un solo punto de fallo puede paralizar operaciones completas en múltiples países. La elección entre replicación síncrona y asíncrona no es binaria: depende del tipo de dato y su criticidad para el negocio.

2. **Estudiante 2:** El teorema CAP deja claro que no se pueden tener consistencia, disponibilidad y tolerancia a particiones simultáneamente. La clave está en elegir qué sacrificar según el contexto. Para inventarios de productos perecibles, la consistencia es innegociable; para tracking GPS, la disponibilidad prevalece.

3. **Estudiante 3:** La simulación implementada en Python demuestra que el failover automático es técnicamente viable y reduce drásticamente el tiempo de inactividad. Sin embargo, la replicación asíncrona conlleva riesgos reales de pérdida de datos que deben mitigarse con estrategias híbridas y monitoreo constante.

4. **Estudiante 4:** Las mejoras propuestas (monitoreo, balanceo geográfico y replicación híbrida) transforman un sistema básico de replicación en una arquitectura empresarial resiliente. La inversión en estas tecnologías se justifica plenamente por la reducción de pérdidas operativas y la mejora en la experiencia del cliente.

5. **Estudiante 5:** La implementación práctica con herramientas como PostgreSQL, Redis, Prometheus y patrones como CQRS y Circuit Breaker demuestra que los conceptos teóricos de sistemas distribuidos tienen aplicación directa en soluciones empresariales reales. La correcta selección de estrategias de replicación impacta directamente en los KPIs del negocio.

### Conclusiones Grupales

1. **La replicación geográfica es indispensable** para empresas multinacionales como FedEx. Garantiza continuidad operativa ante fallos regionales y mejora la experiencia del cliente al reducir latencia.

2. **No existe una estrategia única óptima.** La solución más efectiva es un enfoque híbrido que aplique replicación síncrona para datos críticos (inventario) y asíncrona para datos de alta frecuencia (tracking), balanceando consistencia, disponibilidad y rendimiento según la naturaleza de cada dato.

3. **El failover automático es crítico.** La simulación demostró que un sistema sin failover automático puede permanecer inoperativo por tiempos inaceptables. La automatización reduce el RTO de horas a segundos.

4. **El monitoreo es tan importante como la replicación misma.** Sin visibilidad del estado de los nodos y del lag de replicación, los operadores actúan a ciegas. Herramientas como Prometheus y Grafana son inversiones necesarias, no opcionales.

5. **La resiliencia requiere múltiples capas:** replicación de datos, balanceo de carga, circuit breakers, reintentos con backoff y degradación graceful. Cada capa agrega protección adicional contra diferentes tipos de fallos.

---

## BIBLIOGRAFÍA

### Formato APA (7.a edición)

[1] M. Kleppmann, *Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems*. Sebastopol, CA, USA: O'Reilly Media, 2017.

[2] G. Coulouris, J. Dollimore, T. Kindberg, y G. Blair, *Distributed Systems: Concepts and Design*, 5.a ed. Boston, MA, USA: Addison-Wesley, 2012.

[3] A. S. Tanenbaum y M. Van Steen, *Distributed Systems: Principles and Paradigms*, 3.a ed. Pearson, 2017.

[4] E. Brewer, "CAP Twelve Years Later: How the 'Rules' Have Changed," *Computer*, vol. 45, no. 2, pp. 23–29, feb. 2012, doi: 10.1109/MC.2012.37.

[5] D. Abadi, "Consistency Tradeoffs in Modern Distributed Database System Design," *Computer*, vol. 45, no. 2, pp. 37–42, feb. 2012, doi: 10.1109/MC.2012.33.

[6] D. Ongaro y J. Ousterhout, "In Search of an Understandable Consensus Algorithm," en *Proc. USENIX ATC '14*, Philadelphia, PA, 2014, pp. 305–319.

[7] W. Vogels, "Eventually Consistent," *Communications of the ACM*, vol. 52, no. 1, pp. 40–44, ene. 2009, doi: 10.1145/1435417.1435432.

[8] M. Shapiro, N. Preguiça, C. Baquero, y M. Zawirski, "Conflict-Free Replicated Data Types," en *Proc. SSS 2011*, Granada, España, 2011, pp. 386–400, doi: 10.1007/978-3-642-24550-3_29.

[9] PostgreSQL Global Development Group, "PostgreSQL 16 Documentation: Chapter 27. High Availability, Load Balancing, and Replication," 2023. [En línea]. Disponible: https://www.postgresql.org/docs/16/high-availability.html.

[10] Apache Software Foundation, "Apache Kafka Documentation: Replication," 2023. [En línea]. Disponible: https://kafka.apache.org/documentation/#replication.

[11] Redis Ltd., "Redis Documentation: Replication," 2023. [En línea]. Disponible: https://redis.io/docs/management/replication/.

[12] Prometheus Authors, "Prometheus Documentation: Alerting Rules," 2023. [En línea]. Disponible: https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/.

[13] M. Nygard, *Release It! Design and Deploy Production-Ready Software*, 2.a ed. Raleigh, NC, USA: Pragmatic Bookshelf, 2018.

[14] B. Burns, B. Grant, D. Oppenheimer, E. Brewer, y J. Wilkes, "Borg, Omega, and Kubernetes: Lessons Learned from Three Container-Management Systems over a Decade," *ACM Queue*, vol. 14, no. 1, pp. 70–93, ene. 2016.

[15] Netflix Technology Blog, "Active-Active for Multi-Regional Resiliency," Netflix TechBlog, 2020. [En línea]. Disponible: https://netflixtechblog.com/active-active-for-multi-regional-resiliency-c47719f6685b.

---

*Documento generado como parte del Laboratorio 10 de Sistemas Distribuidos - UNSA 2026-A*
