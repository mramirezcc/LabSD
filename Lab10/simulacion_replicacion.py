"""
SISTEMAS DISTRIBUIDOS - LABORATORIO 10
Replicación de Datos en Sistemas Distribuidos
Caso Empresarial: FedEx Perú

Simulación de arquitectura de replicación distribuida con 4 centros:
- Lima (Nodo Principal / Primary)
- Bogotá, Santiago, Ciudad de México (Réplicas Secundarias)

Autor: Equipo de Laboratorio
Fecha: Junio 2026
"""

import threading
import time
import random
import uuid
import sys
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
import json


# ============================================================
# CONFIGURACIÓN GLOBAL
# ============================================================

class ReplicationMode(Enum):
    SYNCHRONOUS = "SINCRONA"
    ASYNCHRONOUS = "ASINCRONA"


class NodeStatus(Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DEGRADED = "DEGRADED"


# ============================================================
# MODELOS DE DATOS
# ============================================================

@dataclass
class Producto:
    id: str
    nombre: str
    categoria: str
    cantidad: int
    unidad: str
    temperatura_min: float
    temperatura_max: float
    fecha_actualizacion: str = ""


@dataclass
class Pedido:
    id: str
    cliente: str
    producto_id: str
    cantidad: int
    origen: str
    destino: str
    estado: str  # PENDIENTE, EN_TRANSITO, ENTREGADO
    fecha_creacion: str = ""
    fecha_actualizacion: str = ""


@dataclass
class Temperatura:
    sede: str
    valor: float
    humedad: float
    timestamp: str = ""


@dataclass
class Envio:
    id: str
    pedido_id: str
    vehiculo_id: str
    origen: str
    destino: str
    estado: str  # EN_ORIGEN, EN_RUTA, EN_DESTINO, ENTREGADO
    ultima_actualizacion: str = ""


@dataclass
class Vehiculo:
    id: str
    placa: str
    tipo: str
    ubicacion_actual: Dict[str, float] = field(default_factory=lambda: {"lat": 0.0, "lon": 0.0})
    estado: str = "DISPONIBLE"
    ultima_actualizacion: str = ""


# ============================================================
# NODO DEL SISTEMA DISTRIBUIDO
# ============================================================

class Nodo:
    """Representa un centro de distribución en el sistema distribuido."""

    def __init__(self, sede_id: str, ciudad: str, pais: str, es_primario: bool = False):
        self.sede_id = sede_id
        self.ciudad = ciudad
        self.pais = pais
        self.es_primario = es_primario
        self.status = NodeStatus.ONLINE
        self.lock = threading.RLock()

        # Datos críticos del centro de distribución
        self.inventarios: Dict[str, Producto] = {}
        self.pedidos: Dict[str, Pedido] = {}
        self.temperaturas: List[Temperatura] = []
        self.envios: Dict[str, Envio] = {}
        self.vehiculos: Dict[str, Vehiculo] = {}

        # Log de operaciones para replicación
        self.log_operaciones: List[Dict] = []
        self.ultima_sincronizacion: Optional[datetime] = None
        self.version_datos: int = 0

    def registrar_operacion(self, operacion: str, datos: Dict):
        """Registra una operación en el log para replicación."""
        entrada = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(),
            "operacion": operacion,
            "datos": datos,
            "nodo_origen": self.sede_id,
            "version": self.version_datos + 1
        }
        self.log_operaciones.append(entrada)
        self.version_datos += 1
        return entrada

    def actualizar_inventario(self, producto: Producto):
        with self.lock:
            producto.fecha_actualizacion = datetime.now().isoformat()
            self.inventarios[producto.id] = producto
            self.registrar_operacion("UPDATE_INVENTARIO", asdict(producto))

    def crear_pedido(self, pedido: Pedido):
        with self.lock:
            pedido.fecha_creacion = datetime.now().isoformat()
            pedido.fecha_actualizacion = pedido.fecha_creacion
            self.pedidos[pedido.id] = pedido
            self.registrar_operacion("CREATE_PEDIDO", asdict(pedido))

    def actualizar_pedido(self, pedido_id: str, estado: str):
        with self.lock:
            if pedido_id in self.pedidos:
                self.pedidos[pedido_id].estado = estado
                self.pedidos[pedido_id].fecha_actualizacion = datetime.now().isoformat()
                self.registrar_operacion("UPDATE_PEDIDO", {
                    "id": pedido_id, "estado": estado,
                    "fecha": self.pedidos[pedido_id].fecha_actualizacion
                })

    def registrar_temperatura(self, temp: Temperatura):
        with self.lock:
            temp.timestamp = datetime.now().isoformat()
            self.temperaturas.append(temp)
            self.registrar_operacion("REGISTRAR_TEMPERATURA", asdict(temp))

    def actualizar_envio(self, envio: Envio):
        with self.lock:
            envio.ultima_actualizacion = datetime.now().isoformat()
            self.envios[envio.id] = envio
            self.registrar_operacion("UPDATE_ENVIO", asdict(envio))

    def actualizar_ubicacion_vehiculo(self, vehiculo: Vehiculo):
        with self.lock:
            vehiculo.ultima_actualizacion = datetime.now().isoformat()
            self.vehiculos[vehiculo.id] = vehiculo
            self.registrar_operacion("UPDATE_VEHICULO", asdict(vehiculo))

    def aplicar_operacion(self, entrada: Dict):
        """Aplica una operación recibida desde otro nodo."""
        with self.lock:
            op = entrada["operacion"]
            datos = entrada["datos"]

            if op == "UPDATE_INVENTARIO":
                p = Producto(**datos)
                self.inventarios[p.id] = p
            elif op == "CREATE_PEDIDO":
                p = Pedido(**datos)
                self.pedidos[p.id] = p
            elif op == "UPDATE_PEDIDO":
                if datos["id"] in self.pedidos:
                    self.pedidos[datos["id"]].estado = datos["estado"]
                    self.pedidos[datos["id"]].fecha_actualizacion = datos["fecha"]
            elif op == "REGISTRAR_TEMPERATURA":
                t = Temperatura(**datos)
                self.temperaturas.append(t)
            elif op == "UPDATE_ENVIO":
                e = Envio(**datos)
                self.envios[e.id] = e
            elif op == "UPDATE_VEHICULO":
                v = Vehiculo(**datos)
                self.vehiculos[v.id] = v

            if entrada["version"] > self.version_datos:
                self.version_datos = entrada["version"]
                self.log_operaciones.append(entrada)

    def obtener_estado(self) -> Dict:
        """Retorna un resumen del estado actual del nodo."""
        return {
            "sede_id": self.sede_id,
            "ciudad": self.ciudad,
            "pais": self.pais,
            "es_primario": self.es_primario,
            "status": self.status.value,
            "inventarios_count": len(self.inventarios),
            "pedidos_count": len(self.pedidos),
            "temperaturas_count": len(self.temperaturas),
            "envios_count": len(self.envios),
            "vehiculos_count": len(self.vehiculos),
            "version_datos": self.version_datos,
            "log_ops_count": len(self.log_operaciones)
        }


