"""
LogiFresh S.A. - Sistema de Distribucion de Alimentos Refrigerados
GUI Profesional con Tkinter
Arquitectura de Microservicios Distribuidos
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import threading
import re
import time
import json
from datetime import datetime
from queue import Queue
from enum import Enum

# ============================================================
# TEMA Y COLORES PROFESIONALES
# ============================================================
class Colors:
    BG_DARK      = "#0d1117"
    BG_SECONDARY = "#161b22"
    BG_CARD      = "#21262d"
    BG_INPUT     = "#0d1117"
    BORDER       = "#30363d"
    TEXT_PRIMARY = "#e6edf3"
    TEXT_SECONDARY = "#8b949e"
    TEXT_MUTED   = "#6e7681"
    ACCENT_BLUE  = "#58a6ff"
    ACCENT_GREEN = "#3fb950"
    ACCENT_YELLOW = "#d29922"
    ACCENT_RED   = "#f85149"
    ACCENT_ORANGE = "#db6d28"
    ACCENT_PURPLE = "#a371f7"
    SUCCESS_BG   = "#1a3a2a"
    ERROR_BG     = "#3a1a1a"
    WARNING_BG   = "#3a3a1a"
    INFO_BG      = "#1a2a3a"

class Status(Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DEGRADED = "DEGRADADO"

SERVICE_NAMES = {
    "pedidos": "Pedidos",
    "inventario": "Inventario",
    "facturacion": "Facturacion",
    "transporte": "Transporte",
    "notificaciones": "Notificaciones"
}

SERVICE_PORTS = {
    "pedidos": 5001,
    "inventario": 5002,
    "facturacion": 5003,
    "transporte": 5004,
    "notificaciones": 5005,
}

# ============================================================
# VALIDADORES
# ============================================================
class Validators:
    EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    @staticmethod
    def email(value):
        if not value:
            return True, ""
        if Validators.EMAIL_RE.match(value):
            return True, ""
        return False, "Formato de email invalido (ej: usuario@dominio.com)"

    @staticmethod
    def required(value, field_name="Campo"):
        if value and value.strip():
            return True, ""
        return False, f"{field_name} es obligatorio"

    @staticmethod
    def positive_integer(value, field_name="Campo"):
        if not value:
            return False, f"{field_name} es obligatorio"
        try:
            num = int(value)
            if num <= 0:
                return False, f"{field_name} debe ser mayor a 0"
            if num > 999:
                return False, f"{field_name} no puede exceder 999"
            return True, ""
        except ValueError:
            return False, f"{field_name} debe ser un numero entero valido"

    @staticmethod
    def product_id(value):
        if not value or not value.strip():
            return False, "ID de producto es obligatorio"
        pid = value.strip().upper()
        if not pid.startswith("P") or not pid[1:].isdigit():
            return False, "Formato invalido. Use P001, P002, etc."
        return True, ""

# ============================================================
# COMPONENTES REUTILIZABLES
# ============================================================
class ValidatedEntry(tk.Frame):
    def __init__(self, parent, label="", placeholder="", validator=None, width=28, **kwargs):
        super().__init__(parent, bg=Colors.BG_DARK)
        self.validator = validator
        self.valid = True

        if label:
            self.lbl = tk.Label(self, text=label, bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY,
                               font=("Segoe UI", 10), anchor=tk.W, width=14)
            self.lbl.pack(side=tk.LEFT, padx=(0, 5))

        self.entry = tk.Entry(self, bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY,
                              insertbackground=Colors.ACCENT_BLUE, relief=tk.FLAT,
                              font=("Segoe UI", 10), width=width,
                              highlightthickness=1, highlightbackground=Colors.BORDER)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if placeholder:
            self.entry.insert(0, placeholder)
            self.entry.bind("<FocusIn>", lambda e: self._on_focus_in(placeholder))
            self.entry.bind("<FocusOut>", lambda e: self._on_focus_out(placeholder))
            self.entry.config(fg=Colors.TEXT_MUTED)

        self.error_lbl = tk.Label(self, text="", bg=Colors.BG_DARK, fg=Colors.ACCENT_RED,
                                  font=("Segoe UI", 8))
        self.entry.bind("<KeyRelease>", lambda e: self.validate())

    def _on_focus_in(self, placeholder):
        if self.entry.get() == placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=Colors.TEXT_PRIMARY)

    def _on_focus_out(self, placeholder):
        if not self.entry.get():
            self.entry.insert(0, placeholder)
            self.entry.config(fg=Colors.TEXT_MUTED)

    def get(self):
        val = self.entry.get()
        return "" if val == self.entry.cget("fg") == Colors.TEXT_MUTED else val

    def set(self, value):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)

    def validate(self):
        if not self.validator:
            return
        value = self.get()

        if isinstance(self.validator, (list, tuple)):
            all_valid = True
            errors = []
            for v in self.validator:
                try:
                    ok, msg = v(value)
                    if not ok:
                        all_valid = False
                        errors.append(msg)
                except TypeError:
                    ok, msg = v(value, "")
                    if not ok:
                        all_valid = False
                        errors.append(msg)
            self.valid = all_valid
            if errors and value:
                self.show_error(errors[0])
            else:
                self.clear_error()
        else:
            try:
                ok, msg = self.validator(value)
                self.valid = ok
                if not ok and value:
                    self.show_error(msg)
                else:
                    self.clear_error()
            except Exception as e:
                self.valid = False
                if value:
                    self.show_error(str(e))

    def show_error(self, msg):
        self.error_lbl.config(text=f"  {msg}")
        self.entry.config(highlightbackground=Colors.ACCENT_RED)
        self.valid = False

    def clear_error(self):
        self.error_lbl.config(text="")
        self.entry.config(highlightbackground=Colors.BORDER)
        self.valid = True

    def pack_error(self):
        self.error_lbl.pack(side=tk.LEFT, padx=(5, 0))


class StatusDot(tk.Canvas):
    def __init__(self, parent, size=10, **kwargs):
        super().__init__(parent, width=size+4, height=size+4, bg=Colors.BG_DARK,
                        highlightthickness=0, **kwargs)
        self.size = size
        self.color = Colors.TEXT_MUTED
        self._draw()

    def _draw(self):
        self.delete("all")
        cx, cy = (self.size+4)//2, (self.size+4)//2
        r = self.size//2
        self.create_oval(cx-r, cy-r, cx+r, cy+r, fill=self.color, outline="")

    def set_color(self, color):
        self.color = color
        self._draw()


class StatCard(tk.Frame):
    def __init__(self, parent, title, icon="", **kwargs):
        super().__init__(parent, bg=Colors.BG_CARD, highlightthickness=1,
                        highlightbackground=Colors.BORDER, **kwargs)
        self.config(padx=15, pady=12)

        self.title_lbl = tk.Label(self, text=title, bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY,
                                  font=("Segoe UI", 9))
        self.title_lbl.pack(anchor=tk.W)

        self.value_lbl = tk.Label(self, text="--", bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY,
                                  font=("Segoe UI", 22, "bold"))
        self.value_lbl.pack(anchor=tk.W, pady=(2, 0))

    def set_value(self, value):
        self.value_lbl.config(text=str(value))


# ============================================================
# VENTANA PRINCIPAL
# ============================================================
class LogiFreshApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LogiFresh S.A. - Sistema de Distribucion de Alimentos Refrigerados")
        self.root.geometry("1280x780")
        self.root.minsize(1024, 600)
        self.root.configure(bg=Colors.BG_DARK)
        self.toast_queue = Queue()

        self._setup_styles()
        self._build_layout()
        self._start_refresh_cycle()
        self._process_toasts()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<Return>", lambda e: self._on_enter_key())
        self.root.bind("<Escape>", lambda e: self._on_escape_key())

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background=Colors.BG_DARK, borderwidth=0, tabmargins=[0, 0, 0, 0])
        style.configure("TNotebook.Tab", background=Colors.BG_SECONDARY, foreground=Colors.TEXT_SECONDARY,
                       padding=[18, 8], font=("Segoe UI", 10), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", Colors.BG_CARD)],
                  foreground=[("selected", Colors.ACCENT_BLUE)],
                  expand=[("selected", [0, 0, 0, 0])])
        style.configure("TFrame", background=Colors.BG_DARK)
        style.configure("Treeview", background=Colors.BG_CARD, foreground=Colors.TEXT_PRIMARY,
                       fieldbackground=Colors.BG_CARD, borderwidth=0, font=("Segoe UI", 9),
                       rowheight=28)
        style.configure("Treeview.Heading", background=Colors.BG_SECONDARY,
                       foreground=Colors.ACCENT_BLUE, font=("Segoe UI", 9, "bold"),
                       borderwidth=0, relief=tk.FLAT, padding=[8, 4])
        style.map("Treeview.Heading", background=[("active", Colors.BG_CARD)])
        style.map("Treeview", background=[("selected", Colors.ACCENT_BLUE)],
                  foreground=[("selected", Colors.BG_DARK)])
        style.configure("TScrollbar", background=Colors.BG_SECONDARY, troughcolor=Colors.BG_DARK,
                       borderwidth=0, arrowcolor=Colors.TEXT_PRIMARY)
        style.configure("TCombobox", fieldbackground=Colors.BG_INPUT, background=Colors.BG_INPUT,
                       foreground=Colors.TEXT_PRIMARY, arrowcolor=Colors.TEXT_PRIMARY,
                       selectbackground=Colors.BG_CARD, selectforeground=Colors.TEXT_PRIMARY)
        style.map("TCombobox", fieldbackground=[("readonly", Colors.BG_INPUT)],
                  foreground=[("readonly", Colors.TEXT_PRIMARY)])

    def _build_layout(self):
        self.header = tk.Frame(self.root, bg=Colors.BG_SECONDARY, height=48)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)

        logo_frame = tk.Frame(self.header, bg=Colors.BG_SECONDARY)
        logo_frame.pack(side=tk.LEFT, padx=15, pady=8)
        tk.Label(logo_frame, text="\u2744", font=("Segoe UI", 16), bg=Colors.BG_SECONDARY,
                fg=Colors.ACCENT_BLUE).pack(side=tk.LEFT)
        tk.Label(logo_frame, text=" LogiFresh", font=("Segoe UI", 14, "bold"),
                bg=Colors.BG_SECONDARY, fg=Colors.TEXT_PRIMARY).pack(side=tk.LEFT)
        tk.Label(logo_frame, text="S.A.", font=("Segoe UI", 10),
                bg=Colors.BG_SECONDARY, fg=Colors.ACCENT_BLUE).pack(side=tk.LEFT, padx=(0,10))
        tk.Label(logo_frame, text="|  Sistema Distribuido de Alimentos Refrigerados",
                font=("Segoe UI", 9), bg=Colors.BG_SECONDARY, fg=Colors.TEXT_MUTED).pack(side=tk.LEFT)

        self.clock_lbl = tk.Label(self.header, text="", bg=Colors.BG_SECONDARY,
                                  fg=Colors.TEXT_SECONDARY, font=("Segoe UI", 9))
        self.clock_lbl.pack(side=tk.RIGHT, padx=15)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self._build_dashboard_tab()
        self._build_pedidos_tab()
        self._build_inventario_tab()
        self._build_facturas_tab()
        self._build_transporte_tab()
        self._build_notificaciones_tab()

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self.status_frame = tk.Frame(self.root, bg=Colors.BG_SECONDARY, height=26)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_frame.pack_propagate(False)

        self.toast_area = tk.Frame(self.root, bg=Colors.BG_DARK)
        self.toast_area.pack(fill=tk.X, side=tk.BOTTOM, before=self.status_frame)

        self.status_lbl = tk.Label(self.status_frame, text="  Listo", bg=Colors.BG_SECONDARY,
                                   fg=Colors.TEXT_SECONDARY, anchor=tk.W,
                                   font=("Segoe UI", 9))
        self.status_lbl.pack(side=tk.LEFT, padx=8)

        self.loading_lbl = tk.Label(self.status_frame, text="", bg=Colors.BG_SECONDARY,
                                    fg=Colors.ACCENT_BLUE, font=("Segoe UI", 9))
        self.loading_lbl.pack(side=tk.RIGHT, padx=8)

        self._update_clock()

    # ============================================================
    # DASHBOARD
    # ============================================================
    def _build_dashboard_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Dashboard  ")

        canvas = tk.Canvas(tab, bg=Colors.BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=Colors.BG_DARK)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        content = tk.Frame(scroll_frame, bg=Colors.BG_DARK)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(content, text="Panel de Control", font=("Segoe UI", 16, "bold"),
                bg=Colors.BG_DARK, fg=Colors.TEXT_PRIMARY).pack(anchor=tk.W)

        tk.Label(content, text="Monitoreo en tiempo real del sistema distribuido",
                font=("Segoe UI", 10), bg=Colors.BG_DARK, fg=Colors.TEXT_MUTED).pack(anchor=tk.W, pady=(2,15))

        # Service status cards
        svc_frame = tk.Frame(content, bg=Colors.BG_DARK)
        svc_frame.pack(fill=tk.X, pady=(0, 15))
        svc_frame.columnconfigure([0,1,2,3,4], weight=1, uniform="svc")

        self.svc_cards = {}
        services_list = list(SERVICE_NAMES.items())
        for i, (key, name) in enumerate(services_list):
            card = tk.Frame(svc_frame, bg=Colors.BG_CARD, highlightthickness=1,
                           highlightbackground=Colors.BORDER)
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            card.columnconfigure(0, weight=1)

            dot = StatusDot(card, size=8)
            dot.pack(anchor=tk.CENTER, pady=(12, 2))

            tk.Label(card, text=name, font=("Segoe UI", 9, "bold"),
                    bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY).pack()
            tk.Label(card, text=f":{SERVICE_PORTS[key]}", font=("Segoe UI", 8),
                    bg=Colors.BG_CARD, fg=Colors.TEXT_MUTED).pack()

            status_lbl = tk.Label(card, text="Verificando...", font=("Segoe UI", 8, "bold"),
                                 bg=Colors.BG_CARD, fg=Colors.ACCENT_YELLOW)
            status_lbl.pack(pady=(2, 10))
            self.svc_cards[key] = {"dot": dot, "status": status_lbl, "frame": card}

        # Stats cards row
        stats_frame = tk.Frame(content, bg=Colors.BG_DARK)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        stats_frame.columnconfigure([0,1,2,3], weight=1, uniform="stat")

        self.card_pedidos = StatCard(stats_frame, "Pedidos Totales")
        self.card_pedidos.grid(row=0, column=0, padx=5, sticky="nsew")

        self.card_facturas = StatCard(stats_frame, "Facturas Emitidas")
        self.card_facturas.grid(row=0, column=1, padx=5, sticky="nsew")

        self.card_transporte = StatCard(stats_frame, "Entregas Programadas")
        self.card_transporte.grid(row=0, column=2, padx=5, sticky="nsew")

        self.card_alertas = StatCard(stats_frame, "Alertas Activas")
        self.card_alertas.grid(row=0, column=3, padx=5, sticky="nsew")

        # Alertas section
        alert_frame = tk.Frame(content, bg=Colors.BG_CARD, highlightthickness=1,
                              highlightbackground=Colors.BORDER)
        alert_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(alert_frame, text="  Alertas y Notificaciones", font=("Segoe UI", 11, "bold"),
                bg=Colors.BG_CARD, fg=Colors.ACCENT_YELLOW, anchor=tk.W).pack(fill=tk.X, padx=12, pady=(10,5))

        self.alerts_text = tk.Text(alert_frame, height=6, bg=Colors.BG_DARK, fg=Colors.TEXT_PRIMARY,
                                   font=("Consolas", 9), relief=tk.FLAT, borderwidth=0,
                                   wrap=tk.WORD, state=tk.DISABLED)
        self.alerts_text.pack(fill=tk.X, padx=12, pady=(0, 10))

        # Servicios info section
        svc_info = tk.Frame(content, bg=Colors.BG_CARD, highlightthickness=1,
                           highlightbackground=Colors.BORDER)
        svc_info.pack(fill=tk.X, pady=(0, 15))

        tk.Label(svc_info, text="  Servicios del Sistema", font=("Segoe UI", 11, "bold"),
                bg=Colors.BG_CARD, fg=Colors.ACCENT_BLUE, anchor=tk.W
                ).pack(fill=tk.X, padx=12, pady=(10, 8))

        svc_descriptions = [
            ("Pedidos", "5001", "Orquestador principal. Registra, consulta y cancela pedidos. Aplica promociones y coordina con todos los demas servicios."),
            ("Inventario", "5002", "Gestiona el stock de 10 productos refrigerados. Valida disponibilidad antes de confirmar pedidos. Puede mostrar inconsistencias simuladas."),
            ("Facturacion", "5003", "Genera facturas automaticas al crear pedidos. Incluye subtotal, descuentos e IGV. Puede generar duplicados ocasionales (bug simulado)."),
            ("Transporte", "5004", "Programa la entrega asignando conductor y vehiculo refrigerado. Gestiona el estado del envio (Pendiente -> Asignado -> En ruta -> Entregado)."),
            ("Notificaciones", "5005", "Envia confirmaciones por email a los clientes tras registrar un pedido. Puede experimentar retrasos en el envio (bug simulado)."),
        ]
        for name, port, desc in svc_descriptions:
            row = tk.Frame(svc_info, bg=Colors.BG_CARD)
            row.pack(fill=tk.X, padx=12, pady=2)
            tk.Label(row, text=f"  {name}", font=("Segoe UI", 9, "bold"),
                    bg=Colors.BG_CARD, fg=Colors.ACCENT_GREEN, width=16, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=f" :{port}", font=("Segoe UI", 9),
                    bg=Colors.BG_CARD, fg=Colors.TEXT_MUTED, width=8, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=desc, font=("Segoe UI", 8),
                    bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY, anchor=tk.W,
                    wraplength=700).pack(side=tk.LEFT, padx=(8, 0))

        self.dashboard_ref = {
            "alerts_text": self.alerts_text,
            "svc_cards": self.svc_cards,
        }

    # ============================================================
    # PEDIDOS TAB
    # ============================================================
    def _build_pedidos_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Pedidos  ")

        paned = tk.PanedWindow(tab, orient=tk.HORIZONTAL, bg=Colors.BORDER, sashwidth=1)
        paned.pack(fill=tk.BOTH, expand=True)

        form_frame = tk.Frame(paned, bg=Colors.BG_DARK)
        paned.add(form_frame, width=380, minsize=320)

        list_frame = tk.Frame(paned, bg=Colors.BG_DARK)
        paned.add(list_frame, width=700, minsize=400)

        self._build_pedido_form(form_frame)
        self._build_pedido_list(list_frame)

    def _build_pedido_form(self, parent):
        header = tk.Frame(parent, bg=Colors.BG_CARD, height=44)
        header.pack(fill=tk.X, padx=8, pady=(8, 0))
        header.pack_propagate(False)
        tk.Label(header, text="  Nuevo Pedido", font=("Segoe UI", 12, "bold"),
                bg=Colors.BG_CARD, fg=Colors.ACCENT_BLUE).pack(side=tk.LEFT, padx=8, pady=10)

        form = tk.Frame(parent, bg=Colors.BG_CARD)
        form.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        sections = [
            ("Datos del Cliente", [
                ("cliente", "Nombre/Razon Social:", "Supermercado El Sol",
                 [Validators.required, lambda v: (len(v) <= 80, "Maximo 80 caracteres") if v else (True,"")]),
                ("email", "Email:", "contacto@cliente.pe",
                 [Validators.required, Validators.email]),
                ("direccion", "Direccion:", "Av. Principal 123, Distrito",
                 [Validators.required, lambda v: (len(v) <= 120, "Maximo 120 caracteres") if v else (True,"")]),
            ]),
            ("Datos del Producto", [
                ("producto_id", "ID Producto:", "P001",
                 [Validators.required, Validators.product_id]),
                ("cantidad", "Cantidad:", "1",
                 [lambda v: Validators.positive_integer(v, "Cantidad")]),
            ]),
            ("Promocion", [
                ("promocion", "Codigo:", "SIN_PROMOCION", None),
            ]),
        ]

        self.form_entries = {}
        pad_y = 12

        for section_title, fields in sections:
            sep = tk.Frame(form, bg=Colors.BORDER, height=1)
            sep.pack(fill=tk.X, padx=12, pady=(8, 0))

            tk.Label(form, text=section_title, font=("Segoe UI", 9, "bold"),
                    bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY, anchor=tk.W
                    ).pack(fill=tk.X, padx=16, pady=(6, 4))

            for name, label_text, placeholder, validators in fields:
                row = tk.Frame(form, bg=Colors.BG_CARD)
                row.pack(fill=tk.X, padx=16, pady=2)

                if name == "promocion":
                    tk.Label(row, text=label_text, bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY,
                            font=("Segoe UI", 10), width=14, anchor=tk.W).pack(side=tk.LEFT)
                    combo = ttk.Combobox(row, values=["SIN_PROMOCION", "DESC10", "DESC20", "FRESCURA"],
                                        state="readonly", width=20, font=("Segoe UI", 10))
                    combo.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
                    combo.current(0)
                    self.form_entries[name] = combo

                    info_frame = tk.Frame(form, bg=Colors.BG_CARD)
                    info_frame.pack(fill=tk.X, padx=16, pady=(2, 4))
                    tk.Label(info_frame, text="  DESC10: 10%  |  DESC20: 20%  |  FRESCURA: 15%",
                            bg=Colors.BG_CARD, fg=Colors.TEXT_MUTED,
                            font=("Segoe UI", 8, "italic")).pack(anchor=tk.W)
                else:
                    entry = ValidatedEntry(row, label=label_text, placeholder=placeholder,
                                          validator=validators)
                    entry.pack(fill=tk.X, expand=True)
                    if validators:
                        entry.pack_error()
                    self.form_entries[name] = entry

        btn_frame = tk.Frame(form, bg=Colors.BG_CARD)
        btn_frame.pack(fill=tk.X, padx=16, pady=(16, 12))

        self.btn_crear = tk.Button(btn_frame, text="Crear Pedido",
                                   command=self._crear_pedido_action,
                                   font=("Segoe UI", 11, "bold"),
                                   bg=Colors.ACCENT_GREEN, fg="#000000",
                                   activebackground="#2ea043", activeforeground="#000000",
                                   relief=tk.FLAT, cursor="hand2",
                                   padx=30, pady=8, borderwidth=0)
        self.btn_crear.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_limpiar = tk.Button(btn_frame, text="Limpiar Formulario",
                                    command=self._limpiar_formulario,
                                    font=("Segoe UI", 10),
                                    bg=Colors.BG_SECONDARY, fg=Colors.TEXT_PRIMARY,
                                    activebackground=Colors.BG_CARD,
                                    relief=tk.FLAT, cursor="hand2",
                                    padx=16, pady=8, borderwidth=0)
        self.btn_limpiar.pack(side=tk.LEFT)

        # Info panel: explica los servicios involucrados
        info_frame = tk.Frame(form, bg=Colors.INFO_BG, highlightthickness=1,
                              highlightbackground=Colors.BORDER)
        info_frame.pack(fill=tk.X, padx=16, pady=(0, 12))

        tk.Label(info_frame, text="  Al crear un pedido, el sistema automaticamente:",
                font=("Segoe UI", 9, "bold"), bg=Colors.INFO_BG,
                fg=Colors.ACCENT_BLUE, anchor=tk.W
                ).pack(fill=tk.X, padx=8, pady=(6, 2))

        steps = [
            ("1", "Inventario", "Verifica stock y precios del producto"),
            ("2", "Facturacion", "Genera factura automatica con IGV"),
            ("3", "Transporte", "Programa envio con conductor y vehiculo"),
            ("4", "Notificaciones", "Envia confirmacion por email al cliente"),
        ]
        for num, svc, desc in steps:
            row = tk.Frame(info_frame, bg=Colors.INFO_BG)
            row.pack(fill=tk.X, padx=12, pady=1)
            tk.Label(row, text=f"  {num}.", font=("Segoe UI", 8, "bold"),
                    bg=Colors.INFO_BG, fg=Colors.ACCENT_GREEN, width=3, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=f"{svc}:", font=("Segoe UI", 8, "bold"),
                    bg=Colors.INFO_BG, fg=Colors.TEXT_PRIMARY, width=18, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=desc, font=("Segoe UI", 8),
                    bg=Colors.INFO_BG, fg=Colors.TEXT_SECONDARY, anchor=tk.W).pack(side=tk.LEFT)

        self.pedidos_ref = {
            "form_entries": self.form_entries,
            "btn_crear": self.btn_crear,
        }

    def _build_pedido_list(self, parent):
        header = tk.Frame(parent, bg=Colors.BG_CARD, height=44)
        header.pack(fill=tk.X, padx=8, pady=(8, 0))
        header.pack_propagate(False)

        tk.Label(header, text="  Pedidos Registrados", font=("Segoe UI", 12, "bold"),
                bg=Colors.BG_CARD, fg=Colors.ACCENT_BLUE).pack(side=tk.LEFT, padx=8, pady=10)

        btn_cancel = tk.Button(header, text="Cancelar Seleccionado",
                              command=self._cancelar_pedido_action,
                              font=("Segoe UI", 9), bg=Colors.ACCENT_RED, fg="#ffffff",
                              relief=tk.FLAT, cursor="hand2", padx=12, pady=4, borderwidth=0,
                              activebackground="#da3633")
        btn_cancel.pack(side=tk.RIGHT, padx=8, pady=8)

        btn_refresh = tk.Button(header, text="Actualizar",
                               command=self._actualizar_pedidos,
                               font=("Segoe UI", 9), bg=Colors.BG_SECONDARY, fg=Colors.TEXT_PRIMARY,
                               relief=tk.FLAT, cursor="hand2", padx=12, pady=4, borderwidth=0)
        btn_refresh.pack(side=tk.RIGHT, padx=2, pady=8)

        tree_frame = tk.Frame(parent, bg=Colors.BG_CARD)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        cols = ("ID", "Cliente", "Productos", "Subtotal", "Desc.", "Total", "Promo", "Estado", "Notif")
        self.tree_pedidos = ttk.Treeview(tree_frame, columns=cols, show="headings", height=18)
        widths = [90, 140, 100, 75, 65, 75, 70, 95, 55]
        for col, w in zip(cols, widths):
            self.tree_pedidos.heading(col, text=col)
            self.tree_pedidos.column(col, width=w, minwidth=w)

        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_pedidos.yview)
        scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree_pedidos.xview)
        self.tree_pedidos.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree_pedidos.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree_pedidos.tag_configure("cancelado", foreground=Colors.ACCENT_RED)
        self.tree_pedidos.tag_configure("success", foreground=Colors.ACCENT_GREEN)

        self.pedidos_list_ref = {"tree": self.tree_pedidos}

    # ============================================================
    # INVENTARIO TAB
    # ============================================================
    def _build_inventario_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Inventario  ")

        header = tk.Frame(tab, bg=Colors.BG_CARD, height=44)
        header.pack(fill=tk.X, padx=8, pady=(8, 0))
        header.pack_propagate(False)
        tk.Label(header, text="  Inventario de Productos Refrigerados", font=("Segoe UI", 12, "bold"),
                bg=Colors.BG_CARD, fg=Colors.ACCENT_BLUE).pack(side=tk.LEFT, padx=8, pady=10)

        tk.Label(header, text="Actualizacion automatica cada 5s  |  * Puede mostrar inconsistencias simuladas  ",
                font=("Segoe UI", 8, "italic"), bg=Colors.BG_CARD, fg=Colors.ACCENT_YELLOW
                ).pack(side=tk.RIGHT, padx=8)

        tree_frame = tk.Frame(tab, bg=Colors.BG_CARD)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        cols = ("ID", "Producto", "Stock", "Precio Unit.", "Estado")
        self.tree_inventario = ttk.Treeview(tree_frame, columns=cols, show="headings", height=18)
        widths = [70, 300, 80, 100, 100]
        for col, w in zip(cols, widths):
            self.tree_inventario.heading(col, text=col)
            self.tree_inventario.column(col, width=w, minwidth=w)
        self.tree_inventario.pack(fill=tk.BOTH, expand=True)

        self.tree_inventario.tag_configure("low_stock", foreground=Colors.ACCENT_RED)
        self.tree_inventario.tag_configure("ok_stock", foreground=Colors.ACCENT_GREEN)
        self.tree_inventario.tag_configure("inconsistent", foreground=Colors.ACCENT_YELLOW)

    # ============================================================
    # FACTURAS TAB
    # ============================================================
    def _build_facturas_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Facturacion  ")

        header = tk.Frame(tab, bg=Colors.BG_CARD, height=44)
        header.pack(fill=tk.X, padx=8, pady=(8, 0))
        header.pack_propagate(False)
        tk.Label(header, text="  Facturas Emitidas", font=("Segoe UI", 12, "bold"),
                bg=Colors.BG_CARD, fg=Colors.ACCENT_BLUE).pack(side=tk.LEFT, padx=8, pady=10)

        tree_frame = tk.Frame(tab, bg=Colors.BG_CARD)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        cols = ("ID", "Pedido", "Cliente", "Subtotal", "Desc.", "Total", "Estado")
        self.tree_facturas = ttk.Treeview(tree_frame, columns=cols, show="headings", height=18)
        widths = [110, 100, 150, 80, 70, 80, 120]
        for col, w in zip(cols, widths):
            self.tree_facturas.heading(col, text=col)
            self.tree_facturas.column(col, width=w, minwidth=w)
        self.tree_facturas.pack(fill=tk.BOTH, expand=True)
        self.tree_facturas.tag_configure("duplicada", foreground=Colors.ACCENT_RED)
        self.tree_facturas.tag_configure("normal", foreground=Colors.ACCENT_GREEN)

    # ============================================================
    # TRANSPORTE TAB
    # ============================================================
    def _build_transporte_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Transporte  ")

        header = tk.Frame(tab, bg=Colors.BG_CARD, height=44)
        header.pack(fill=tk.X, padx=8, pady=(8, 0))
        header.pack_propagate(False)
        tk.Label(header, text="  Entregas Programadas", font=("Segoe UI", 12, "bold"),
                bg=Colors.BG_CARD, fg=Colors.ACCENT_BLUE).pack(side=tk.LEFT, padx=8, pady=10)

        tree_frame = tk.Frame(tab, bg=Colors.BG_CARD)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        cols = ("ID", "Pedido", "Cliente", "Destino", "Estado", "Conductor", "Vehiculo")
        self.tree_transporte = ttk.Treeview(tree_frame, columns=cols, show="headings", height=18)
        widths = [100, 100, 140, 200, 100, 120, 120]
        for col, w in zip(cols, widths):
            self.tree_transporte.heading(col, text=col)
            self.tree_transporte.column(col, width=w, minwidth=w)
        self.tree_transporte.pack(fill=tk.BOTH, expand=True)
        self.tree_transporte.tag_configure("pendiente", foreground=Colors.ACCENT_YELLOW)
        self.tree_transporte.tag_configure("en_ruta", foreground=Colors.ACCENT_BLUE)
        self.tree_transporte.tag_configure("entregado", foreground=Colors.ACCENT_GREEN)
        self.tree_transporte.tag_configure("cancelado", foreground=Colors.ACCENT_RED)

    # ============================================================
    # NOTIFICACIONES TAB
    # ============================================================
    def _build_notificaciones_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Notificaciones  ")

        header = tk.Frame(tab, bg=Colors.BG_CARD, height=44)
        header.pack(fill=tk.X, padx=8, pady=(8, 0))
        header.pack_propagate(False)
        tk.Label(header, text="  Notificaciones Enviadas", font=("Segoe UI", 12, "bold"),
                bg=Colors.BG_CARD, fg=Colors.ACCENT_BLUE).pack(side=tk.LEFT, padx=8, pady=10)

        tree_frame = tk.Frame(tab, bg=Colors.BG_CARD)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        cols = ("ID", "Pedido", "Cliente", "Email", "Tipo", "Enviado", "Retraso")
        self.tree_notificaciones = ttk.Treeview(tree_frame, columns=cols, show="headings", height=18)
        widths = [110, 100, 140, 180, 60, 70, 80]
        for col, w in zip(cols, widths):
            self.tree_notificaciones.heading(col, text=col)
            self.tree_notificaciones.column(col, width=w, minwidth=w)
        self.tree_notificaciones.pack(fill=tk.BOTH, expand=True)
        self.tree_notificaciones.tag_configure("retrasada", foreground=Colors.ACCENT_YELLOW)
        self.tree_notificaciones.tag_configure("ok", foreground=Colors.ACCENT_GREEN)

    # ============================================================
    # LOGICA DE PEDIDOS
    # ============================================================
    def _crear_pedido_action(self):
        if not self._validar_formulario():
            return

        cliente = self.form_entries["cliente"].get()
        email = self.form_entries["email"].get()
        direccion = self.form_entries["direccion"].get()
        producto_id = self.form_entries["producto_id"].get().strip().upper()
        cantidad = int(self.form_entries["cantidad"].get())
        promo = self.form_entries["promocion"].get()
        if promo == "SIN_PROMOCION":
            promo = ""

        self._set_loading(True, "Procesando pedido...")
        self.btn_crear.config(state=tk.DISABLED)

        data = {
            "cliente": cliente,
            "email": email,
            "direccion": direccion,
            "productos": [{"producto_id": producto_id, "cantidad": cantidad}],
            "codigo_promocion": promo
        }

        def do_create():
            result = self._api_post("pedidos", "/pedido", data)
            self.root.after(0, lambda: self._handle_pedido_result(result))

        threading.Thread(target=do_create, daemon=True).start()

    def _validar_formulario(self):
        errors = []
        fields_with_errors = []

        cliente = self.form_entries["cliente"].get()
        email = self.form_entries["email"].get()
        direccion = self.form_entries["direccion"].get()
        producto_id = self.form_entries["producto_id"].get().strip().upper()
        cantidad = self.form_entries["cantidad"].get()

        for key in ["cliente", "email", "direccion", "producto_id", "cantidad"]:
            self.form_entries[key].validate()

        if not cliente or cliente == "Supermercado El Sol":
            errors.append("Nombre del cliente: campo obligatorio")
            fields_with_errors.append("CLIENTE")
        elif len(cliente) > 80:
            errors.append("Nombre del cliente: maximo 80 caracteres")

        if not email or email == "contacto@cliente.pe":
            errors.append("Email: campo obligatorio")
            fields_with_errors.append("EMAIL")
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append("Email: formato invalido (ej: usuario@dominio.com)")

        if not direccion or direccion == "Av. Principal 123, Distrito":
            errors.append("Direccion de entrega: campo obligatorio")
            fields_with_errors.append("DIRECCION")

        if not producto_id:
            errors.append("ID del producto: campo obligatorio")
            fields_with_errors.append("PRODUCTO")
        elif not re.match(r'^P\d{3}$', producto_id):
            errors.append("ID del producto: formato invalido. Use P001, P002, etc.")

        try:
            cant = int(cantidad)
            if cant <= 0:
                errors.append("Cantidad: debe ser un numero mayor a 0")
                fields_with_errors.append("CANTIDAD")
            elif cant > 500:
                errors.append("Cantidad: maximo 500 unidades por pedido")
                fields_with_errors.append("CANTIDAD")
        except (ValueError, TypeError):
            errors.append("Cantidad: debe ser un numero entero valido")
            fields_with_errors.append("CANTIDAD")

        if errors:
            error_msg = "No se puede crear el pedido:\n\n" + "\n".join(f"  \u2022 {e}" for e in errors)
            messagebox.showwarning("Validacion de Pedido", error_msg)
            self._set_status(f"Corrija {len(errors)} error(es) en el formulario")
            return False
        return True

    def _handle_pedido_result(self, result):
        self._set_loading(False)
        self.btn_crear.config(state=tk.NORMAL)

        if not result:
            self._show_toast("Servicio no disponible. Verifique que los servicios esten corriendo.", "error")
            return

        if "error" in result:
            self._show_toast(f"Error: {result['error']}", "error")
            self._set_status(f"Error: {result['error']}")
            return

        pedido_id = result.get("pedido_id", "?")
        total = result.get("total", 0)
        msg_desc = result.get("mensaje_descuento", "")
        notif = result.get("notificacion_enviada", False)

        notification_msg = "Notificacion enviada" if notif else "Notificacion con retraso"

        cols = ("ID", "Cliente", "Productos", "Subtotal", "Desc.", "Total", "Promo", "Estado", "Notif")
        productos_str = ", ".join(f"{p.get('producto_id','?')}x{p.get('cantidad',0)}"
                                  for p in result.get("productos", []))
        self.tree_pedidos.insert("", 0, values=(
            pedido_id,
            result.get("cliente", "")[:30],
            productos_str[:20],
            f"S/. {result.get('subtotal', 0):.2f}",
            f"S/. {result.get('descuento', 0):.2f}",
            f"S/. {total:.2f}",
            result.get("promocion") or "Ninguna",
            result.get("estado", ""),
            "Si" if notif else "No"
        ), tags=("success",))

        self._set_status(f"Pedido {pedido_id} creado - Total: S/. {total:.2f}")

        alertas = []
        for p in result.get("productos", []):
            if p.get("_alerta_inventario"):
                alertas.append(p["_alerta_inventario"])
        if not notif:
            alertas.append("Notificacion con retraso (bug simulado)")
        if not result.get("factura_id"):
            alertas.append("Factura no generada")
        if not result.get("transporte_id"):
            alertas.append("Transporte no asignado")

        if alertas:
            self._show_toast(" | ".join(alertas), "warning")

        mensaje = f"Pedido #{pedido_id} registrado. {msg_desc}. Total: S/. {total:.2f}. {notification_msg}."
        self._show_toast(mensaje, "success")

    def _cancelar_pedido_action(self):
        selected = self.tree_pedidos.selection()
        if not selected:
            self._show_toast("Seleccione un pedido de la lista para cancelar", "warning")
            return
        pedido_id = self.tree_pedidos.item(selected[0])["values"][0]
        estado = self.tree_pedidos.item(selected[0])["values"][7]
        if estado == "CANCELADO":
            self._show_toast("El pedido ya esta cancelado", "warning")
            return

        if messagebox.askyesno("Confirmar Cancelacion",
                               f"Esta seguro de cancelar el pedido {pedido_id}?\n\n"
                               "Se liberara el inventario y se cancelara el transporte asociado.",
                               parent=self.root):
            result = self._api_post("pedidos", f"/pedido/{pedido_id}/cancelar", {})
            if result and "error" not in result:
                self._actualizar_pedidos()
                self._show_toast(f"Pedido {pedido_id} cancelado correctamente", "success")
            else:
                self._show_toast(f"No se pudo cancelar el pedido {pedido_id}", "error")

    def _limpiar_formulario(self):
        self.form_entries["cliente"].set("")
        self.form_entries["email"].set("")
        self.form_entries["direccion"].set("")
        self.form_entries["producto_id"].set("P001")
        self.form_entries["cantidad"].set("1")
        self.form_entries["promocion"].current(0)
        for entry in [self.form_entries["cliente"], self.form_entries["email"],
                      self.form_entries["direccion"], self.form_entries["producto_id"],
                      self.form_entries["cantidad"]]:
            entry.clear_error()

    def _on_enter_key(self):
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 1:
            self._crear_pedido_action()

    def _on_escape_key(self):
        self._limpiar_formulario()

    # ============================================================
    # REFRESH / API
    # ============================================================
    _BASE_PORT = 5001
    _URLS = {}

    def _get_url(self, service, endpoint):
        return f"http://127.0.0.1:{SERVICE_PORTS[service]}{endpoint}"

    def _api_get(self, service, endpoint):
        try:
            r = requests.get(self._get_url(service, endpoint), timeout=8)
            return r.json() if r.status_code == 200 else None
        except:
            return None

    def _api_post(self, service, endpoint, data):
        try:
            r = requests.post(self._get_url(service, endpoint), json=data, timeout=25)
            return r.json() if r.status_code in (200, 201) else {"error": f"HTTP {r.status_code}"}
        except requests.exceptions.Timeout:
            return {"error": "Timeout: el servicio no respondio a tiempo"}
        except requests.exceptions.ConnectionError:
            return {"error": "Servicio no disponible"}
        except Exception as e:
            return {"error": str(e)}

    def _start_refresh_cycle(self):
        self._refresh_all()
        self.root.after(4000, self._start_refresh_cycle)

    def _refresh_all(self):
        threading.Thread(target=self._refresh_services_status, daemon=True).start()
        self._actualizar_pedidos()
        self._actualizar_inventario()
        self._actualizar_facturas()
        self._actualizar_transporte()
        self._actualizar_notificaciones()
        self._actualizar_dashboard()

    def _refresh_services_status(self):
        for name in SERVICE_NAMES:
            try:
                r = requests.get(f"http://127.0.0.1:{SERVICE_PORTS[name]}/health", timeout=2)
                status = Status.ONLINE if r.status_code == 200 else Status.DEGRADED
            except:
                status = Status.OFFLINE

            card = self.svc_cards[name]
            if status == Status.ONLINE:
                card["dot"].set_color(Colors.ACCENT_GREEN)
                card["status"].config(text="ONLINE", fg=Colors.ACCENT_GREEN)
                card["frame"].config(highlightbackground=Colors.ACCENT_GREEN)
            elif status == Status.DEGRADED:
                card["dot"].set_color(Colors.ACCENT_YELLOW)
                card["status"].config(text="DEGRADADO", fg=Colors.ACCENT_YELLOW)
                card["frame"].config(highlightbackground=Colors.ACCENT_YELLOW)
            else:
                card["dot"].set_color(Colors.ACCENT_RED)
                card["status"].config(text="OFFLINE", fg=Colors.ACCENT_RED)
                card["frame"].config(highlightbackground=Colors.ACCENT_RED)

    def _actualizar_dashboard(self):
        try:
            pedidos = self._api_get("pedidos", "/pedidos")
            facturas = self._api_get("facturacion", "/facturas")
            transportes = self._api_get("transporte", "/transportes")

            if pedidos is not None:
                self.card_pedidos.set_value(len(pedidos))
            if facturas is not None:
                self.card_facturas.set_value(len(facturas))
                dups = len([f for f in facturas if f.get("_duplicada")])
            if transportes is not None:
                self.card_transporte.set_value(len(transportes))

            alert_count = 0
            alerts = []
            if facturas:
                dups = [f for f in facturas if f.get("_duplicada")]
                alert_count += len(dups)
                if dups:
                    alerts.append(f"{len(dups)} factura(s) duplicada(s) detectada(s)")

            if pedidos:
                sin_notif = [p for p in pedidos if not p.get("notificacion_enviada")]
                alert_count += len(sin_notif)
                if sin_notif:
                    alerts.append(f"{len(sin_notif)} pedido(s) con notificacion pendiente")

                sin_factura = [p for p in pedidos if not p.get("factura_id")]
                alert_count += len(sin_factura)
                if sin_factura:
                    alerts.append(f"{len(sin_factura)} pedido(s) sin factura generada")

            self.card_alertas.set_value(alert_count)
            if alert_count > 0:
                self.card_alertas.value_lbl.config(fg=Colors.ACCENT_RED)
            else:
                self.card_alertas.value_lbl.config(fg=Colors.ACCENT_GREEN)

            self.alerts_text.config(state=tk.NORMAL)
            self.alerts_text.delete(1.0, tk.END)
            if alerts:
                for a in alerts:
                    self.alerts_text.insert(tk.END, f"  [!] {a}\n")
            else:
                self.alerts_text.insert(tk.END, "  No se detectaron alertas.\n")
            self.alerts_text.config(state=tk.DISABLED)

        except Exception as e:
            pass

    def _actualizar_pedidos(self):
        result = self._api_get("pedidos", "/pedidos")
        if not result:
            return
        self.tree_pedidos.delete(*self.tree_pedidos.get_children())
        for p in reversed(result):
            productos_str = ", ".join(f"{i.get('producto_id','?')}x{i.get('cantidad',0)}"
                                      for i in p.get("productos", []))
            ntf = "Si" if p.get("notificacion_enviada") else "No"
            tag = "cancelado" if p.get("estado") == "CANCELADO" else "success"
            self.tree_pedidos.insert("", 0, values=(
                p["pedido_id"], p.get("cliente","")[:30], productos_str[:20],
                f"S/. {p.get('subtotal',0):.2f}", f"S/. {p.get('descuento',0):.2f}",
                f"S/. {p.get('total',0):.2f}", p.get("promocion") or "Ninguna",
                p.get("estado",""), ntf
            ), tags=(tag,))

    def _actualizar_inventario(self):
        result = self._api_get("inventario", "/inventario")
        if not result:
            return
        self.tree_inventario.delete(*self.tree_inventario.get_children())
        for pid, prod in result.items():
            stock = prod["stock"]
            tag = "low_stock" if stock < 30 else "ok_stock"
            estado = "STOCK BAJO" if stock < 30 else ("INCONSISTENTE" if prod.get("_inconsistente") else "DISPONIBLE")
            self.tree_inventario.insert("", tk.END, values=(
                pid, prod["nombre"], stock, f"S/. {prod['precio']:.2f}", estado
            ), tags=(tag,))

    def _actualizar_facturas(self):
        result = self._api_get("facturacion", "/facturas")
        if not result:
            return
        self.tree_facturas.delete(*self.tree_facturas.get_children())
        for f in reversed(result):
            dup = f.get("_duplicada", False)
            estado = "DUPLICADA" if dup else f.get("estado", "EMITIDA")
            tag = "duplicada" if dup else "normal"
            self.tree_facturas.insert("", 0, values=(
                f.get("factura_id",""), f.get("pedido_id",""), f.get("cliente","")[:30],
                f"S/. {f.get('subtotal',0):.2f}", f"S/. {f.get('descuento',0):.2f}",
                f"S/. {f.get('total',0):.2f}", estado
            ), tags=(tag,))

    def _actualizar_transporte(self):
        result = self._api_get("transporte", "/transportes")
        if not result:
            return
        self.tree_transporte.delete(*self.tree_transporte.get_children())
        for t in reversed(result):
            estado = t.get("estado", "PENDIENTE")
            tag_map = {"PENDIENTE":"pendiente", "ASIGNADO":"en_ruta", "EN_RUTA":"en_ruta",
                      "ENTREGADO":"entregado", "CANCELADO":"cancelado"}
            tag = tag_map.get(estado, "pendiente")
            self.tree_transporte.insert("", 0, values=(
                t.get("transporte_id",""), t.get("pedido_id",""), t.get("cliente","")[:30],
                t.get("destino","")[:40], estado,
                t.get("conductor") or "No asignado",
                t.get("vehiculo") or "No asignado"
            ), tags=(tag,))

    def _actualizar_notificaciones(self):
        result = self._api_get("notificaciones", "/notificaciones")
        if not result:
            return
        self.tree_notificaciones.delete(*self.tree_notificaciones.get_children())
        for n in reversed(result):
            enviado = "Si" if n.get("enviado") else "No"
            retraso = f"{n.get('retraso_segundos', 0)}s" if n.get("retraso_segundos", 0) > 0 else "-"
            tag = "retrasada" if n.get("retraso_segundos", 0) > 0 else "ok"
            self.tree_notificaciones.insert("", 0, values=(
                n.get("notificacion_id",""), n.get("pedido_id",""), n.get("cliente","")[:30],
                n.get("email","")[:35], n.get("tipo","EMAIL"), enviado, retraso
            ), tags=(tag,))

    # ============================================================
    # TOAST / STATUS
    # ============================================================
    def _show_toast(self, message, level="info"):
        self.toast_queue.put((message, level))
        self.root.after(100, self._process_toasts)

    def _process_toasts(self):
        while not self.toast_queue.empty():
            msg, level = self.toast_queue.get()
            colors_map = {
                "success": (Colors.SUCCESS_BG, Colors.ACCENT_GREEN),
                "error": (Colors.ERROR_BG, Colors.ACCENT_RED),
                "warning": (Colors.WARNING_BG, Colors.ACCENT_YELLOW),
                "info": (Colors.INFO_BG, Colors.ACCENT_BLUE),
            }
            bg, fg = colors_map.get(level, (Colors.INFO_BG, Colors.ACCENT_BLUE))

            toast = tk.Frame(self.toast_area, bg=bg, highlightthickness=0)
            toast.pack(fill=tk.X, padx=8, pady=1)

            tk.Label(toast, text=f"  {msg}", bg=bg, fg=fg, font=("Segoe UI", 9),
                    anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, padx=8, pady=4)

            close_btn = tk.Label(toast, text="X", bg=bg, fg=fg, font=("Segoe UI", 9, "bold"),
                                cursor="hand2")
            close_btn.pack(side=tk.RIGHT, padx=8)
            close_btn.bind("<Button-1>", lambda e, t=toast: t.destroy())

            self.root.after(6000, toast.destroy)

    def _set_status(self, msg):
        self.status_lbl.config(text=f"  {msg}")

    def _set_loading(self, loading, msg=""):
        if loading:
            dots = [".", "..", "..."]
            self._loading_dots = 0

            def animate():
                if hasattr(self, '_loading_active') and self._loading_active:
                    self._loading_dots = (self._loading_dots + 1) % 3
                    self.loading_lbl.config(text=f"{msg}{dots[self._loading_dots]}")
                    self.root.after(400, animate)

            self._loading_active = True
            animate()
        else:
            self._loading_active = False
            self.loading_lbl.config(text="")

    def _update_clock(self):
        now = datetime.now().strftime("%H:%M:%S  |  %d/%m/%Y")
        self.clock_lbl.config(text=now)
        self.root.after(1000, self._update_clock)

    def _on_tab_changed(self, event):
        tab_idx = self.notebook.index(self.notebook.select())
        self._set_status(f"Pestana: {['Dashboard','Pedidos','Inventario','Facturacion','Transporte','Notificaciones'][tab_idx]}")

    def _on_close(self):
        if messagebox.askyesno("Salir", "Cerrar la interfaz grafica de LogiFresh S.A.?"):
            self.root.destroy()


def main():
    root = tk.Tk()
    app = LogiFreshApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
