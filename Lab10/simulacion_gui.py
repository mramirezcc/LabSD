"""
SISTEMAS DISTRIBUIDOS - LABORATORIO 10
Interfaz Grafica de Simulacion de Replicacion Distribuida
Caso Empresarial: FedEx Peru

Ejecutar: python simulacion_gui.py
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import random
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from enum import Enum


# ============================================================
# MODELOS Y LOGICA DE NEGOCIO
# ============================================================

class ReplicationMode(Enum):
    SYNCHRONOUS = "SINCRONA"
    ASYNCHRONOUS = "ASINCRONA"

class NodeStatus(Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DEGRADED = "DEGRADED"

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
    estado: str
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
    estado: str
    ultima_actualizacion: str = ""

@dataclass
class Vehiculo:
    id: str
    placa: str
    tipo: str
    ubicacion_actual: Dict = field(default_factory=lambda: {"lat": 0.0, "lon": 0.0})
    estado: str = "DISPONIBLE"
    ultima_actualizacion: str = ""


class Nodo:
    def __init__(self, sede_id: str, ciudad: str, pais: str, es_primario: bool = False):
        self.sede_id = sede_id
        self.ciudad = ciudad
        self.pais = pais
        self.es_primario = es_primario
        self.status = NodeStatus.ONLINE
        self.lock = threading.RLock()
        self.inventarios: Dict[str, Producto] = {}
        self.pedidos: Dict[str, Pedido] = {}
        self.temperaturas: List[Temperatura] = []
        self.envios: Dict[str, Envio] = {}
        self.vehiculos: Dict[str, Vehiculo] = {}
        self.log_operaciones: List[Dict] = []
        self.ultima_sincronizacion = None
        self.version_datos: int = 0
        self.operaciones_pendientes: int = 0

    def registrar_operacion(self, operacion: str, datos: Dict) -> Dict:
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

    def crear_envio(self, envio: Envio):
        with self.lock:
            envio.ultima_actualizacion = datetime.now().isoformat()
            self.envios[envio.id] = envio
            self.registrar_operacion("CREATE_ENVIO", asdict(envio))

    def actualizar_envio(self, envio_id: str, estado: str):
        with self.lock:
            if envio_id in self.envios:
                self.envios[envio_id].estado = estado
                self.envios[envio_id].ultima_actualizacion = datetime.now().isoformat()
                self.registrar_operacion("UPDATE_ENVIO", {
                    "id": envio_id, "estado": estado,
                    "fecha": self.envios[envio_id].ultima_actualizacion
                })

    def actualizar_ubicacion_vehiculo(self, vehiculo: Vehiculo):
        with self.lock:
            vehiculo.ultima_actualizacion = datetime.now().isoformat()
            self.vehiculos[vehiculo.id] = vehiculo
            self.registrar_operacion("UPDATE_VEHICULO", asdict(vehiculo))

    def aplicar_operacion(self, entrada: Dict):
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
                self.temperaturas.append(Temperatura(**datos))
            elif op == "CREATE_ENVIO":
                e = Envio(**datos)
                self.envios[e.id] = e
            elif op == "UPDATE_ENVIO":
                if datos["id"] in self.envios:
                    self.envios[datos["id"]].estado = datos["estado"]
                    self.envios[datos["id"]].ultima_actualizacion = datos["fecha"]
            elif op == "UPDATE_VEHICULO":
                v = Vehiculo(**datos)
                self.vehiculos[v.id] = v
            if entrada["version"] > self.version_datos:
                self.version_datos = entrada["version"]
                self.log_operaciones.append(entrada)


class GestorReplicacion:
    def __init__(self, nodos: Dict[str, Nodo], nodo_primario_id: str = "LIM"):
        self.nodos = nodos
        self.nodo_primario_id = nodo_primario_id
        self.modo: ReplicationMode = ReplicationMode.ASYNCHRONOUS
        self.historial_eventos: List[Dict] = []
        self._fallo_activo = False
        self._nodo_fallback_id: Optional[str] = None
        self.callback_log = None
        self.callback_ui = None  # callback para refrescar UI despues de operaciones

    def registrar_evento(self, tipo: str, mensaje: str):
        evento = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "tipo": tipo,
            "mensaje": mensaje
        }
        self.historial_eventos.append(evento)
        if self.callback_log:
            self.callback_log(evento)

    def replicacion_sincrona(self, nodo_origen: Nodo, entrada: Dict) -> bool:
        replicas = [n for nid, n in self.nodos.items()
                    if nid != nodo_origen.sede_id and n.status == NodeStatus.ONLINE]
        if not replicas:
            self.registrar_evento("WARN", f"Sin replicas disponibles desde {nodo_origen.sede_id}")
            return False
        exitos = []
        for replica in replicas:
            try:
                time.sleep(0.08)
                replica.aplicar_operacion(entrada)
                exitos.append(replica.sede_id)
            except Exception as e:
                self.registrar_evento("ERROR", f"Fallo replica sincrona -> {replica.sede_id}: {e}")
        exito = len(exitos) == len(replicas)
        self.registrar_evento(
            "REPLICA_SYNC" if exito else "REPLICA_SYNC_FAIL",
            f"Replica sincrona {nodo_origen.sede_id}: {'OK' if exito else 'FALLO PARCIAL'} -> {exitos}")
        if self.callback_ui:
            self.callback_ui()
        return exito

    def replicacion_asincrona(self, nodo_origen: Nodo, entrada: Dict):
        replicas = [n for nid, n in self.nodos.items()
                    if nid != nodo_origen.sede_id and n.status == NodeStatus.ONLINE]

        nodo_origen.operaciones_pendientes += len(replicas)

        def replicar_a_nodo(replica: Nodo):
            time.sleep(random.uniform(0.15, 0.6))
            try:
                replica.aplicar_operacion(entrada)
                nodo_origen.operaciones_pendientes -= 1
                self.registrar_evento("REPLICA_ASYNC", f"OK -> {replica.sede_id}")
                if self.callback_ui:
                    self.callback_ui()
            except Exception as e:
                nodo_origen.operaciones_pendientes -= 1
                self.registrar_evento("ERROR", f"Fallo -> {replica.sede_id}: {e}")

        for replica in replicas:
            t = threading.Thread(target=replicar_a_nodo, args=(replica,), daemon=True)
            t.start()
        self.registrar_evento("REPLICA_ASYNC_QUEUED",
            f"Encolado {nodo_origen.sede_id} -> {len(replicas)} replicas")

    def replicar_operacion(self, nodo_origen: Nodo, entrada: Dict):
        if self.modo == ReplicationMode.SYNCHRONOUS:
            return self.replicacion_sincrona(nodo_origen, entrada)
        else:
            self.replicacion_asincrona(nodo_origen, entrada)
            return True

    def obtener_primario_activo(self) -> Optional[Nodo]:
        if self._fallo_activo and self._nodo_fallback_id:
            return self.nodos.get(self._nodo_fallback_id)
        return self.nodos.get(self.nodo_primario_id)

    def simular_caida_nodo(self, nodo_id: str):
        if nodo_id not in self.nodos:
            return
        nodo = self.nodos[nodo_id]
        if nodo.status == NodeStatus.OFFLINE:
            return

        nodo.status = NodeStatus.OFFLINE
        self.registrar_evento("FAILURE",
            f"!!! CAIDA: {nodo_id} ({nodo.ciudad}) !!!")

        if nodo_id == self.nodo_primario_id:
            self._fallo_activo = True
            self._ejecutar_failover()
        if self.callback_ui:
            self.callback_ui()

    def _ejecutar_failover(self):
        self.registrar_evento("FAILOVER", "Iniciando failover automatico...")
        candidatos = [(nid, n) for nid, n in self.nodos.items()
                      if nid != self.nodo_primario_id and n.status == NodeStatus.ONLINE]
        if not candidatos:
            self.registrar_evento("FAILOVER_FAIL", "No hay nodos disponibles para failover")
            return
        mejor = max(candidatos, key=lambda x: x[1].version_datos)
        self._nodo_fallback_id = mejor[0]
        mejor[1].es_primario = True
        self.registrar_evento("FAILOVER_SUCCESS",
            f"FAILOVER: {mejor[1].ciudad} ({mejor[1].sede_id}) asume como PRIMARIO [v{mejor[1].version_datos}]")

    def recuperar_nodo(self, nodo_id: str):
        if nodo_id not in self.nodos:
            return
        nodo = self.nodos[nodo_id]
        if nodo.status == NodeStatus.ONLINE:
            return

        nodo.status = NodeStatus.ONLINE
        self.registrar_evento("RECOVERY", f"{nodo_id} ({nodo.ciudad}) vuelve a estar en linea")

        # Si se recupera el primario original cuando hay un fallback activo
        if nodo_id == self.nodo_primario_id and self._nodo_fallback_id:
            primario_temp = self.nodos[self._nodo_fallback_id]
            self.registrar_evento("SYNC",
                f"Sincronizando {nodo.ciudad} desde {primario_temp.ciudad} [v{primario_temp.version_datos}]...")
            time.sleep(0.2)
            nodo.inventarios = dict(primario_temp.inventarios)
            nodo.pedidos = dict(primario_temp.pedidos)
            nodo.temperaturas = list(primario_temp.temperaturas)
            nodo.envios = dict(primario_temp.envios)
            nodo.vehiculos = dict(primario_temp.vehiculos)
            nodo.version_datos = primario_temp.version_datos
            nodo.operaciones_pendientes = 0
            nodo.es_primario = True
            self.nodos[self._nodo_fallback_id].es_primario = False
            self.registrar_evento("RESTORE",
                f"Primario {nodo.ciudad} RESTAURADO. {primario_temp.ciudad} vuelve a replica. [v{nodo.version_datos}]")
            self._fallo_activo = False
            self._nodo_fallback_id = None

        # Si se recupera una replica cualquiera, sincronizar desde el primario activo
        elif nodo_id != self.nodo_primario_id or not self._fallo_activo:
            primario = self.obtener_primario_activo()
            if primario and primario.status == NodeStatus.ONLINE:
                self.registrar_evento("SYNC",
                    f"Sincronizando {nodo.ciudad} desde primario {primario.ciudad} [v{primario.version_datos}]...")
                time.sleep(0.15)
                nodo.inventarios = dict(primario.inventarios)
                nodo.pedidos = dict(primario.pedidos)
                nodo.temperaturas = list(primario.temperaturas)
                nodo.envios = dict(primario.envios)
                nodo.vehiculos = dict(primario.vehiculos)
                nodo.version_datos = primario.version_datos
                nodo.operaciones_pendientes = 0
                self.registrar_evento("SYNC_COMPLETE",
                    f"{nodo.ciudad} sincronizado correctamente [v{nodo.version_datos}]")

        if self.callback_ui:
            self.callback_ui()


# ============================================================
# INTERFAZ GRAFICA CON TKINTER
# ============================================================

COLOR_BG = "#1a1a2e"
COLOR_BG2 = "#16213e"
COLOR_BG3 = "#0f3460"
COLOR_PRIMARY = "#FF6B35"
COLOR_REPLICA = "#004B87"
COLOR_ONLINE = "#00C853"
COLOR_OFFLINE = "#D32F2F"
COLOR_TEXT = "#E0E0E0"
COLOR_TEXT_DIM = "#AAAAAA"
COLOR_ACCENT = "#e94560"
COLOR_GOLD = "#FFD700"
COLOR_ASYNC = "#F77F00"
COLOR_SYNC = "#00E676"
COLOR_WARN = "#FFC107"
COLOR_PURPLE = "#7C4DFF"


class SimulacionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FedEx Peru - Sistema de Replicacion Distribuida | Lab 10 - Sistemas Distribuidos")
        self.root.state('zoomed')
        self.root.configure(bg=COLOR_BG)
        self.root.minsize(1100, 700)

        self._inicializar_sistema()
        self._running = True
        self._flash_animations = {}  # para animaciones de feedback visual

        self._construir_ui()

        self.gestor.callback_log = self._on_evento_log
        self.gestor.callback_ui = lambda: self.root.after(0, self._refrescar_ui)

        self._refrescar_ui()
        self._iniciar_actualizacion_periodica()

    def _inicializar_sistema(self):
        self.nodos = {
            "LIM": Nodo("LIM", "Lima", "Peru", es_primario=True),
            "BOG": Nodo("BOG", "Bogota", "Colombia", es_primario=False),
            "STG": Nodo("STG", "Santiago", "Chile", es_primario=False),
            "CDMX": Nodo("CDMX", "Ciudad de Mexico", "Mexico", es_primario=False),
        }

        self.gestor = GestorReplicacion(self.nodos, nodo_primario_id="LIM")

        productos = [
            Producto("PROD-001", "Mango fresco", "Frutas", 500, "kg", 8.0, 12.0),
            Producto("PROD-002", "Palta Hass", "Verduras", 300, "kg", 4.0, 8.0),
            Producto("PROD-003", "Salmon fresco", "Pescados", 200, "kg", 0.0, 4.0),
            Producto("PROD-004", "Lacteos premium", "Lacteos", 450, "L", 2.0, 6.0),
            Producto("PROD-005", "Flores de corte", "Flores", 1000, "unidades", 2.0, 10.0),
        ]
        for nodo in self.nodos.values():
            for p in productos:
                nodo.inventarios[p.id] = Producto(**asdict(p))
            for i in range(3):
                t = Temperatura(sede=nodo.ciudad,
                                valor=round(random.uniform(0, 15), 1),
                                humedad=round(random.uniform(40, 80), 1),
                                timestamp=datetime.now().isoformat())
                nodo.temperaturas.append(t)
            nodo.version_datos = 5

        for i in range(3):
            pedido = Pedido(
                id=f"PED-{i+1:03d}",
                cliente=f"Cliente {chr(65+i)}",
                producto_id=productos[i].id,
                cantidad=random.randint(5, 30),
                origen="Lima",
                destino=random.choice(["Bogota", "Santiago", "CDMX"]),
                estado="PENDIENTE",
                fecha_creacion=datetime.now().isoformat()
            )
            for nodo in self.nodos.values():
                nodo.pedidos[pedido.id] = Pedido(**asdict(pedido))

        vehiculos_data = [
            ("VEH-001", "ABC-123", "Refrigerado", {"lat": -12.0464, "lon": -77.0428}),
            ("VEH-002", "DEF-456", "Refrigerado", {"lat": 4.7110, "lon": -74.0721}),
            ("VEH-003", "GHI-789", "Seco", {"lat": -33.4489, "lon": -70.6693}),
            ("VEH-004", "JKL-012", "Refrigerado", {"lat": 19.4326, "lon": -99.1332}),
        ]
        for vdata in vehiculos_data:
            v = Vehiculo(id=vdata[0], placa=vdata[1], tipo=vdata[2],
                         ubicacion_actual=vdata[3], estado="DISPONIBLE",
                         ultima_actualizacion=datetime.now().isoformat())
            for nodo in self.nodos.values():
                nodo.vehiculos[v.id] = Vehiculo(**asdict(v))

    # ============================================================
    # CONSTRUCCION DE UI
    # ============================================================

    def _construir_ui(self):
        # ---- HEADER ----
        header = tk.Frame(self.root, bg=COLOR_BG2, height=65)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        left_h = tk.Frame(header, bg=COLOR_BG2)
        left_h.pack(side=tk.LEFT, padx=18, pady=10)
        tk.Label(left_h, text="FedEx", font=("Arial", 20, "bold"),
                 fg=COLOR_PRIMARY, bg=COLOR_BG2).pack(side=tk.LEFT)
        tk.Label(left_h, text=" Peru", font=("Arial", 20, "bold"),
                 fg="white", bg=COLOR_BG2).pack(side=tk.LEFT)
        tk.Label(left_h, text="  |  Sistema de Replicacion Distribuida",
                 font=("Consolas", 11), fg=COLOR_TEXT_DIM, bg=COLOR_BG2).pack(side=tk.LEFT, padx=(6, 0))

        right_h = tk.Frame(header, bg=COLOR_BG2)
        right_h.pack(side=tk.RIGHT, padx=18, pady=10)

        self._lbl_primario_activo = tk.Label(right_h, text="Primario: LIMA",
                                             font=("Consolas", 10, "bold"),
                                             fg=COLOR_PRIMARY, bg=COLOR_BG2)
        self._lbl_primario_activo.pack(side=tk.RIGHT, padx=(10, 0))
        tk.Label(right_h, text="Lab 10 - UNSA 2026-A",
                 font=("Consolas", 9), fg=COLOR_TEXT_DIM, bg=COLOR_BG2).pack(side=tk.RIGHT)

        # ---- BARRA DE ESTADO RAPIDA ----
        status_bar = tk.Frame(self.root, bg=COLOR_BG3, height=28)
        status_bar.pack(fill=tk.X, side=tk.TOP)
        status_bar.pack_propagate(False)

        self._lbl_status = tk.Label(status_bar, text="Sistema operativo | 4 nodos en linea | Modo: ASINCRONA",
                                    font=("Consolas", 9), fg=COLOR_TEXT_DIM, bg=COLOR_BG3, anchor=tk.W)
        self._lbl_status.pack(side=tk.LEFT, padx=12, pady=3)

        self._lbl_pendientes = tk.Label(status_bar, text="",
                                        font=("Consolas", 9), fg=COLOR_ASYNC, bg=COLOR_BG3, anchor=tk.E)
        self._lbl_pendientes.pack(side=tk.RIGHT, padx=12, pady=3)

        # ---- CONTENIDO PRINCIPAL ----
        main = tk.Frame(self.root, bg=COLOR_BG)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Panel izquierdo
        left_panel = tk.Frame(main, bg=COLOR_BG, width=420)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        left_panel.pack_propagate(False)

        self._construir_panel_nodos(left_panel)
        self._construir_panel_controles(left_panel)

        # Panel derecho
        right_panel = tk.Frame(main, bg=COLOR_BG)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Sub-paneles superiores (arquitectura + datos)
        right_top = tk.Frame(right_panel, bg=COLOR_BG, height=380)
        right_top.pack(fill=tk.X, expand=False)
        right_top.pack_propagate(False)

        arch_frame = tk.Frame(right_top, bg=COLOR_BG)
        arch_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))

        data_frame = tk.Frame(right_top, bg=COLOR_BG, width=380)
        data_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        data_frame.pack_propagate(False)

        self._construir_panel_arquitectura(arch_frame)
        self._construir_panel_datos(data_frame)

        # Log
        self._construir_panel_log(right_panel)

    def _construir_panel_nodos(self, parent):
        frame = tk.LabelFrame(parent, text=" Centros de Distribucion ",
                              font=("Consolas", 10, "bold"),
                              fg=COLOR_TEXT, bg=COLOR_BG, bd=1, relief=tk.RIDGE)
        frame.pack(fill=tk.X, pady=3)

        self._nodo_frames = {}

        for nid, nodo in self.nodos.items():
            nf = tk.Frame(frame, bg=COLOR_BG2, bd=1, relief=tk.GROOVE)
            nf.pack(fill=tk.X, padx=8, pady=3)

            # Indicador LED
            canvas = tk.Canvas(nf, width=18, height=18, bg=COLOR_BG2, highlightthickness=0)
            canvas.pack(side=tk.LEFT, padx=(8, 6), pady=6)
            dot = canvas.create_oval(2, 2, 16, 16, fill=COLOR_ONLINE, outline="", tags="dot")
            ring = canvas.create_oval(1, 1, 17, 17, outline=COLOR_ONLINE, width=2, tags="ring")

            # Info
            info = tk.Frame(nf, bg=COLOR_BG2)
            info.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=3)

            rol_text = "PRIMARIO" if nodo.es_primario else "REPLICA"
            color_rol = COLOR_PRIMARY if nodo.es_primario else COLOR_REPLICA
            status_text = "ONLINE" if nodo.status == NodeStatus.ONLINE else "OFFLINE"

            header_row = tk.Frame(info, bg=COLOR_BG2)
            header_row.pack(anchor=tk.W, fill=tk.X)

            self_lbl_nombre = tk.Label(header_row, text=f"{nid}",
                                       font=("Consolas", 12, "bold"), fg=color_rol, bg=COLOR_BG2)
            self_lbl_nombre.pack(side=tk.LEFT)

            tk.Label(header_row, text=f" {rol_text}",
                     font=("Consolas", 8, "bold"), fg=color_rol, bg=COLOR_BG2).pack(side=tk.LEFT, padx=4)

            tk.Label(info, text=f"{nodo.ciudad}, {nodo.pais}",
                     font=("Consolas", 8), fg=COLOR_TEXT_DIM, bg=COLOR_BG2).pack(anchor=tk.W)

            lbl_stats = tk.Label(info, text="", font=("Consolas", 7),
                                 fg=COLOR_TEXT_DIM, bg=COLOR_BG2)
            lbl_stats.pack(anchor=tk.W, pady=1)

            # Botones
            btn_frame = tk.Frame(nf, bg=COLOR_BG2)
            btn_frame.pack(side=tk.RIGHT, padx=8)

            btn_caer = tk.Button(btn_frame, text="Tirar", font=("Consolas", 7, "bold"),
                                 bg=COLOR_ACCENT, fg="white", bd=0, padx=8, pady=2,
                                 cursor="hand2", activebackground="#c0392b",
                                 command=lambda n=nid: self._tirar_nodo(n))
            btn_caer.pack(side=tk.TOP, pady=1)

            btn_up = tk.Button(btn_frame, text="Recuperar", font=("Consolas", 7, "bold"),
                               bg=COLOR_ONLINE, fg="white", bd=0, padx=8, pady=2,
                               cursor="hand2", activebackground="#27ae60",
                               command=lambda n=nid: self._recuperar_nodo(n))
            btn_up.pack(side=tk.TOP, pady=1)

            self._nodo_frames[nid] = {
                "frame": nf, "canvas": canvas, "dot": dot, "ring": ring,
                "stats": lbl_stats, "btn_caer": btn_caer, "btn_up": btn_up,
                "info_frame": info, "header_lbl": self_lbl_nombre, "header_row": header_row
            }

    def _construir_panel_controles(self, parent):
        frame = tk.LabelFrame(parent, text=" Panel de Operaciones ",
                              font=("Consolas", 10, "bold"),
                              fg=COLOR_TEXT, bg=COLOR_BG, bd=1, relief=tk.RIDGE)
        frame.pack(fill=tk.X, pady=3)

        # ---- MODO DE REPLICACION ----
        modo_frame = tk.Frame(frame, bg=COLOR_BG)
        modo_frame.pack(fill=tk.X, padx=10, pady=(8, 3))

        tk.Label(modo_frame, text="Modo:", font=("Consolas", 9, "bold"),
                 fg=COLOR_TEXT, bg=COLOR_BG).pack(side=tk.LEFT, padx=(0, 8))

        self._btn_sync = tk.Button(modo_frame, text="SINCRONA", font=("Consolas", 9, "bold"),
                                   bg=COLOR_BG3, fg=COLOR_TEXT_DIM, bd=0, padx=10, pady=3,
                                   cursor="hand2", command=lambda: self._cambiar_modo("sync"))
        self._btn_sync.pack(side=tk.LEFT, padx=2)

        self._btn_async = tk.Button(modo_frame, text="ASINCRONA", font=("Consolas", 9, "bold"),
                                    bg=COLOR_ASYNC, fg="white", bd=0, padx=10, pady=3,
                                    cursor="hand2", command=lambda: self._cambiar_modo("async"))
        self._btn_async.pack(side=tk.LEFT, padx=2)

        self._lbl_modo_desc = tk.Label(modo_frame, text=" - Mayor rendimiento, posible retraso",
                                       font=("Consolas", 7), fg=COLOR_TEXT_DIM, bg=COLOR_BG)
        self._lbl_modo_desc.pack(side=tk.LEFT, padx=10)

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=6)

        # ---- OPERACIONES DE DATOS ----
        tk.Label(frame, text="Operaciones sobre el primario activo:",
                 font=("Consolas", 8, "bold"), fg=COLOR_TEXT_DIM, bg=COLOR_BG).pack(anchor=tk.W, padx=10)

        ops_frame = tk.Frame(frame, bg=COLOR_BG)
        ops_frame.pack(fill=tk.X, padx=10, pady=4)

        btns_data = [
            ("+ Nuevo Pedido", COLOR_PRIMARY, self._crear_pedido_aleatorio,
             "Crea un pedido en el primario y replica a las secundarias"),
            ("Actualizar Inventario", COLOR_REPLICA, self._actualizar_inventario_aleatorio,
             "Modifica el stock de un producto aleatorio"),
            ("Registrar Temperatura", "#1B5E20", self._registrar_temperatura_aleatoria,
             "Registra lectura de temperatura del almacen"),
            ("Nuevo Envio", COLOR_PURPLE, self._crear_envio_aleatorio,
             "Crea un envio asignado a un vehiculo"),
            ("Mover Vehiculo (GPS)", "#6A1B9A", self._actualizar_vehiculo_aleatorio,
             "Actualiza ubicacion GPS de un vehiculo"),
        ]

        for texto, color, cmd, tooltip in btns_data:
            btn = tk.Button(ops_frame, text=texto, font=("Consolas", 9),
                            bg=color, fg="white", bd=0, padx=8, pady=4,
                            cursor="hand2", command=cmd)
            btn.pack(fill=tk.X, pady=1)
            self._crear_tooltip(btn, tooltip)

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=6)

        # ---- ESCENARIO DE FALLO ----
        tk.Label(frame, text="Escenario de Fallo (Actividad 4):",
                 font=("Consolas", 8, "bold"), fg=COLOR_TEXT_DIM, bg=COLOR_BG).pack(anchor=tk.W, padx=10)

        scenario_frame = tk.Frame(frame, bg=COLOR_BG)
        scenario_frame.pack(fill=tk.X, padx=10, pady=4)

        btn_fallo = tk.Button(scenario_frame, text="Simular Caida de Lima (20 min)",
                              font=("Consolas", 9, "bold"),
                              bg=COLOR_ACCENT, fg="white", bd=0, padx=10, pady=6,
                              cursor="hand2", command=self._simular_escenario_fallo)
        btn_fallo.pack(fill=tk.X, pady=2)
        self._crear_tooltip(btn_fallo,
            "1.Genera pedidos en Lima 2.Tira Lima 3.Failover automatico 4.Opera en Bogota")

        btn_rec = tk.Button(scenario_frame, text="Recuperar Lima y Restaurar Sistema",
                            font=("Consolas", 9, "bold"),
                            bg=COLOR_ONLINE, fg="white", bd=0, padx=10, pady=6,
                            cursor="hand2", command=self._recuperar_escenario)
        btn_rec.pack(fill=tk.X, pady=2)
        self._crear_tooltip(btn_rec,
            "Sincroniza Lima con los datos mas recientes y la restaura como primario")

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=6)

        # ---- REINICIAR ----
        btn_reset = tk.Button(frame, text="Reiniciar Simulacion",
                              font=("Consolas", 9),
                              bg="#424242", fg=COLOR_TEXT, bd=0, padx=10, pady=4,
                              cursor="hand2", command=self._reiniciar_sistema)
        btn_reset.pack(fill=tk.X, padx=10, pady=(2, 6))

        # Pie
        tk.Label(frame, text="UNSA 2026-A | Mg. Maribel Molina Barriga",
                 font=("Consolas", 7), fg="#555", bg=COLOR_BG).pack(pady=4)

    def _construir_panel_arquitectura(self, parent):
        frame = tk.LabelFrame(parent, text=" Diagrama de Arquitectura ",
                              font=("Consolas", 10, "bold"),
                              fg=COLOR_TEXT, bg=COLOR_BG, bd=1, relief=tk.RIDGE)
        frame.pack(fill=tk.BOTH, expand=True)

        self._arch_canvas = tk.Canvas(frame, bg=COLOR_BG2, highlightthickness=0)
        self._arch_canvas.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self._arch_canvas.bind("<Configure>", lambda e: self._dibujar_arquitectura())

    def _dibujar_arquitectura(self):
        c = self._arch_canvas
        c.delete("all")
        w = max(c.winfo_width(), 400)
        h = max(c.winfo_height(), 280)

        if w < 100 or h < 100:
            return

        # Posiciones
        pos = {
            "LIM": (w * 0.12, h * 0.55),
            "BOG": (w * 0.32, h * 0.55),
            "STG": (w * 0.52, h * 0.55),
            "CDMX": (w * 0.72, h * 0.55),
        }
        size = 42

        # Titulo
        c.create_text(w/2, 22, text="ARQUITECTURA MAESTRO - REPLICA",
                      fill=COLOR_TEXT, font=("Consolas", 12, "bold"))
        c.create_text(w/2, 44, text="Balanceador de Carga (DNS Geo-Routing + HAProxy) - Redis Cache",
                      fill=COLOR_ACCENT, font=("Consolas", 8))

        # Lineas del balanceador
        for x, y in pos.values():
            c.create_line(x, 58, x, y - size - 8, fill="#3a3a5c", width=1, dash=(3, 3))

        # Flechas de replicacion entre nodos
        modo_color = COLOR_SYNC if self.gestor.modo == ReplicationMode.SYNCHRONOUS else COLOR_ASYNC
        for oid, (ox, oy) in pos.items():
            nodo_o = self.nodos[oid]
            if nodo_o.status != NodeStatus.ONLINE:
                continue
            for did, (dx, dy) in pos.items():
                if oid == did:
                    continue
                nodo_d = self.nodos[did]
                # Solo dibujar flecha si ambos estan ONLINE
                if nodo_o.status != NodeStatus.ONLINE or nodo_d.status != NodeStatus.ONLINE:
                    continue
                # Flecha de origen a destino
                c.create_line(ox + size + 4, oy, dx - size - 4, dy,
                              fill=modo_color, width=1.8,
                              arrow=tk.LAST, arrowshape=(12, 14, 6))

        # Nodos
        for nid, (x, y) in pos.items():
            nodo = self.nodos[nid]
            is_primary = nodo.es_primario
            is_online = nodo.status == NodeStatus.ONLINE

            fill_color = COLOR_PRIMARY if is_primary else COLOR_REPLICA
            if not is_online:
                fill_color = "#424242"
            outline_color = COLOR_ONLINE if is_online else COLOR_OFFLINE

            # Sombra
            c.create_oval(x - size - 3, y - size - 3, x + size + 3, y + size + 3,
                          fill="#000000", outline="", tags=f"nodo_{nid}")

            # Circulo
            c.create_oval(x - size, y - size, x + size, y + size,
                          fill=fill_color, outline=outline_color, width=3, tags=f"nodo_{nid}")

            # Texto ID
            c.create_text(x, y - 8, text=nid if is_online else f"{nid}",
                          fill="white", font=("Consolas", 13, "bold"), tags=f"nodo_{nid}")

            # Estado
            estado = "ONLINE" if is_online else "CAIDO"
            estado_color = COLOR_ONLINE if is_online else COLOR_OFFLINE
            dot_x = x
            c.create_oval(dot_x - 4, y + 6, dot_x + 4, y + 14, fill=estado_color, outline="", tags=f"nodo_{nid}")
            c.create_text(x + 10, y + 10, text=estado, anchor=tk.W,
                          fill=estado_color, font=("Consolas", 7, "bold"), tags=f"nodo_{nid}")

            # Rol
            rol = "PRIMARIO" if is_primary else "REPLICA"
            c.create_text(x, y + 24, text=rol, fill="#CCC" if is_online else "#777",
                          font=("Consolas", 7), tags=f"nodo_{nid}")

            # Ciudad
            c.create_text(x, y + size + 14, text=nodo.ciudad, fill=COLOR_TEXT_DIM,
                          font=("Consolas", 9), tags=f"nodo_{nid}")
            c.create_text(x, y + size + 28, text=f"v{nodo.version_datos} | "
                          f"Inv:{len(nodo.inventarios)} Ped:{len(nodo.pedidos)}",
                          fill="#666", font=("Consolas", 7), tags=f"nodo_{nid}")

        # Leyenda de modo
        lx, ly = w - 210, h - 55
        c.create_rectangle(lx - 5, ly - 5, lx + 205, ly + 50,
                           fill=COLOR_BG, outline="#444")
        modo_nombre = "SINCRONA" if self.gestor.modo == ReplicationMode.SYNCHRONOUS else "ASINCRONA"
        c.create_text(lx + 100, ly + 8, text="REPLICACION",
                      fill=COLOR_TEXT, font=("Consolas", 8, "bold"))
        c.create_text(lx + 100, ly + 26, text=f"Modo: {modo_nombre}",
                      fill=modo_color, font=("Consolas", 10, "bold"))
        c.create_text(lx + 100, ly + 42, text="Maestro-Replica c/ Failover",
                      fill=COLOR_TEXT_DIM, font=("Consolas", 7))

    def _construir_panel_datos(self, parent):
        frame = tk.LabelFrame(parent, text=" Comparativa entre Nodos ",
                              font=("Consolas", 10, "bold"),
                              fg=COLOR_TEXT, bg=COLOR_BG, bd=1, relief=tk.RIDGE)
        frame.pack(fill=tk.BOTH, expand=True)

        columns = ("metrica", "LIM", "BOG", "STG", "CDMX", "estado")
        self._data_tree = ttk.Treeview(frame, columns=columns, show="headings", height=11)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=COLOR_BG2, foreground=COLOR_TEXT,
                        fieldbackground=COLOR_BG2, rowheight=26,
                        font=("Consolas", 9), borderwidth=0)
        style.configure("Treeview.Heading", background=COLOR_BG3, foreground=COLOR_TEXT,
                        font=("Consolas", 8, "bold"), relief=tk.FLAT, borderwidth=0)
        style.map("Treeview.Heading", background=[("active", COLOR_BG3)])

        widths = {"metrica": 110, "LIM": 55, "BOG": 55, "STG": 55, "CDMX": 55, "estado": 60}
        for col in columns:
            self._data_tree.heading(col, text=col)
            self._data_tree.column(col, width=widths.get(col, 50), anchor=tk.CENTER, minwidth=40)

        self._data_tree.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self._data_tree.yview)
        self._data_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._data_tree.tag_configure("inconsistente", background="#3e1a1a", foreground="#FF8A80")
        self._data_tree.tag_configure("consistente", background=COLOR_BG2, foreground=COLOR_TEXT)
        self._data_tree.tag_configure("separador", background=COLOR_BG3)

    def _construir_panel_log(self, parent):
        frame = tk.LabelFrame(parent, text=" Registro de Eventos - Log de Replicacion ",
                              font=("Consolas", 10, "bold"),
                              fg=COLOR_TEXT, bg=COLOR_BG, bd=1, relief=tk.RIDGE)
        frame.pack(fill=tk.BOTH, expand=True, pady=3)

        log_container = tk.Frame(frame, bg=COLOR_BG)
        log_container.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        self._log_text = scrolledtext.ScrolledText(
            log_container, height=8, bg="#0a0a14", fg="#CCCCCC",
            font=("Consolas", 9), wrap=tk.WORD, bd=0,
            insertbackground=COLOR_PRIMARY, state=tk.DISABLED
        )
        self._log_text.pack(fill=tk.BOTH, expand=True)

        self._log_text.tag_configure("FAILURE", foreground="#FF5252")
        self._log_text.tag_configure("FAILOVER", foreground=COLOR_PRIMARY)
        self._log_text.tag_configure("RECOVERY", foreground=COLOR_ONLINE)
        self._log_text.tag_configure("RESTORE", foreground=COLOR_GOLD)
        self._log_text.tag_configure("SYNC", foreground=COLOR_SYNC)
        self._log_text.tag_configure("ASYNC", foreground=COLOR_ASYNC)
        self._log_text.tag_configure("WARN", foreground=COLOR_WARN)
        self._log_text.tag_configure("INFO", foreground=COLOR_TEXT_DIM)

    def _crear_tooltip(self, widget, texto):
        """Tooltip simple que aparece al pasar el mouse."""
        def mostrar(event):
            if hasattr(self, '_tooltip_win') and self._tooltip_win:
                self._tooltip_win.destroy()
            x = event.x_root + 15
            y = event.y_root + 10
            self._tooltip_win = tw = tk.Toplevel(widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            lbl = tk.Label(tw, text=texto, font=("Consolas", 7),
                           bg="#333", fg="#EEE", padx=6, pady=3,
                           relief=tk.SOLID, borderwidth=1)
            lbl.pack()

        def ocultar(event):
            if hasattr(self, '_tooltip_win') and self._tooltip_win:
                self._tooltip_win.destroy()
                self._tooltip_win = None

        widget.bind("<Enter>", mostrar)
        widget.bind("<Leave>", ocultar)

    # ============================================================
    # ACCIONES DE USUARIO
    # ============================================================

    def _tirar_nodo(self, nodo_id: str):
        if self.nodos[nodo_id].status == NodeStatus.OFFLINE:
            return
        self.gestor.simular_caida_nodo(nodo_id)
        self._refrescar_ui()

    def _recuperar_nodo(self, nodo_id: str):
        if self.nodos[nodo_id].status == NodeStatus.ONLINE:
            return
        self.gestor.recuperar_nodo(nodo_id)
        self._refrescar_ui()

    def _cambiar_modo(self, modo: str):
        if modo == "sync":
            self.gestor.modo = ReplicationMode.SYNCHRONOUS
            self._btn_sync.configure(bg=COLOR_SYNC, fg="black")
            self._btn_async.configure(bg=COLOR_BG3, fg=COLOR_TEXT_DIM)
            self._lbl_modo_desc.configure(text=" - Consistencia fuerte, mayor latencia")
        else:
            self.gestor.modo = ReplicationMode.ASYNCHRONOUS
            self._btn_async.configure(bg=COLOR_ASYNC, fg="white")
            self._btn_sync.configure(bg=COLOR_BG3, fg=COLOR_TEXT_DIM)
            self._lbl_modo_desc.configure(text=" - Mayor rendimiento, posible retraso")
        self._refrescar_ui()

    def _ejecutar_en_primario(self, operacion_fn, nombre_op: str):
        """Ejecuta una operacion en el primario activo con manejo de errores."""
        primario = self.gestor.obtener_primario_activo()
        if not primario:
            messagebox.showwarning("Sin Primario",
                                   "No hay ningun nodo primario activo en el sistema.\n"
                                   "Use 'Recuperar' en un nodo para restablecer el servicio.")
            return None
        if primario.status != NodeStatus.ONLINE:
            messagebox.showwarning("Primario Caido",
                                   f"El primario ({primario.ciudad}) esta fuera de linea.\n"
                                   "El failover deberia haberse activado. Revise el sistema.")
            return None
        return operacion_fn(primario)

    def _replicar_desde_primario(self, primario):
        entrada = primario.log_operaciones[-1]
        self.gestor.replicar_operacion(primario, entrada)
        self._refrescar_ui()

    def _crear_pedido_aleatorio(self):
        def op(primario):
            productos = list(primario.inventarios.keys())
            if not productos:
                return False
            nuevo_id = f"PED-{random.randint(100, 999)}"
            pedido = Pedido(
                id=nuevo_id,
                cliente=f"Cliente {chr(random.randint(65, 90))}",
                producto_id=random.choice(productos),
                cantidad=random.randint(5, 50),
                origen=primario.ciudad,
                destino=random.choice(["Bogota", "Santiago", "CDMX"]),
                estado="PENDIENTE",
                fecha_creacion=datetime.now().isoformat()
            )
            primario.crear_pedido(pedido)
            return True
        if self._ejecutar_en_primario(op, "Crear Pedido"):
            self._replicar_desde_primario(self.gestor.obtener_primario_activo())

    def _actualizar_inventario_aleatorio(self):
        def op(primario):
            if not primario.inventarios:
                return False
            pid = random.choice(list(primario.inventarios.keys()))
            prod = primario.inventarios[pid]
            delta = random.randint(-30, 30)
            prod.cantidad = max(0, prod.cantidad + delta)
            prod.fecha_actualizacion = datetime.now().isoformat()
            primario.actualizar_inventario(prod)
            return True
        if self._ejecutar_en_primario(op, "Actualizar Inventario"):
            self._replicar_desde_primario(self.gestor.obtener_primario_activo())

    def _registrar_temperatura_aleatoria(self):
        def op(primario):
            temp = Temperatura(
                sede=primario.ciudad,
                valor=round(random.uniform(0, 15), 1),
                humedad=round(random.uniform(40, 80), 1),
                timestamp=datetime.now().isoformat()
            )
            primario.registrar_temperatura(temp)
            return True
        if self._ejecutar_en_primario(op, "Registrar Temperatura"):
            self._replicar_desde_primario(self.gestor.obtener_primario_activo())

    def _crear_envio_aleatorio(self):
        def op(primario):
            if not primario.pedidos or not primario.vehiculos:
                return False
            pedido_id = random.choice(list(primario.pedidos.keys()))
            vehiculo_id = random.choice(list(primario.vehiculos.keys()))
            envio = Envio(
                id=f"ENV-{random.randint(100, 999)}",
                pedido_id=pedido_id,
                vehiculo_id=vehiculo_id,
                origen=primario.ciudad,
                destino=primario.pedidos[pedido_id].destino,
                estado="EN_ORIGEN",
                ultima_actualizacion=datetime.now().isoformat()
            )
            primario.crear_envio(envio)
            return True
        if self._ejecutar_en_primario(op, "Crear Envio"):
            self._replicar_desde_primario(self.gestor.obtener_primario_activo())

    def _actualizar_vehiculo_aleatorio(self):
        def op(primario):
            if not primario.vehiculos:
                return False
            vid = random.choice(list(primario.vehiculos.keys()))
            v = primario.vehiculos[vid]
            v.ubicacion_actual = {
                "lat": round(random.uniform(-34, 20), 4),
                "lon": round(random.uniform(-100, -70), 4)
            }
            v.ultima_actualizacion = datetime.now().isoformat()
            primario.actualizar_ubicacion_vehiculo(v)
            return True
        if self._ejecutar_en_primario(op, "Mover Vehiculo"):
            self._replicar_desde_primario(self.gestor.obtener_primario_activo())

    def _simular_escenario_fallo(self):
        """Simulacion del escenario de fallo de Lima (Actividad 4)."""
        # Verificar que Lima este online
        if self.nodos["LIM"].status != NodeStatus.ONLINE:
            messagebox.showinfo("Lima ya esta caida",
                                "Lima ya esta fuera de linea. Use 'Recuperar Lima y Restaurar'.")
            return

        self._log_evento_ui("\n=== INICIANDO ESCENARIO DE FALLO (Actividad 4) ===", "INFO")
        self._log_evento_ui("Fase 1: Generando operaciones en Lima antes de la caida...", "INFO")

        # Generar operaciones en Lima antes de la caida (en thread para no bloquear)
        def escenario():
            primario = self.gestor.obtener_primario_activo()
            if not primario or primario.sede_id != "LIM":
                return

            for i in range(3):
                productos = list(primario.inventarios.keys())
                if productos:
                    pedido = Pedido(
                        id=f"PED-FALLO-{i+1}",
                        cliente=f"Cliente X{i+1}",
                        producto_id=random.choice(productos),
                        cantidad=random.randint(10, 40),
                        origen="Lima",
                        destino=random.choice(["Bogota", "Santiago", "CDMX"]),
                        estado="PENDIENTE",
                        fecha_creacion=datetime.now().isoformat()
                    )
                    primario.crear_pedido(pedido)
                    entrada = primario.log_operaciones[-1]
                    self.gestor.replicacion_asincrona(primario, entrada)
                time.sleep(0.15)

            self.root.after(0, self._refrescar_ui)
            time.sleep(0.3)

            # Fase 2: Caida de Lima
            self.root.after(0, lambda: self._log_evento_ui(
                "Fase 2: Lima ha caido. Activando failover...", "FAILURE"))
            self.root.after(0, lambda: self.gestor.simular_caida_nodo("LIM"))
            time.sleep(0.2)
            self.root.after(0, self._refrescar_ui)
            time.sleep(0.3)

            # Fase 3: Operar en el nuevo primario (Bogota)
            nuevo_primario = self.gestor.obtener_primario_activo()
            if nuevo_primario:
                self.root.after(0, lambda: self._log_evento_ui(
                    f"Fase 3: Operando en el nuevo primario {nuevo_primario.ciudad}...", "FAILOVER"))
                for i in range(2):
                    productos = list(nuevo_primario.inventarios.keys())
                    if productos:
                        pedido = Pedido(
                            id=f"PED-POST-{i+1}",
                            cliente=f"Cliente Y{i+1}",
                            producto_id=random.choice(productos),
                            cantidad=random.randint(5, 25),
                            origen=nuevo_primario.ciudad,
                            destino=random.choice(["Santiago", "CDMX"]),
                            estado="PENDIENTE",
                            fecha_creacion=datetime.now().isoformat()
                        )
                        nuevo_primario.crear_pedido(pedido)
                        entrada = nuevo_primario.log_operaciones[-1]
                        self.gestor.replicacion_asincrona(nuevo_primario, entrada)
                    time.sleep(0.15)
                self.root.after(0, self._refrescar_ui)
                self.root.after(0, lambda: self._log_evento_ui(
                    "Escenario de fallo completado. Lima caida, Bogota es primario.\n"
                    "Use 'Recuperar Lima y Restaurar' para restaurar el sistema.", "INFO"))

        threading.Thread(target=escenario, daemon=True).start()

    def _recuperar_escenario(self):
        """Recuperar Lima despues del fallo."""
        if self.nodos["LIM"].status == NodeStatus.ONLINE and not self.gestor._fallo_activo:
            messagebox.showinfo("Lima ya esta operativa",
                                "Lima esta en linea y es el primario. No es necesario recuperar.")
            return

        self._log_evento_ui("\n=== RECUPERANDO LIMA Y RESTAURANDO SISTEMA ===", "INFO")
        self.gestor.recuperar_nodo("LIM")
        self._refrescar_ui()

    def _reiniciar_sistema(self):
        if messagebox.askyesno("Reiniciar Simulacion",
                               "Esto reiniciara todos los datos y el estado del sistema.\n"
                               "Todos los nodos volveran a estar en linea.\n\n"
                               "Desea continuar?"):
            self._inicializar_sistema()
            self.gestor.callback_log = self._on_evento_log
            self.gestor.callback_ui = lambda: self.root.after(0, self._refrescar_ui)
            self._log_text.configure(state=tk.NORMAL)
            self._log_text.delete("1.0", tk.END)
            self._log_text.configure(state=tk.DISABLED)
            self._cambiar_modo("async")
            self._refrescar_ui()
            self._log_evento_ui("Sistema reiniciado. Todos los nodos en linea.", "INFO")

    # ============================================================
    # LOG Y ACTUALIZACION
    # ============================================================

    def _on_evento_log(self, evento: Dict):
        self.root.after(0, self._agregar_log, evento)

    def _agregar_log(self, evento: Dict):
        ts = evento["timestamp"]
        tipo = evento["tipo"]
        msg = evento["mensaje"]

        tipo_a_tag = {
            "FAILURE": ("FAIL", "FAILURE"),
            "FAILOVER": ("FAILOVER", "FAILOVER"),
            "FAILOVER_SUCCESS": ("FAILOVER_OK", "FAILOVER"),
            "FAILOVER_FAIL": ("FAILOVER_ERR", "FAILURE"),
            "RECOVERY": ("RECOVER", "RECOVERY"),
            "RESTORE": ("RESTORE", "RESTORE"),
            "SYNC": ("SYNC", "SYNC"),
            "SYNC_COMPLETE": ("SYNC_OK", "SYNC"),
            "REPLICA_ASYNC": ("ASYNC_OK", "ASYNC"),
            "REPLICA_ASYNC_QUEUED": ("ASYNC_QUEUED", "ASYNC"),
            "REPLICA_SYNC": ("SYNC_REPL", "SYNC"),
            "REPLICA_SYNC_FAIL": ("SYNC_FAIL", "FAILURE"),
            "WARN": ("WARN", "WARN"),
            "ERROR": ("ERROR", "FAILURE"),
        }

        tag, color_tag = tipo_a_tag.get(tipo, ("INFO", "INFO"))
        line = f"[{ts}] [{tag}] {msg}\n"

        self._log_text.configure(state=tk.NORMAL)
        self._log_text.insert(tk.END, line, color_tag)
        self._log_text.see(tk.END)
        self._log_text.configure(state=tk.DISABLED)

    def _log_evento_ui(self, msg, color_tag="INFO"):
        """Agrega un mensaje al log directamente desde el hilo principal."""
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] [UI] {msg}\n"
        self._log_text.configure(state=tk.NORMAL)
        self._log_text.insert(tk.END, line, color_tag)
        self._log_text.see(tk.END)
        self._log_text.configure(state=tk.DISABLED)

    def _refrescar_ui(self):
        """Actualiza todos los elementos visuales."""
        self._actualizar_nodos()
        self._actualizar_tabla_datos()
        self._actualizar_barra_estado()
        self._dibujar_arquitectura()

    def _iniciar_actualizacion_periodica(self):
        """Timer que refresca la UI periodicamente (para datos asincronos)."""
        if not self._running:
            return
        self._actualizar_nodos()
        self._actualizar_tabla_datos()
        self._actualizar_barra_estado()
        self.root.after(1500, self._iniciar_actualizacion_periodica)

    def _actualizar_nodos(self):
        for nid, nodo in self.nodos.items():
            if nid not in self._nodo_frames:
                continue
            nf = self._nodo_frames[nid]

            is_online = nodo.status == NodeStatus.ONLINE
            is_primary = nodo.es_primario

            status_color = COLOR_ONLINE if is_online else COLOR_OFFLINE
            nf["canvas"].itemconfig(nf["dot"], fill=status_color)
            nf["canvas"].itemconfig(nf["ring"], outline=status_color)

            color_rol = COLOR_PRIMARY if is_primary else COLOR_REPLICA
            if not is_online:
                color_rol = "#666"
            nf["header_lbl"].configure(fg=color_rol)

            rol = "PRIMARIO" if is_primary else "REPLICA"
            pend = f" [pend:{nodo.operaciones_pendientes}]" if nodo.operaciones_pendientes > 0 else ""
            stats = (f"Inv:{len(nodo.inventarios)} Ped:{len(nodo.pedidos)} "
                     f"Env:{len(nodo.envios)} Veh:{len(nodo.vehiculos)} "
                     f"Tmp:{len(nodo.temperaturas)} | v{nodo.version_datos}{pend}")
            nf["stats"].configure(text=stats)

            if is_online:
                nf["btn_caer"].configure(state=tk.NORMAL, bg=COLOR_ACCENT)
                nf["btn_up"].configure(state=tk.DISABLED, bg="#555")
            else:
                nf["btn_caer"].configure(state=tk.DISABLED, bg="#555")
                nf["btn_up"].configure(state=tk.NORMAL, bg=COLOR_ONLINE)

    def _actualizar_tabla_datos(self):
        for item in self._data_tree.get_children():
            self._data_tree.delete(item)

        # Usar el primario activo como referencia, o LIM si no hay
        primario = self.gestor.obtener_primario_activo()
        ref_nodo = primario if (primario and primario.status == NodeStatus.ONLINE) else None

        # Si el primario activo esta caido, buscar cualquier nodo online como referencia
        if not ref_nodo:
            for n in self.nodos.values():
                if n.status == NodeStatus.ONLINE:
                    ref_nodo = n
                    break

        nodos_online = sum(1 for n in self.nodos.values() if n.status == NodeStatus.ONLINE)

        metricas = [
            ("--- ESTADO ---", ["", "", "", "", ""], None),
            ("Online?", ["SI" if n.status == NodeStatus.ONLINE else "NO" for n in self.nodos.values()], None),
            ("Es Primario?", ["SI" if n.es_primario else "NO" for n in self.nodos.values()], None),
            ("--- DATOS ---", ["", "", "", "", ""], None),
            ("Inventarios", [str(len(n.inventarios)) for n in self.nodos.values()],
             len(ref_nodo.inventarios) if ref_nodo else 0),
            ("Pedidos", [str(len(n.pedidos)) for n in self.nodos.values()],
             len(ref_nodo.pedidos) if ref_nodo else 0),
            ("Envios", [str(len(n.envios)) for n in self.nodos.values()],
             len(ref_nodo.envios) if ref_nodo else 0),
            ("Vehiculos", [str(len(n.vehiculos)) for n in self.nodos.values()],
             len(ref_nodo.vehiculos) if ref_nodo else 0),
            ("Temperaturas", [str(len(n.temperaturas)) for n in self.nodos.values()],
             len(ref_nodo.temperaturas) if ref_nodo else 0),
            ("--- SINCRONIZACION ---", ["", "", "", "", ""], None),
            ("Version Datos", [str(n.version_datos) for n in self.nodos.values()],
             ref_nodo.version_datos if ref_nodo else 0),
            ("Ops. Pendientes", [str(n.operaciones_pendientes) for n in self.nodos.values()],
             0),
        ]

        for nombre, vals, ref_val in metricas:
            if nombre.startswith("---"):
                item_id = self._data_tree.insert("", tk.END, values=[nombre] + vals + [""])
                self._data_tree.item(item_id, tags=("separador",))
                continue

            if ref_val is not None:
                consistente = all(int(v) == ref_val for v in vals)
                estado = "OK" if consistente else "DESFASADO"
            else:
                consistente = True
                estado = "-"

            tag_name = nombre
            item_id = self._data_tree.insert("", tk.END, values=[tag_name] + vals + [estado])

            if not consistente:
                self._data_tree.item(item_id, tags=("inconsistente",))
            else:
                self._data_tree.item(item_id, tags=("consistente",))

    def _actualizar_barra_estado(self):
        online = sum(1 for n in self.nodos.values() if n.status == NodeStatus.ONLINE)
        total = len(self.nodos)
        modo = "SINCRONA" if self.gestor.modo == ReplicationMode.SYNCHRONOUS else "ASINCRONA"

        primario = self.gestor.obtener_primario_activo()
        primario_nombre = primario.ciudad if primario else "NINGUNO"

        self._lbl_primario_activo.configure(
            text=f"Primario: {primario_nombre}",
            fg=COLOR_PRIMARY if primario else COLOR_OFFLINE
        )

        status_text = f"Modo: {modo} | Nodos activos: {online}/{total} | Primario activo: {primario_nombre}"
        self._lbl_status.configure(text=status_text)

        pendientes_total = sum(n.operaciones_pendientes for n in self.nodos.values())
        if pendientes_total > 0:
            self._lbl_pendientes.configure(
                text=f"Operaciones pendientes de replicar: {pendientes_total}",
                fg=COLOR_ASYNC)
        else:
            self._lbl_pendientes.configure(text="Todas las replicas sincronizadas", fg=COLOR_ONLINE)

    def on_close(self):
        self._running = False
        self.root.destroy()


def main():
    root = tk.Tk()

    try:
        root.iconbitmap(default=None)
    except:
        pass

    app = SimulacionGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)

    app._log_text.configure(state=tk.NORMAL)
    app._log_text.insert(tk.END,
        "=" * 65 + "\n"
        "  SISTEMAS DISTRIBUIDOS - LABORATORIO 10\n"
        "  REPLICACION DE DATOS EN SISTEMAS DISTRIBUIDOS\n"
        "  Caso: FedEx Peru - Transporte de Productos Perecibles\n"
        "  Arquitectura: Maestro-Replica con Failover Automatico\n"
        "=" * 65 + "\n\n"
        "  INSTRUCCIONES:\n"
        "  * Use los botones 'Tirar'/'Recuperar' para simular fallos.\n"
        "  * Alterne entre modo SINCRONA y ASINCRONA.\n"
        "  * Genere operaciones con los botones del panel izquierdo.\n"
        "  * Observe la tabla: detecta automaticamente inconsistencias.\n"
        "  * Use 'Simular Caida de Lima' para el escenario completo.\n"
        "  * El diagrama muestra flujo de replicacion en tiempo real.\n\n"
    )
    app._log_text.configure(state=tk.DISABLED)

    root.mainloop()


if __name__ == "__main__":
    main()