# ============================================================
# GESTOR DE REPLICACIÓN
# ============================================================

class GestorReplicacion:
    """Gestiona la replicación de datos entre nodos del sistema distribuido."""

    def __init__(self, nodos: Dict[str, Nodo], nodo_primario_id: str = "LIM"):
        self.nodos = nodos
        self.nodo_primario_id = nodo_primario_id
        self.modo: ReplicationMode = ReplicationMode.SYNCHRONOUS
        self.historial_eventos: List[Dict] = []
        self._fallo_activo = False
        self._nodo_fallback_id: Optional[str] = None

    def registrar_evento(self, tipo: str, mensaje: str):
        evento = {
            "timestamp": datetime.now().isoformat(),
            "tipo": tipo,
            "mensaje": mensaje
        }
        self.historial_eventos.append(evento)

    def replicacion_sincrona(self, nodo_origen: Nodo, entrada: Dict) -> bool:
        """
        Replicación síncrona: Espera confirmación de todas las réplicas
        antes de retornar éxito.
        """
        replicas = [n for nid, n in self.nodos.items()
                    if nid != nodo_origen.sede_id and n.status == NodeStatus.ONLINE]

        if not replicas:
            self.registrar_evento("WARN",
                f"No hay réplicas disponibles para replicación síncrona desde {nodo_origen.sede_id}")
            return False

        exitos = []
        for replica in replicas:
            try:
                time.sleep(0.1)  # Simula latencia de red
                replica.aplicar_operacion(entrada)
                exitos.append(replica.sede_id)
            except Exception as e:
                self.registrar_evento("ERROR",
                    f"Fallo replicación síncrona a {replica.sede_id}: {e}")

        exito = len(exitos) == len(replicas)
        self.registrar_evento(
            "REPLICA_SYNC" if exito else "REPLICA_SYNC_FAIL",
            f"Replicación síncrona desde {nodo_origen.sede_id}: "
            f"{'EXITO' if exito else 'FALLO PARCIAL'} - Réplicas: {exitos}"
        )
        return exito

    def replicacion_asincrona(self, nodo_origen: Nodo, entrada: Dict):
        """
        Replicación asíncrona: Confirma inmediatamente y replica en segundo plano.
        """
        replicas = [n for nid, n in self.nodos.items()
                    if nid != nodo_origen.sede_id and n.status == NodeStatus.ONLINE]

        def replicar_a_nodo(replica: Nodo):
            time.sleep(random.uniform(0.2, 0.8))  # Simula latencia variable
            try:
                replica.aplicar_operacion(entrada)
                self.registrar_evento("REPLICA_ASYNC",
                    f"Replicación asíncrona exitosa a {replica.sede_id}")
            except Exception as e:
                self.registrar_evento("ERROR",
                    f"Fallo replicación asíncrona a {replica.sede_id}: {e}")

        for replica in replicas:
            t = threading.Thread(target=replicar_a_nodo, args=(replica,), daemon=True)
            t.start()

        self.registrar_evento("REPLICA_ASYNC_QUEUED",
            f"Replicación asíncrona encolada desde {nodo_origen.sede_id} a {len(replicas)} réplicas")

    def replicar_operacion(self, nodo_origen: Nodo, entrada: Dict):
        """Replica según el modo configurado."""
        if self.modo == ReplicationMode.SYNCHRONOUS:
            return self.replicacion_sincrona(nodo_origen, entrada)
        else:
            self.replicacion_asincrona(nodo_origen, entrada)
            return True

    # ============================================================
    # SIMULACIÓN DE FALLOS Y RECUPERACIÓN
    # ============================================================

    def simular_caida_nodo(self, nodo_id: str):
        """Simula la caída de un nodo."""
        if nodo_id in self.nodos:
            self.nodos[nodo_id].status = NodeStatus.OFFLINE
            self.registrar_evento("FAILURE",
                f"!!! NODO {nodo_id} ({self.nodos[nodo_id].ciudad}) HA CAÍDO !!!")

            # Si cae el primario, activar failover
            if nodo_id == self.nodo_primario_id:
                self._fallo_activo = True
                self._ejecutar_failover()

    def _ejecutar_failover(self):
        """Ejecuta failover cuando el nodo primario falla."""
        self.registrar_evento("FAILOVER",
            "Iniciando proceso de failover automático...")

        candidatos = [(nid, n) for nid, n in self.nodos.items()
                      if nid != self.nodo_primario_id and n.status == NodeStatus.ONLINE]

        if not candidatos:
            self.registrar_evento("FAILOVER_FAIL",
                "No hay nodos disponibles para failover")
            return

        # Seleccionar el nodo con la versión de datos más reciente
        mejor_candidato = max(candidatos, key=lambda x: x[1].version_datos)
        self._nodo_fallback_id = mejor_candidato[0]
        mejor_candidato[1].es_primario = True

        self.registrar_evento("FAILOVER_SUCCESS",
            f"FAILOVER: {mejor_candidato[1].ciudad} ({mejor_candidato[1].sede_id}) "
            f"asume como nuevo nodo primario. Version datos: {mejor_candidato[1].version_datos}")

    def recuperar_nodo(self, nodo_id: str):
        """Simula la recuperacion de un nodo caido."""
        if nodo_id in self.nodos:
            nodo = self.nodos[nodo_id]
            nodo.status = NodeStatus.ONLINE
            self.registrar_evento("RECOVERY",
                f"Nodo {nodo_id} ({nodo.ciudad}) recuperado y en linea")

            if nodo_id == self.nodo_primario_id and self._nodo_fallback_id:
                # Primero sincronizar datos desde el primario temporal
                self.registrar_evento("SYNC",
                    f"Sincronizando {nodo.ciudad} con datos del primario temporal "
                    f"{self.nodos[self._nodo_fallback_id].ciudad}...")
                time.sleep(0.3)
                primario_temp = self.nodos[self._nodo_fallback_id]
                nodo.inventarios = dict(primario_temp.inventarios)
                nodo.pedidos = dict(primario_temp.pedidos)
                nodo.temperaturas = list(primario_temp.temperaturas)
                nodo.envios = dict(primario_temp.envios)
                nodo.vehiculos = dict(primario_temp.vehiculos)
                nodo.version_datos = primario_temp.version_datos

                # Luego restaurar primario original
                nodo.es_primario = True
                self.nodos[self._nodo_fallback_id].es_primario = False
                self.registrar_evento("RESTORE",
                    f"Primario original {nodo.ciudad} restaurado. "
                    f"{self.nodos[self._nodo_fallback_id].ciudad} vuelve a replica. "
                    f"Version sincronizada: {nodo.version_datos}")
                self._fallo_activo = False
                self._nodo_fallback_id = None

    def sincronizar_nodo_recuperado(self, nodo_id: str):
        """Sincroniza un nodo recuperado con los datos más recientes."""
        if nodo_id not in self.nodos:
            return

        nodo = self.nodos[nodo_id]
        nodo_primario = self.nodos.get(
            self._nodo_fallback_id if self._fallo_activo else self.nodo_primario_id
        )

        if not nodo_primario:
            return

        self.registrar_evento("SYNC",
            f"Sincronizando {nodo.ciudad} con datos del primario {nodo_primario.ciudad}...")

        time.sleep(0.5)  # Simula sincronización

        nodo.inventarios = dict(nodo_primario.inventarios)
        nodo.pedidos = dict(nodo_primario.pedidos)
        nodo.temperaturas = list(nodo_primario.temperaturas)
        nodo.envios = dict(nodo_primario.envios)
        nodo.vehiculos = dict(nodo_primario.vehiculos)
        nodo.version_datos = nodo_primario.version_datos

        self.registrar_evento("SYNC_COMPLETE",
            f"Sincronización completa de {nodo.ciudad}. Version: {nodo.version_datos}")

    def obtener_datos_perdidos_estimados(self, nodo_id: str) -> int:
        """Estima cuántas operaciones se habrían perdido con replicación asíncrona."""
        if nodo_id not in self.nodos:
            return 0
        nodo = self.nodos[nodo_id]
        return max(0, nodo.version_datos - sum(
            n.version_datos for nid, n in self.nodos.items()
            if nid != nodo_id and n.status == NodeStatus.ONLINE
        ) // max(1, len([n for nid, n in self.nodos.items()
                         if nid != nodo_id and n.status == NodeStatus.ONLINE])))


# ============================================================
# INICIALIZACIÓN DEL SISTEMA
# ============================================================

def inicializar_datos_prueba(nodos: Dict[str, Nodo]):
    """Carga datos de prueba en los nodos del sistema."""
    productos = [
        Producto("PROD-001", "Mango fresco", "Frutas", 500, "kg", 8.0, 12.0),
        Producto("PROD-002", "Palta Hass", "Verduras", 300, "kg", 4.0, 8.0),
        Producto("PROD-003", "Salmón fresco", "Pescados", 200, "kg", 0.0, 4.0),
        Producto("PROD-004", "Lácteos premium", "Lácteos", 450, "L", 2.0, 6.0),
        Producto("PROD-005", "Flores de corte", "Flores", 1000, "unidades", 2.0, 10.0),
    ]

    for nodo in nodos.values():
        for p in productos:
            nodo.inventarios[p.id] = Producto(**asdict(p))

    for nodo in nodos.values():
        for i in range(5):
            t = Temperatura(
                sede=nodo.ciudad,
                valor=round(random.uniform(0, 15), 1),
                humedad=round(random.uniform(40, 80), 1),
                timestamp=datetime.now().isoformat()
            )
            nodo.temperaturas.append(t)

    origen = nodos["LIM"]
    for i in range(3):
        pedido = Pedido(
            id=f"PED-{i+1:03d}",
            cliente=f"Cliente {chr(65+i)}",
            producto_id=productos[i].id,
            cantidad=random.randint(5, 30),
            origen="Lima",
            destino=random.choice(["Bogotá", "Santiago", "CDMX"]),
            estado="PENDIENTE",
            fecha_creacion=datetime.now().isoformat()
        )
        for nodo in nodos.values():
            nodo.pedidos[pedido.id] = Pedido(**asdict(pedido))

    vehiculos_data = [
        ("VEH-001", "ABC-123", "Refrigerado", {"lat": -12.0464, "lon": -77.0428}),
        ("VEH-002", "DEF-456", "Refrigerado", {"lat": 4.7110, "lon": -74.0721}),
        ("VEH-003", "GHI-789", "Refrigerado", {"lat": -33.4489, "lon": -70.6693}),
        ("VEH-004", "JKL-012", "Refrigerado", {"lat": 19.4326, "lon": -99.1332}),
    ]
    for vdata in vehiculos_data:
        v = Vehiculo(
            id=vdata[0], placa=vdata[1], tipo=vdata[2],
            ubicacion_actual=vdata[3], estado="DISPONIBLE",
            ultima_actualizacion=datetime.now().isoformat()
        )
        for nodo in nodos.values():
            nodo.vehiculos[v.id] = Vehiculo(**asdict(v))

    for nodo in nodos.values():
        nodo.version_datos = 5


# ============================================================
# VISUALIZACIÓN Y REPORTES
# ============================================================

SEPARADOR = "=" * 70
SEPARADOR_DOBLE = "=" * 70
LINEA = "-" * 70


def imprimir_encabezado(titulo: str):
    print(f"\n{SEPARADOR_DOBLE}")
    print(f"  {titulo}")
    print(SEPARADOR_DOBLE)


def imprimir_seccion(titulo: str):
    print(f"\n{LINEA}")
    print(f"  {titulo}")
    print(LINEA)


def imprimir_estado_nodos(nodos: Dict[str, Nodo]):
    print(f"\n{'Sede':<8} {'Ciudad':<22} {'Rol':<12} {'Status':<12} {'Inv':<6} {'Ped':<6} {'Tmp':<6} {'Env':<6} {'Veh':<6} {'Ver':<6}")
    print("-" * 100)
    for nid, n in nodos.items():
        rol = "PRIMARIO" if n.es_primario else "REPLICA"
        status_icon = "ONLINE" if n.status == NodeStatus.ONLINE else "OFFLINE"
        print(f"{nid:<8} {n.ciudad:<22} {rol:<12} {status_icon:<12} "
              f"{len(n.inventarios):<6} {len(n.pedidos):<6} {len(n.temperaturas):<6} "
              f"{len(n.envios):<6} {len(n.vehiculos):<6} {n.version_datos:<6}")


def imprimir_historial_eventos(gestor: GestorReplicacion, limite: int = 20):
    eventos = gestor.historial_eventos[-limite:]
    print(f"\n  Últimos {len(eventos)} eventos:")
    for e in eventos:
        tag = f"[{e['tipo']}]"
        print(f"  {tag:<25} {e['mensaje']}")


def imprimir_comparacion_consistencia(nodos: Dict[str, Nodo]):
    """Compara los datos entre nodos para verificar consistencia."""
    print(f"\n{'Sede':<8} {'Inv OK':<8} {'Ped OK':<8} {'Tmp OK':<8} {'Env OK':<8} {'Veh OK':<8}")
    print("-" * 55)

    ref = list(nodos.values())[0]
    for nid, n in nodos.items():
        inv_ok = "SI" if len(n.inventarios) == len(ref.inventarios) else "NO"
        ped_ok = "SI" if len(n.pedidos) == len(ref.pedidos) else "NO"
        tmp_ok = "SI" if len(n.temperaturas) == len(ref.temperaturas) else "NO"
        env_ok = "SI" if len(n.envios) == len(ref.envios) else "NO"
        veh_ok = "SI" if len(n.vehiculos) == len(ref.vehiculos) else "NO"
        print(f"{nid:<8} {inv_ok:<8} {ped_ok:<8} {tmp_ok:<8} {env_ok:<8} {veh_ok:<8}")


# ============================================================
# SIMULACIONES DE LAS ACTIVIDADES
# ============================================================

def actividad_2_demostracion(nodos: Dict[str, Nodo], gestor: GestorReplicacion):
    """Demostración de la arquitectura diseñada."""
    imprimir_encabezado("ACTIVIDAD 2: DEMOSTRACIÓN DE ARQUITECTURA DISTRIBUIDA")

    print("""
  ARQUITECTURA: MAESTRO-REPLICA (PRIMARY-REPLICA) CON FAILOVER AUTOMATICO

                          +------------------+
                          |     CLIENTES     |
                          |  (Web / Movil)   |
                          +--------+---------+
                                   |
                          +--------+---------+
                          |   BALANCEADOR    |
                          |    DE CARGA      |
                          +--------+---------+
                                   |
              +--------------------+--------------------+
              |                    |                    |
    +---------+---------+ +-------+-------+ +---------+---------+
    |   NODO PRIMARIO   | |   REPLICA 1   | |   REPLICA 2       |
    |   LIMA - PERU     | |   BOGOTA      | |   SANTIAGO        |
    |   (Escritura +    | |   (Lectura)   | |   (Lectura)       |
    |    Lectura)       | |               | |                   |
    +---------+---------+ +-------+-------+ +---------+---------+
              |                    |                    |
              |     +--------------+--------------+     |
              |     |              |              |     |
              |     |   +----------+----------+   |     |
              |     |   |   REPLICA 3         |   |     |
              |     |   |   CDMX - MEXICO     |   |     |
              |     |   |   (Lectura)         |   |     |
              |     |   +---------------------+   |     |
              |     |                              |     |
              +-----+------------------------------+-----+
                    |                              |
                    +-------- REPLICACION ---------+
                           (Sincrona/Asincrona)
    """)

    imprimir_estado_nodos(nodos)
    print("\n  Justificación de la arquitectura:")
    print("  1. Maestro-Réplica: Un solo nodo de escritura evita conflictos de datos.")
    print("  2. Geográficamente distribuida: Reduce latencia para clientes en cada región.")
    print("  3. Réplicas de solo lectura: Balancean la carga de consultas.")
    print("  4. Failover automático: Si Lima falla, el nodo con datos más recientes asume.")


def actividad_3_demostracion(nodos: Dict[str, Nodo], gestor: GestorReplicacion):
    """Demostración de los tipos de replicación por tipo de dato."""
    imprimir_encabezado("ACTIVIDAD 3: SELECCIÓN DEL TIPO DE REPLICACIÓN POR DATO")

    estrategias = [
        ("Inventarios", "SÍNCRONA",
         "CRÍTICO: Si hay inconsistencia se pueden vender productos sin stock real. "
         "Se requiere consistencia fuerte para evitar sobreventa de perecibles."),
        ("Seguimiento de Envíos", "ASÍNCRONA",
         "ALTA FRECUENCIA: Las ubicaciones se actualizan cada pocos segundos. "
         "La replicación asíncrona evita latencia excesiva. Consistencia eventual aceptable."),
        ("Historial de Pedidos", "ASÍNCRONA",
         "CONSULTAS FRECUENTES: Los clientes consultan historial constantemente. "
         "La replicación asíncrona permite balanceo de carga en lecturas."),
        ("Reportes Ejecutivos", "SÍNCRONA + ASÍNCRONA (HÍBRIDA)",
         "Los reportes diarios usan síncrona para exactitud; los dashboards en tiempo real "
         "usan asíncrona para velocidad.")
    ]

    print(f"\n  {'Dato':<25} {'Estrategia':<22} {'Justificación'}")
    print(f"  {'-'*25} {'-'*22} {'-'*50}")
    for nombre, estrategia, justificacion in estrategias:
        print(f"  {nombre:<25} {estrategia:<22} {justificacion}")

    print("\n  Resumen de decisiones según el teorema CAP:")
    print("  - Inventarios        -> CP (Consistencia + Tolerancia a Particion)")
    print("  - Seguimiento Envios -> AP (Disponibilidad + Tolerancia a Particion)")
    print("  - Historial Pedidos  -> AP (Disponibilidad + Tolerancia a Particion)")
    print("  - Reportes Ejecutivos -> CP para reportes, AP para dashboards")


def actividad_4_demostracion(nodos: Dict[str, Nodo], gestor: GestorReplicacion):
    """Simulación completa de fallo del nodo primario."""
    imprimir_encabezado("ACTIVIDAD 4: SIMULACIÓN DE FALLO DEL CENTRO PRINCIPAL (LIMA)")

    # ---- FASE 1: Estado normal ----
    imprimir_seccion("FASE 1: OPERACIÓN NORMAL - Todos los nodos en línea")
    imprimir_estado_nodos(nodos)

    gestor.modo = ReplicationMode.ASYNCHRONOUS

    nodo_lima = nodos["LIM"]
    print("\n  Realizando operaciones en Lima (primario)...")
    for i in range(3):
        pedido = Pedido(
            id=f"PED-NEW-{i+1}",
            cliente=f"Cliente Emergencia {i+1}",
            producto_id="PROD-001",
            cantidad=random.randint(10, 50),
            origen="Lima",
            destino="Bogotá",
            estado="PENDIENTE",
            fecha_creacion=datetime.now().isoformat()
        )
        nodo_lima.crear_pedido(pedido)
        entrada = nodo_lima.log_operaciones[-1]
        gestor.replicacion_asincrona(nodo_lima, entrada)
        time.sleep(0.3)
    print("  Operaciones realizadas. Replicación asíncrona en proceso...")
    time.sleep(1.0)

    imprimir_estado_nodos(nodos)
    imprimir_comparacion_consistencia(nodos)

    # ---- FASE 2: Caída del primario ----
    imprimir_seccion("FASE 2: CAÍDA DEL NODO PRIMARIO LIMA (20 minutos simulados)")
    gestor.simular_caida_nodo("LIM")
    time.sleep(0.5)

    imprimir_estado_nodos(nodos)

    nodo_nuevo_primario = None
    for nid, n in nodos.items():
        if n.es_primario and n.status == NodeStatus.ONLINE:
            nodo_nuevo_primario = n
            break

    if nodo_nuevo_primario:
        print(f"\n  >>> {nodo_nuevo_primario.ciudad} ({nodo_nuevo_primario.sede_id}) "
              f"es ahora el NODO PRIMARIO <<<")

        print("\n  Continuidad operativa: Los clientes son redirigidos al nuevo primario.")
        print("  Las operaciones de escritura ahora se procesan en "
              f"{nodo_nuevo_primario.ciudad}.")

        print(f"\n  Realizando nuevas operaciones en {nodo_nuevo_primario.ciudad}...")
        for i in range(2):
            pedido = Pedido(
                id=f"PED-FAILOVER-{i+1}",
                cliente=f"Cliente Post-Fallo {i+1}",
                producto_id="PROD-002",
                cantidad=random.randint(5, 20),
                origen=nodo_nuevo_primario.ciudad,
                destino="CDMX",
                estado="PENDIENTE",
                fecha_creacion=datetime.now().isoformat()
            )
            nodo_nuevo_primario.crear_pedido(pedido)
            entrada = nodo_nuevo_primario.log_operaciones[-1]
            gestor.replicacion_asincrona(nodo_nuevo_primario, entrada)
            time.sleep(0.2)
        print("  Operaciones realizadas en el nuevo primario.")
        time.sleep(0.8)

        imprimir_estado_nodos(nodos)

        print("\n  ANÁLISIS DE PÉRDIDA DE INFORMACIÓN (Replicación Asíncrona):")
        print("  " + "-" * 60)
        print("  Las operaciones que estaban en cola de replicación desde Lima")
        print("  hacia las réplicas podrían no haberse completado antes de la caída.")
        print("  Esto significa que algunas actualizaciones de inventario, pedidos")
        print("  nuevos o cambios de estado podrían perderse si no llegaron a")
        print("  ninguna réplica antes del fallo.")
        print()
        print("  ANÁLISIS CON REPLICACIÓN SÍNCRONA:")
        print("  " + "-" * 60)
        print("  Con replicación síncrona, el sistema se habría detenido al no")
        print("  poder confirmar las escrituras en todas las réplicas. Esto")
        print("  garantiza consistencia pero sacrifica disponibilidad durante")
        print("  el fallo. El failover habría sido más rápido porque todas")
        print("  las réplicas tendrían datos idénticos.")

    # ---- FASE 3: Recuperación ----
    imprimir_seccion("FASE 3: RECUPERACIÓN DEL NODO LIMA")
    time.sleep(0.5)
    gestor.recuperar_nodo("LIM")
    time.sleep(0.3)
    gestor.sincronizar_nodo_recuperado("LIM")
    time.sleep(0.5)

    imprimir_estado_nodos(nodos)
    imprimir_comparacion_consistencia(nodos)

    print("\n  Conclusión de la simulación:")
    print("  1. El failover automático garantizó continuidad operativa.")
    print("  2. Con replicación asíncrona se pudo perder información no replicada.")
    print("  3. Con replicación síncrona se habría garantizado consistencia total.")
    print("  4. La recuperación sincronizó los datos más recientes en Lima.")


def actividad_5_demostracion():
    """Evaluación crítica: tres mejoras propuestas."""
    imprimir_encabezado("ACTIVIDAD 5: EVALUACIÓN CRÍTICA - MEJORAS PROPUESTAS")

    mejoras = [
        {
            "titulo": "1. MONITOREO DISTRIBUIDO CON HEALTH CHECKS Y ALERTAS",
            "descripcion": """
    Implementar un sistema de monitoreo continuo con:
    - Heartbeats cada 5 segundos entre nodos.
    - Health checks para CPU, memoria, disco y latencia de red.
    - Dashboard en tiempo real (Prometheus + Grafana).
    - Alertas automáticas vía Slack/Email cuando un nodo se degrada.
    - Registro de métricas de replicación: lag, throughput, errores.
    Beneficio: Detección temprana de fallos, reducción del MTTR (Mean Time To Repair)."""
        },
        {
            "titulo": "2. BALANCEADOR DE CARGA CON ENRUTAMIENTO GEOGRÁFICO",
            "descripcion": """
    Desplegar un balanceador de carga global (DNS Geo-routing + HAProxy):
    - Redirigir clientes a la réplica geográficamente más cercana para lecturas.
    - Enrutar todas las escrituras al nodo primario activo.
    - Health checks para excluir nodos caídos del pool automáticamente.
    - Rate limiting para evitar sobrecarga en el nodo primario.
    - Cache de lecturas frecuentes en CDN (Redis) para reducir carga.
    Beneficio: Menor latencia para usuarios, distribución equitativa de carga."""
        },
        {
            "titulo": "3. ESTRATEGIA HÍBRIDA DE REPLICACIÓN CON CONSENSO",
            "descripcion": """
    Combinar estrategias según criticidad del dato:
    - Datos críticos (inventario): Replicación sincrona con quórum (Raft/Paxos).
      Solo se confirma escritura si la mayoría de nodos (N/2 + 1) confirman.
    - Datos de alta frecuencia (ubicaciones): Replicación asíncrona con
      buffer de operaciones y reconciliación periódica (CRDT).
    - Datos de consulta (historial): Event Sourcing + CQRS para separar
      escrituras de lecturas.
    - Implementar patrón Circuit Breaker para aislar nodos fallidos.
    - Recuperación automática con replicación incremental (solo delta de cambios).
    Beneficio: Balance óptimo entre consistencia, disponibilidad y rendimiento."""
        }
    ]

    for m in mejoras:
        print(f"\n  {m['titulo']}")
        print(m['descripcion'])

    print(f"\n  {'='*60}")
    print("  RESUMEN DE MEJORAS TECNOLÓGICAS")
    print(f"  {'='*60}")
    print(f"  {'Mejora':<30} {'Impacto':<15} {'Tecnologías'}")
    print(f"  {'-'*30} {'-'*15} {'-'*25}")
    print(f"  {'Monitoreo Distribuido':<30} {'Alta':<15} {'Prometheus, Grafana, AlertManager'}")
    print(f"  {'Balanceo Geográfico':<30} {'Alta':<15} {'HAProxy, DNS Geo, Redis Cache'}")
    print(f"  {'Replicación Híbrida':<30} {'Crítica':<15} {'Raft, CRDT, CQRS, Circuit Breaker'}")


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():
    """Ejecuta la simulación completa del sistema distribuido."""

    print("""
+======================================================================+
|   SISTEMAS DISTRIBUIDOS - LABORATORIO 10                            |
|   REPLICACION DE DATOS EN SISTEMAS DISTRIBUIDOS                     |
|   Caso: FedEx Peru - Transporte de Productos Perecibles             |
|   Simulacion de Arquitectura de Replicacion Distribuida             |
+======================================================================+
    """)

    # ---- Inicialización del sistema ----
    imprimir_encabezado("INICIALIZACIÓN DEL SISTEMA DISTRIBUIDO")

    nodos = {
        "LIM": Nodo("LIM", "Lima", "Perú", es_primario=True),
        "BOG": Nodo("BOG", "Bogotá", "Colombia", es_primario=False),
        "STG": Nodo("STG", "Santiago", "Chile", es_primario=False),
        "CDMX": Nodo("CDMX", "Ciudad de México", "México", es_primario=False),
    }

    gestor = GestorReplicacion(nodos, nodo_primario_id="LIM")

    inicializar_datos_prueba(nodos)
    imprimir_estado_nodos(nodos)

    print("\n  Sistema inicializado con 4 centros de distribución.")
    print("  Lima (LIM) configurado como nodo primario para escrituras.")
    print("  Bogotá (BOG), Santiago (STG) y CDMX configurados como réplicas de lectura.")
    print(f"  Modo de replicación predeterminado: {gestor.modo.value}")

    # ---- Ejecucion de actividades ----
    def pausa_opcional(mensaje):
        try:
            input(mensaje)
        except (EOFError, OSError):
            pass

    pausa_opcional("\n  Presione ENTER para continuar a la Actividad 2...")
    actividad_2_demostracion(nodos, gestor)

    pausa_opcional("\n  Presione ENTER para continuar a la Actividad 3...")
    actividad_3_demostracion(nodos, gestor)

    pausa_opcional("\n  Presione ENTER para continuar a la Actividad 4 (Simulacion de fallo)...")
    actividad_4_demostracion(nodos, gestor)

    pausa_opcional("\n  Presione ENTER para continuar a la Actividad 5...")
    actividad_5_demostracion()

    # ---- Resumen final ----
    imprimir_encabezado("RESUMEN FINAL DEL SISTEMA")
    imprimir_estado_nodos(nodos)
    imprimir_historial_eventos(gestor, limite=15)

    print(f"\n{'='*70}")
    print("  SIMULACIÓN COMPLETADA EXITOSAMENTE")
    print(f"{'='*70}")
    print("""
  CONCLUSIONES PRINCIPALES:
  1. La replicación geográfica garantiza alta disponibilidad y continuidad.
  2. La replicación síncrona asegura consistencia pero aumenta latencia.
  3. La replicación asíncrona es más rápida pero con riesgo de pérdida de datos.
  4. El failover automático es esencial para la continuidad del negocio.
  5. Una estrategia híbrida balancea consistencia, disponibilidad y rendimiento.
    """)

    return nodos, gestor


if __name__ == "__main__":
    main()
