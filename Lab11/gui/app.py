"""
Interfaz Grafica - Logi Market Peru S.A.C.
Panel de Administracion de Seguridad para Sistema Distribuido

Proposito: Demostrar de forma interactiva todas las actividades del Lab11:
  - Matriz de Riesgos (Actividad 1)
  - Autenticacion Segura con MFA y RBAC (Actividad 2)
  - Comunicaciones Cifradas TLS (Actividad 3)
  - Proteccion de APIs con JWT + Rate Limiting (Actividad 4)
  - Sistema de Auditoria y Monitoreo (Actividad 5)

Conexion: Se comunica con el API Gateway seguro en https://localhost:8443
"""
import json
import threading
import time
import re
from datetime import datetime
from tkinter import Tk, Toplevel, Frame, Label, Button, Entry, Text, Scrollbar
from tkinter import ttk, messagebox, scrolledtext
from tkinter import Canvas, WORD, END, NSEW, EW, W, E, N, S, CENTER, LEFT, RIGHT

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =============================================================================
# Constantes
# =============================================================================

API_BASE = "https://localhost:8443"
CERT_DIR = "certs"
LOG_DIR = "logs"


class Colors:
    BG_DARK = "#0d1117"
    BG_MEDIUM = "#161b22"
    BG_LIGHT = "#21262d"
    BORDER = "#30363d"
    TEXT_PRIMARY = "#e6edf3"
    TEXT_SECONDARY = "#8b949e"
    TEXT_MUTED = "#6e7681"
    ACCENT_BLUE = "#58a6ff"
    ACCENT_GREEN = "#3fb950"
    ACCENT_RED = "#f85149"
    ACCENT_ORANGE = "#d2991d"
    ACCENT_PURPLE = "#a371f7"
    SUCCESS_BG = "#0d3320"
    ERROR_BG = "#3d1214"
    WARNING_BG = "#3d2e0a"
    INFO_BG = "#0d2137"


class RiskLevel:
    CRITICO = "Critico"
    ALTO = "Alto"
    MEDIO = "Medio"
    BAJO = "Bajo"


# =============================================================================
# GUI Principal
# =============================================================================

class LogiMarketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Logi Market Peru S.A.C. - Panel de Seguridad")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)
        self.root.configure(bg=Colors.BG_DARK)

        self.access_token = None
        self.token_type = None
        self.usuario_actual = None
        self.rol_actual = None

        self._setup_styles()
        self._build_ui()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=Colors.BG_DARK)
        style.configure("TLabel", background=Colors.BG_DARK, foreground=Colors.TEXT_PRIMARY)
        style.configure("TButton",
                        background=Colors.BG_LIGHT, foreground=Colors.TEXT_PRIMARY,
                        borderwidth=0, relief="flat", padding=(12, 6))
        style.map("TButton",
                  background=[("active", Colors.BORDER), ("!active", Colors.BG_LIGHT)])
        style.configure("Accent.TButton",
                        background=Colors.ACCENT_GREEN, foreground="#000000",
                        borderwidth=0, relief="flat", padding=(12, 8))
        style.map("Accent.TButton",
                  background=[("active", "#2ea043"), ("!active", Colors.ACCENT_GREEN)])
        style.configure("Danger.TButton",
                        background=Colors.ACCENT_RED, foreground="#ffffff",
                        borderwidth=0, relief="flat", padding=(12, 8))
        style.configure("TNotebook", background=Colors.BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=Colors.BG_MEDIUM, foreground=Colors.TEXT_SECONDARY,
                        padding=(18, 8), borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", Colors.BG_LIGHT)],
                  foreground=[("selected", Colors.TEXT_PRIMARY)])
        style.configure("Treeview",
                        background=Colors.BG_MEDIUM, foreground=Colors.TEXT_PRIMARY,
                        fieldbackground=Colors.BG_MEDIUM, borderwidth=0)
        style.configure("Treeview.Heading",
                        background=Colors.BG_LIGHT, foreground=Colors.TEXT_PRIMARY,
                        borderwidth=0, relief="flat")
        style.map("Treeview.Heading",
                  background=[("active", Colors.BORDER)])
        style.configure("TEntry",
                        fieldbackground=Colors.BG_LIGHT, foreground=Colors.TEXT_PRIMARY,
                        borderwidth=1, relief="solid")

    def _build_ui(self):
        # Barra superior
        top_bar = Frame(self.root, bg=Colors.BG_MEDIUM, height=50)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        title_lbl = Label(top_bar, text="Logi Market Peru S.A.C.",
                          font=("Segoe UI", 14, "bold"),
                          bg=Colors.BG_MEDIUM, fg=Colors.ACCENT_BLUE)
        title_lbl.pack(side="left", padx=16, pady=10)

        subtitle_lbl = Label(top_bar, text="Panel de Administracion de Seguridad | Arquitectura de Microservicios",
                             font=("Segoe UI", 9),
                             bg=Colors.BG_MEDIUM, fg=Colors.TEXT_SECONDARY)
        subtitle_lbl.pack(side="left", padx=8, pady=10)

        # Indicador de sesion
        self.session_frame = Frame(top_bar, bg=Colors.BG_MEDIUM)
        self.session_frame.pack(side="right", padx=16)
        self.session_dot = Canvas(self.session_frame, width=12, height=12,
                                   bg=Colors.BG_MEDIUM, highlightthickness=0)
        self.session_dot.pack(side="left", padx=4)
        self.session_oval = self.session_dot.create_oval(2, 2, 10, 10,
                                                          fill=Colors.TEXT_MUTED, outline="")
        self.session_label = Label(self.session_frame, text="No autenticado",
                                    font=("Segoe UI", 9),
                                    bg=Colors.BG_MEDIUM, fg=Colors.TEXT_MUTED)
        self.session_label.pack(side="left", padx=2)

        # Notebook (pestanas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)

        self._build_dashboard_tab()
        self._build_auth_tab()
        self._build_inventario_tab()
        self._build_pagos_tab()
        self._build_logistica_tab()
        self._build_auditoria_tab()
        self._build_seguridad_tab()

        # Barra inferior
        bottom_bar = Frame(self.root, bg=Colors.BG_MEDIUM, height=28)
        bottom_bar.pack(fill="x", side="bottom")
        bottom_bar.pack_propagate(False)
        self.status_lbl = Label(bottom_bar, text="Listo | API: https://localhost:8443",
                                font=("Segoe UI", 8),
                                bg=Colors.BG_MEDIUM, fg=Colors.TEXT_MUTED)
        self.status_lbl.pack(side="left", padx=12, pady=4)

    # =========================================================================
    # Pestana 1: Dashboard - Matriz de Riesgos y Estado General
    # =========================================================================

    def _build_dashboard_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Dashboard  ")

        # Scrollable
        canvas = Canvas(tab, bg=Colors.BG_DARK, highlightthickness=0)
        scrollbar = Scrollbar(tab, orient="vertical", command=canvas.yview)
        scroll_frame = Frame(canvas, bg=Colors.BG_DARK)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Tarjetas de estado
        cards_frame = Frame(scroll_frame, bg=Colors.BG_DARK)
        cards_frame.pack(fill="x", padx=16, pady=(16, 8))

        self._create_stat_card(cards_frame, "API Gateway", "Activo", Colors.ACCENT_GREEN, 0)
        self._create_stat_card(cards_frame, "TLS / HTTPS", "Habilitado", Colors.ACCENT_GREEN, 1)
        self._create_stat_card(cards_frame, "JWT / RBAC", "Configurado", Colors.ACCENT_GREEN, 2)
        self._create_stat_card(cards_frame, "Rate Limiting", "Activo", Colors.ACCENT_ORANGE, 3)
        self._create_stat_card(cards_frame, "Auditoria", "Centralizada", Colors.ACCENT_GREEN, 4)
        self._create_stat_card(cards_frame, "MFA", "Activo", Colors.ACCENT_GREEN, 5)

        # Matriz de riesgos
        risk_header = Label(scroll_frame, text="Matriz de Riesgos - Logi Market Peru S.A.C.",
                            font=("Segoe UI", 13, "bold"),
                            bg=Colors.BG_DARK, fg=Colors.TEXT_PRIMARY)
        risk_header.pack(anchor="w", padx=16, pady=(16, 8))

        columns = ("activo", "amenaza", "vulnerabilidad", "impacto", "riesgo")
        self.risk_tree = ttk.Treeview(scroll_frame, columns=columns, show="headings",
                                       height=8)
        self.risk_tree.heading("activo", text="Activo")
        self.risk_tree.heading("amenaza", text="Amenaza")
        self.risk_tree.heading("vulnerabilidad", text="Vulnerabilidad")
        self.risk_tree.heading("impacto", text="Impacto")
        self.risk_tree.heading("riesgo", text="Nivel de Riesgo")

        self.risk_tree.column("activo", width=180)
        self.risk_tree.column("amenaza", width=240)
        self.risk_tree.column("vulnerabilidad", width=240)
        self.risk_tree.column("impacto", width=160)
        self.risk_tree.column("riesgo", width=120)

        self.risk_tree.pack(fill="x", padx=16, pady=(0, 8))

        # Scrollbar para la tabla
        risk_scroll = Scrollbar(scroll_frame, orient="vertical", command=self.risk_tree.yview)
        self.risk_tree.configure(yscrollcommand=risk_scroll.set)

        self._cargar_matriz_riesgos()

        # Tags de color por nivel de riesgo
        self.risk_tree.tag_configure("critico", background=Colors.ERROR_BG,
                                      foreground=Colors.ACCENT_RED)
        self.risk_tree.tag_configure("alto", background=Colors.WARNING_BG,
                                      foreground=Colors.ACCENT_ORANGE)
        self.risk_tree.tag_configure("medio", background=Colors.INFO_BG,
                                      foreground=Colors.ACCENT_BLUE)

        # Leyenda
        legend_frame = Frame(scroll_frame, bg=Colors.BG_DARK)
        legend_frame.pack(fill="x", padx=16, pady=(4, 16))
        for nivel, color, bg in [
            ("Critico", Colors.ACCENT_RED, Colors.ERROR_BG),
            ("Alto", Colors.ACCENT_ORANGE, Colors.WARNING_BG),
            ("Medio", Colors.ACCENT_BLUE, Colors.INFO_BG),
        ]:
            dot = Canvas(legend_frame, width=14, height=14, bg=Colors.BG_DARK, highlightthickness=0)
            dot.create_oval(2, 2, 12, 12, fill=color, outline="")
            dot.pack(side="left", padx=(12, 4))
            Label(legend_frame, text=nivel, font=("Segoe UI", 9),
                  bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY).pack(side="left", padx=(0, 8))

    def _create_stat_card(self, parent, title, value, color, col):
        card = Frame(parent, bg=Colors.BG_MEDIUM, bd=0, relief="solid",
                     highlightbackground=Colors.BORDER, highlightthickness=1)
        card.grid(row=0, column=col, padx=6, pady=8, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)
        Label(card, text=title, font=("Segoe UI", 8),
              bg=Colors.BG_MEDIUM, fg=Colors.TEXT_SECONDARY).pack(pady=(10, 2), padx=14)
        dot_frame = Frame(card, bg=Colors.BG_MEDIUM)
        dot_frame.pack(pady=(0, 10))
        d = Canvas(dot_frame, width=10, height=10, bg=Colors.BG_MEDIUM, highlightthickness=0)
        d.create_oval(1, 1, 9, 9, fill=color, outline="")
        d.pack(side="left", padx=4)
        Label(dot_frame, text=value, font=("Segoe UI", 10, "bold"),
              bg=Colors.BG_MEDIUM, fg=color).pack(side="left")

    def _cargar_matriz_riesgos(self):
        riesgos = [
            ("Cuentas de Clientes", "Acceso no autorizado\n(credential stuffing)", "Solo usuario/contrasena\nsin MFA", "Robo de identidad,\ntransacciones fraudulentas", "Critico"),
            ("Trafico entre\nMicroservicios", "Interceptacion de trafico\n(MITM)", "HTTP sin TLS,\nausencia de mTLS", "Exposicion de datos\nsensibles en transito", "Critico"),
            ("Datos Personales\nde Clientes", "Exposicion accidental\nde PII", "Falta de DLP, logs\nsin anonimizacion", "Violacion Ley 29733,\nsanciones economicas", "Critico"),
            ("Registros de\nActividad", "Ausencia de mecanismos\nde auditoria", "Sin registro centralizado,\nsin SIEM", "Imposibilidad de deteccion\nde intrusiones", "Alto"),
            ("Credenciales\ndel Sistema", "Uso de credenciales\ncompartidas", "Sin cuentas nominales,\nsin directorio LDAP", "Sin trazabilidad de\nautor de acciones", "Alto"),
            ("Plataforma\nde APIs", "Ataques DoS/DDoS\ncontra endpoints", "Sin API Gateway,\nexposicion directa", "Indisponibilidad de\nservicios criticos", "Alto"),
        ]

        for r in riesgos:
            nivel = r[4]
            tag = nivel.lower()
            if "critico" in tag:
                tag = "critico"
            elif "alto" in tag:
                tag = "alto"
            elif "medio" in tag:
                tag = "medio"
            else:
                tag = ""
            self.risk_tree.insert("", "end", values=r, tags=(tag,))

    # =========================================================================
    # Pestana 2: Autenticacion Segura (Actividad 2)
    # =========================================================================

    def _build_auth_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Login / Auth  ")

        # Panel izquierdo - Login
        left_frame = Frame(tab, bg=Colors.BG_DARK)
        left_frame.pack(side="left", fill="both", expand=True, padx=(16, 8), pady=16)

        Label(left_frame, text="Inicio de Sesion Seguro",
              font=("Segoe UI", 14, "bold"),
              bg=Colors.BG_DARK, fg=Colors.ACCENT_BLUE).pack(anchor="w", pady=(0, 16))

        Label(left_frame, text="Usuario",
              font=("Segoe UI", 9), bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY).pack(anchor="w")
        self.auth_user = Entry(left_frame, font=("Segoe UI", 11),
                               bg=Colors.BG_LIGHT, fg=Colors.TEXT_PRIMARY,
                               insertbackground=Colors.TEXT_PRIMARY, relief="flat")
        self.auth_user.pack(fill="x", pady=(2, 10))
        self.auth_user.insert(0, "admin")

        Label(left_frame, text="Contrasena",
              font=("Segoe UI", 9), bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY).pack(anchor="w")
        self.auth_pass = Entry(left_frame, font=("Segoe UI", 11),
                               bg=Colors.BG_LIGHT, fg=Colors.TEXT_PRIMARY,
                               insertbackground=Colors.TEXT_PRIMARY, relief="flat", show="*")
        self.auth_pass.pack(fill="x", pady=(2, 10))
        self.auth_pass.insert(0, "Admin@2026!")

        Label(left_frame, text="Codigo MFA (6 digitos)",
              font=("Segoe UI", 9), bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY).pack(anchor="w")
        self.auth_mfa = Entry(left_frame, font=("Segoe UI", 11),
                              bg=Colors.BG_LIGHT, fg=Colors.TEXT_PRIMARY,
                              insertbackground=Colors.TEXT_PRIMARY, relief="flat")
        self.auth_mfa.pack(fill="x", pady=(2, 10))
        self.auth_mfa.insert(0, "123456")

        btn_frame = Frame(left_frame, bg=Colors.BG_DARK)
        btn_frame.pack(fill="x", pady=4)
        login_btn = ttk.Button(btn_frame, text="Iniciar Sesion (MFA)",
                                style="Accent.TButton",
                                command=self._login)
        login_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

        logout_btn = ttk.Button(btn_frame, text="Cerrar Sesion",
                                 style="Danger.TButton",
                                 command=self._logout)
        logout_btn.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # Info de sesion
        info_frame = Frame(left_frame, bg=Colors.BG_MEDIUM, bd=0,
                           highlightbackground=Colors.BORDER, highlightthickness=1)
        info_frame.pack(fill="x", pady=(16, 0))

        self.auth_info_text = scrolledtext.ScrolledText(
            info_frame, height=6, font=("Consolas", 9),
            bg=Colors.BG_MEDIUM, fg=Colors.ACCENT_GREEN,
            insertbackground=Colors.TEXT_PRIMARY, relief="flat", wrap=WORD
        )
        self.auth_info_text.pack(fill="x", padx=10, pady=10)
        self.auth_info_text.insert("1.0", "Informacion de sesion:\nNo se ha iniciado sesion.\n\nUsuarios de prueba:\n- admin / Admin@2026!\n- operador / Oper@dor#2026\n- cliente / Client3$2026\n\nMFA: cualquier codigo de 6 digitos.")

        # Panel derecho - Diagrama de Arquitectura Auth
        right_frame = Frame(tab, bg=Colors.BG_DARK)
        right_frame.pack(side="right", fill="both", expand=True, padx=(8, 16), pady=16)

        Label(right_frame, text="Arquitectura de Autenticacion (Actividad 2)",
              font=("Segoe UI", 14, "bold"),
              bg=Colors.BG_DARK, fg=Colors.ACCENT_BLUE).pack(anchor="w", pady=(0, 12))

        diagram_text = scrolledtext.ScrolledText(
            right_frame, height=22, font=("Consolas", 9),
            bg=Colors.BG_MEDIUM, fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY, relief="flat", wrap=WORD
        )
        diagram_text.pack(fill="both", expand=True)

        diagrama = """
  FLUJO DE AUTENTICACION MULTIFACTOR (MFA) + RBAC
  =================================================

  [1] Cliente/App
       |
       v
  [2] API Gateway (HTTPS :8443)
       |
       v
  [3] Servicio de Autenticacion
       |
       +--> [3a] Validar Usuario + Contrasena
       |         |
       |         +--> IAM Centralizado (RBAC)
       |
       +--> [3b] Validar MFA (TOTP 6 digitos)
       |         |
       |         +--> Servidor TOTP
       |
       v
  [4] Generar JWT (HS512, 30 min)
       |
       v
  [5] Retornar Token Bearer + Claims RBAC
       |
       v
  [6] Requests subsecuentes con Authorization Header
       |
       +--> API Gateway valida JWT + Permisos
       +--> Rate Limiting (10-60 req/min)
       +--> Auditoria centralizada

  FLUJO OAUTH 2.0 (Resource Owner Password Credentials)
  ======================================================
  Cliente --> POST /api/auth/login
              {usuario, password, mfa_code}
  Servidor -> {access_token, token_type, expires_in}
  Cliente --> Authorization: Bearer <token> en cada request
  Gateway --> Validar firma, exp, jti, claims RBAC
           --> 401 si invalido/expirado/revocado
           --> 403 si rol sin permiso
           --> 200 + datos protegidos
        """
        diagram_text.insert("1.0", diagrama.strip())
        diagram_text.configure(state="disabled")

        # Politicas RBAC
        Label(right_frame, text="Roles y Permisos (RBAC):",
              font=("Segoe UI", 10, "bold"),
              bg=Colors.BG_DARK, fg=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(12, 4))

        rbac_cols = ("rol", "permisos")
        self.rbac_tree = ttk.Treeview(right_frame, columns=rbac_cols, show="headings",
                                       height=4)
        self.rbac_tree.heading("rol", text="Rol")
        self.rbac_tree.heading("permisos", text="Permisos Asignados")
        self.rbac_tree.column("rol", width=90)
        self.rbac_tree.column("permisos", width=380)
        self.rbac_tree.pack(fill="x")

        for rol, perms in [
            ("admin", "inventory:r/w, payments:r/w, logistics:r/w, audit:r, users:manage"),
            ("operador", "inventory:r/w, payments:r, logistics:r/w"),
            ("cliente", "inventory:r, payments:r (propios), logistics:r (propios)"),
        ]:
            self.rbac_tree.insert("", "end", values=(rol, perms))

    # =========================================================================
    # Pestana 3: Inventario (Actividad 4 - API protegida)
    # =========================================================================

    def _build_inventario_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Inventario  ")

        top_bar = Frame(tab, bg=Colors.BG_MEDIUM, height=44)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)
        Label(top_bar, text="Microservicio de Inventario (protegido con JWT + TLS)",
              font=("Segoe UI", 11, "bold"),
              bg=Colors.BG_MEDIUM, fg=Colors.ACCENT_BLUE).pack(side="left", padx=14, pady=10)

        refresh_btn = ttk.Button(top_bar, text="Actualizar Listado",
                                  command=self._cargar_inventario)
        refresh_btn.pack(side="right", padx=14, pady=10)

        cols = ("id", "nombre", "stock", "precio")
        self.inv_tree = ttk.Treeview(tab, columns=cols, show="headings", height=8)
        self.inv_tree.heading("id", text="ID")
        self.inv_tree.heading("nombre", text="Producto")
        self.inv_tree.heading("stock", text="Stock")
        self.inv_tree.heading("precio", text="Precio (S/)")
        self.inv_tree.column("id", width=100, anchor="center")
        self.inv_tree.column("nombre", width=300)
        self.inv_tree.column("stock", width=120, anchor="center")
        self.inv_tree.column("precio", width=150, anchor="center")
        self.inv_tree.pack(fill="both", expand=True, padx=16, pady=(8, 0))

        self._cargar_inventario_local()

        # Info de seguridad
        info_frame = Frame(tab, bg=Colors.BG_MEDIUM)
        info_frame.pack(fill="x", padx=16, pady=(8, 16))
        Label(info_frame,
              text="Proteccion: TLS 1.2+ en trafico | JWT HS512 en cabecera Authorization | RBAC: admin/operador/cliente con inventory:read",
              font=("Segoe UI", 8),
              bg=Colors.BG_MEDIUM, fg=Colors.TEXT_MUTED).pack(padx=12, pady=8)

    def _cargar_inventario_local(self):
        productos = [
            ("P001", "Laptop HP", 50, "S/ 2,500.00"),
            ("P002", 'Monitor Dell 27"', 30, "S/ 1,200.00"),
            ("P003", "Teclado Mecanico", 100, "S/ 350.00"),
            ("P004", "Mouse Inalambrico", 80, "S/ 150.00"),
            ("P005", "Audifonos Bluetooth", 60, "S/ 200.00"),
        ]
        for p in productos:
            self.inv_tree.insert("", "end", values=p)

    def _cargar_inventario(self):
        def tarea():
            try:
                resp = requests.get(f"{API_BASE}/api/inventory",
                                    headers=self._auth_header(),
                                    verify=False, timeout=10)
                data = resp.json()
                self.inv_tree.delete(*self.inv_tree.get_children())
                if "datos" in data:
                    for p in data["datos"]:
                        self.inv_tree.insert("", "end", values=(
                            p["id"], p["nombre"], p["stock"],
                            f"S/ {p['precio']:,.2f}"
                        ))
                self._set_status(f"Inventario cargado: {resp.status_code}")
            except Exception as e:
                self._set_status(f"Error: {e}")

        threading.Thread(target=tarea, daemon=True).start()

    # =========================================================================
    # Pestana 4: Pagos (Actividad 4 - API protegida)
    # =========================================================================

    def _build_pagos_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Pagos  ")

        # Panel izquierdo - Formulario
        left = Frame(tab, bg=Colors.BG_DARK)
        left.pack(side="left", fill="y", padx=(16, 8), pady=16)

        Label(left, text="Procesar Pago",
              font=("Segoe UI", 13, "bold"),
              bg=Colors.BG_DARK, fg=Colors.ACCENT_BLUE).pack(anchor="w", pady=(0, 12))

        Label(left, text="Monto (S/)",
              font=("Segoe UI", 9), bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY).pack(anchor="w")
        self.pago_monto = Entry(left, font=("Segoe UI", 11),
                                bg=Colors.BG_LIGHT, fg=Colors.TEXT_PRIMARY,
                                insertbackground=Colors.TEXT_PRIMARY, relief="flat")
        self.pago_monto.pack(fill="x", pady=(2, 10))
        self.pago_monto.insert(0, "150.00")

        Label(left, text="Metodo de Pago",
              font=("Segoe UI", 9), bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY).pack(anchor="w")
        self.pago_metodo = ttk.Combobox(left, values=["tarjeta", "transferencia", "efectivo"],
                                        font=("Segoe UI", 11), state="readonly")
        self.pago_metodo.pack(fill="x", pady=(2, 10))
        self.pago_metodo.set("tarjeta")

        procesar_btn = ttk.Button(left, text="Procesar Pago (JWT requerido)",
                                   style="Accent.TButton",
                                   command=self._procesar_pago)
        procesar_btn.pack(fill="x", pady=4)

        self.pago_result = scrolledtext.ScrolledText(
            left, height=4, font=("Consolas", 9),
            bg=Colors.BG_MEDIUM, fg=Colors.ACCENT_GREEN,
            insertbackground=Colors.TEXT_PRIMARY, relief="flat", wrap=WORD
        )
        self.pago_result.pack(fill="x", pady=(12, 0))
        self.pago_result.insert("1.0", "Listo para procesar pagos.\nRequiere autenticacion JWT previa.")

        # Panel derecho - Listado
        right = Frame(tab, bg=Colors.BG_DARK)
        right.pack(side="right", fill="both", expand=True, padx=(8, 16), pady=16)

        top = Frame(right, bg=Colors.BG_MEDIUM, height=44)
        top.pack(fill="x")
        top.pack_propagate(False)
        Label(top, text="Historial de Pagos",
              font=("Segoe UI", 11, "bold"),
              bg=Colors.BG_MEDIUM, fg=Colors.ACCENT_BLUE).pack(side="left", padx=14, pady=10)
        ttk.Button(top, text="Actualizar", command=self._listar_pagos).pack(side="right", padx=14, pady=10)

        cols = ("id", "monto", "metodo", "estado", "timestamp")
        self.pagos_tree = ttk.Treeview(right, columns=cols, show="headings", height=12)
        self.pagos_tree.heading("id", text="ID Pago")
        self.pagos_tree.heading("monto", text="Monto")
        self.pagos_tree.heading("metodo", text="Metodo")
        self.pagos_tree.heading("estado", text="Estado")
        self.pagos_tree.heading("timestamp", text="Fecha")
        self.pagos_tree.column("id", width=300)
        self.pagos_tree.column("monto", width=100, anchor="center")
        self.pagos_tree.column("metodo", width=100, anchor="center")
        self.pagos_tree.column("estado", width=100, anchor="center")
        self.pagos_tree.column("timestamp", width=180, anchor="center")
        self.pagos_tree.pack(fill="both", expand=True, pady=(8, 0))

        Label(right,
              text="Proteccion: Rate Limit 20 req/min (POST) | TLS cifrado | RBAC: payments:write/admin-operador",
              font=("Segoe UI", 8),
              bg=Colors.BG_DARK, fg=Colors.TEXT_MUTED).pack(anchor="w", pady=(4, 0))

    def _procesar_pago(self):
        if not self.access_token:
            messagebox.showwarning("No autenticado", "Inicie sesion en la pestana Login/Auth primero.")
            return

        def tarea():
            try:
                resp = requests.post(f"{API_BASE}/api/payments",
                                     json={"monto": float(self.pago_monto.get()),
                                           "metodo": self.pago_metodo.get()},
                                     headers=self._auth_header(),
                                     verify=False, timeout=10)
                data = resp.json()
                if resp.status_code == 201:
                    self.pago_result.delete("1.0", END)
                    self.pago_result.insert("1.0", json.dumps(data, indent=2))
                    self._listar_pagos()
                    self._set_status("Pago procesado exitosamente")
                else:
                    self.pago_result.delete("1.0", END)
                    self.pago_result.insert("1.0", f"ERROR {resp.status_code}:\n{json.dumps(data, indent=2)}")
                    self._set_status(f"Error en pago: {resp.status_code}")
            except Exception as e:
                self.pago_result.delete("1.0", END)
                self.pago_result.insert("1.0", f"Error de conexion:\n{e}")
                self._set_status(f"Error: {e}")

        threading.Thread(target=tarea, daemon=True).start()

    def _listar_pagos(self):
        if not self.access_token:
            return
        def tarea():
            try:
                resp = requests.get(f"{API_BASE}/api/payments",
                                    headers=self._auth_header(),
                                    verify=False, timeout=10)
                data = resp.json()
                self.pagos_tree.delete(*self.pagos_tree.get_children())
                if "pagos" in data:
                    for p in data["pagos"]:
                        ts = p.get("timestamp", "")[:19].replace("T", " ")
                        self.pagos_tree.insert("", "end", values=(
                            p["id"], f"S/ {p['monto']:,.2f}",
                            p["metodo"], p["estado"], ts
                        ))
            except Exception as e:
                self._set_status(f"Error listar pagos: {e}")
        threading.Thread(target=tarea, daemon=True).start()

    # =========================================================================
    # Pestana 5: Logistica (Actividad 4 - API protegida)
    # =========================================================================

    def _build_logistica_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Logistica  ")

        left = Frame(tab, bg=Colors.BG_DARK)
        left.pack(side="left", fill="y", padx=(16, 8), pady=16)

        Label(left, text="Crear Envio",
              font=("Segoe UI", 13, "bold"),
              bg=Colors.BG_DARK, fg=Colors.ACCENT_BLUE).pack(anchor="w", pady=(0, 12))

        Label(left, text="Direccion de Destino",
              font=("Segoe UI", 9), bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY).pack(anchor="w")
        self.envio_destino = Entry(left, font=("Segoe UI", 11),
                                   bg=Colors.BG_LIGHT, fg=Colors.TEXT_PRIMARY,
                                   insertbackground=Colors.TEXT_PRIMARY, relief="flat")
        self.envio_destino.pack(fill="x", pady=(2, 10))
        self.envio_destino.insert(0, "Av. Ejercito 123, Arequipa")

        Label(left, text="Productos (IDs separados por coma)",
              font=("Segoe UI", 9), bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY).pack(anchor="w")
        self.envio_productos = Entry(left, font=("Segoe UI", 11),
                                     bg=Colors.BG_LIGHT, fg=Colors.TEXT_PRIMARY,
                                     insertbackground=Colors.TEXT_PRIMARY, relief="flat")
        self.envio_productos.pack(fill="x", pady=(2, 10))
        self.envio_productos.insert(0, "P001, P003")

        ttk.Button(left, text="Programar Envio (JWT requerido)",
                   style="Accent.TButton",
                   command=self._crear_envio).pack(fill="x", pady=4)

        self.envio_result = scrolledtext.ScrolledText(
            left, height=4, font=("Consolas", 9),
            bg=Colors.BG_MEDIUM, fg=Colors.ACCENT_GREEN,
            insertbackground=Colors.TEXT_PRIMARY, relief="flat", wrap=WORD
        )
        self.envio_result.pack(fill="x", pady=(12, 0))
        self.envio_result.insert("1.0", "Listo para programar envios.\nRequiere autenticacion JWT previa.")

        right = Frame(tab, bg=Colors.BG_DARK)
        right.pack(side="right", fill="both", expand=True, padx=(8, 16), pady=16)

        top = Frame(right, bg=Colors.BG_MEDIUM, height=44)
        top.pack(fill="x")
        top.pack_propagate(False)
        Label(top, text="Envios Programados",
              font=("Segoe UI", 11, "bold"),
              bg=Colors.BG_MEDIUM, fg=Colors.ACCENT_BLUE).pack(side="left", padx=14, pady=10)
        ttk.Button(top, text="Actualizar", command=self._listar_envios).pack(side="right", padx=14, pady=10)

        cols = ("id", "destino", "productos", "estado", "timestamp")
        self.envios_tree = ttk.Treeview(right, columns=cols, show="headings", height=12)
        self.envios_tree.heading("id", text="ID Envio")
        self.envios_tree.heading("destino", text="Destino")
        self.envios_tree.heading("productos", text="Productos")
        self.envios_tree.heading("estado", text="Estado")
        self.envios_tree.heading("timestamp", text="Fecha")
        self.envios_tree.column("id", width=280)
        self.envios_tree.column("destino", width=180)
        self.envios_tree.column("productos", width=120, anchor="center")
        self.envios_tree.column("estado", width=100, anchor="center")
        self.envios_tree.column("timestamp", width=170, anchor="center")
        self.envios_tree.pack(fill="both", expand=True, pady=(8, 0))

        Label(right,
              text="Proteccion: Rate Limit 30 req/min (POST) | TLS cifrado | RBAC: logistics:write/admin-operador",
              font=("Segoe UI", 8),
              bg=Colors.BG_DARK, fg=Colors.TEXT_MUTED).pack(anchor="w", pady=(4, 0))

    def _crear_envio(self):
        if not self.access_token:
            messagebox.showwarning("No autenticado", "Inicie sesion en la pestana Login/Auth primero.")
            return

        def tarea():
            try:
                prods = [p.strip() for p in self.envio_productos.get().split(",") if p.strip()]
                resp = requests.post(f"{API_BASE}/api/logistics",
                                     json={"destino": self.envio_destino.get(),
                                           "productos": prods},
                                     headers=self._auth_header(),
                                     verify=False, timeout=10)
                data = resp.json()
                if resp.status_code == 201:
                    self.envio_result.delete("1.0", END)
                    self.envio_result.insert("1.0", json.dumps(data, indent=2))
                    self._listar_envios()
                    self._set_status("Envio programado exitosamente")
                else:
                    self.envio_result.delete("1.0", END)
                    self.envio_result.insert("1.0", f"ERROR {resp.status_code}:\n{json.dumps(data, indent=2)}")
                    self._set_status(f"Error en envio: {resp.status_code}")
            except Exception as e:
                self.envio_result.delete("1.0", END)
                self.envio_result.insert("1.0", f"Error de conexion:\n{e}")
                self._set_status(f"Error: {e}")

        threading.Thread(target=tarea, daemon=True).start()

    def _listar_envios(self):
        if not self.access_token:
            return
        def tarea():
            try:
                resp = requests.get(f"{API_BASE}/api/logistics",
                                    headers=self._auth_header(),
                                    verify=False, timeout=10)
                data = resp.json()
                self.envios_tree.delete(*self.envios_tree.get_children())
                if "envios" in data:
                    for e in data["envios"]:
                        ts = e.get("timestamp", "")[:19].replace("T", " ")
                        prods = ", ".join(e.get("productos", []))
                        self.envios_tree.insert("", "end", values=(
                            e["id"], e["destino"], prods, e["estado"], ts
                        ))
            except Exception as e:
                self._set_status(f"Error listar envios: {e}")
        threading.Thread(target=tarea, daemon=True).start()

    # =========================================================================
    # Pestana 6: Auditoria (Actividad 5)
    # =========================================================================

    def _build_auditoria_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Auditoria  ")

        top_bar = Frame(tab, bg=Colors.BG_MEDIUM, height=44)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)
        Label(top_bar, text="Sistema de Auditoria Centralizada (Actividad 5)",
              font=("Segoe UI", 11, "bold"),
              bg=Colors.BG_MEDIUM, fg=Colors.ACCENT_BLUE).pack(side="left", padx=14, pady=10)

        btn_frame = Frame(top_bar, bg=Colors.BG_MEDIUM)
        btn_frame.pack(side="right", padx=10)
        ttk.Button(btn_frame, text="Logs Auditoria", command=self._cargar_logs_auditoria).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Logs Seguridad", command=self._cargar_logs_seguridad).pack(side="left", padx=4)

        # Panel principal con dos areas de logs
        paned = Frame(tab, bg=Colors.BG_DARK)
        paned.pack(fill="both", expand=True, padx=16, pady=8)

        Label(paned, text="Logs de Auditoria (operaciones de negocio)",
              font=("Segoe UI", 10, "bold"),
              bg=Colors.BG_DARK, fg=Colors.ACCENT_GREEN).pack(anchor="w", pady=(0, 4))

        self.audit_log_text = scrolledtext.ScrolledText(
            paned, height=14, font=("Consolas", 9),
            bg=Colors.BG_LIGHT, fg=Colors.ACCENT_GREEN,
            insertbackground=Colors.TEXT_PRIMARY, relief="flat", wrap=WORD
        )
        self.audit_log_text.pack(fill="both", expand=True)
        self.audit_log_text.insert("1.0", "Cargando logs de auditoria...")

        Label(paned, text="Logs de Seguridad (eventos de seguridad)",
              font=("Segoe UI", 10, "bold"),
              bg=Colors.BG_DARK, fg=Colors.ACCENT_RED).pack(anchor="w", pady=(12, 4))

        self.sec_log_text = scrolledtext.ScrolledText(
            paned, height=12, font=("Consolas", 9),
            bg=Colors.BG_LIGHT, fg=Colors.ACCENT_RED,
            insertbackground=Colors.TEXT_PRIMARY, relief="flat", wrap=WORD
        )
        self.sec_log_text.pack(fill="both", expand=True)
        self.sec_log_text.insert("1.0", "Cargando logs de seguridad...")

        # Tabla de eventos auditables
        Label(paned, text="Eventos Auditables Criticos",
              font=("Segoe UI", 10, "bold"),
              bg=Colors.BG_DARK, fg=Colors.ACCENT_ORANGE).pack(anchor="w", pady=(12, 4))

        ev_cols = ("categoria", "eventos", "retencion")
        self.ev_tree = ttk.Treeview(paned, columns=ev_cols, show="headings", height=6)
        self.ev_tree.heading("categoria", text="Categoria")
        self.ev_tree.heading("eventos", text="Eventos Registrados")
        self.ev_tree.heading("retencion", text="Retencion")
        self.ev_tree.column("categoria", width=150)
        self.ev_tree.column("eventos", width=420)
        self.ev_tree.column("retencion", width=140, anchor="center")
        self.ev_tree.pack(fill="x")

        eventos_auditables = [
            ("Autenticacion", "Login exitoso/fallido, MFA, bloqueo cuenta, cambio password", "12 meses"),
            ("Pagos", "Pago iniciado/completado/rechazado, reembolso, disputa", "7 anios (SUNAT)"),
            ("Configuracion", "Cambio roles RBAC, politicas seguridad, rotacion secretos", "12 meses"),
            ("Datos PII", "Consulta/exportacion datos personales, acceso masivo", "12 meses"),
            ("Seguridad", "Token invalido, rate limit, acceso denegado, escaneo endpoints", "18 meses"),
            ("Sistema", "Inicio/detencion/fallo servicio, health check, consumo recursos", "6 meses"),
        ]
        for ev in eventos_auditables:
            self.ev_tree.insert("", "end", values=ev)

    def _cargar_logs_auditoria(self):
        if not self.access_token:
            messagebox.showwarning("No autenticado", "Inicie sesion como admin.")
            return
        def tarea():
            try:
                resp = requests.get(f"{API_BASE}/api/audit/logs",
                                    headers=self._auth_header(),
                                    verify=False, timeout=10)
                data = resp.json()
                self.audit_log_text.delete("1.0", END)
                if data.get("eventos"):
                    for ev in reversed(data["eventos"][-30:]):
                        self.audit_log_text.insert("1.0", json.dumps(ev, indent=2) + "\n")
                else:
                    self.audit_log_text.insert("1.0", "No hay eventos de auditoria registrados.")
                self._set_status(f"Logs auditoria cargados: {data.get('total_eventos', 0)} eventos")
            except Exception as e:
                self._set_status(f"Error: {e}")
        threading.Thread(target=tarea, daemon=True).start()

    def _cargar_logs_seguridad(self):
        if not self.access_token:
            messagebox.showwarning("No autenticado", "Inicie sesion como admin.")
            return
        def tarea():
            try:
                resp = requests.get(f"{API_BASE}/api/audit/security",
                                    headers=self._auth_header(),
                                    verify=False, timeout=10)
                data = resp.json()
                self.sec_log_text.delete("1.0", END)
                if data.get("eventos"):
                    for ev in reversed(data["eventos"][-20:]):
                        self.sec_log_text.insert("1.0", json.dumps(ev, indent=2) + "\n")
                else:
                    self.sec_log_text.insert("1.0", "No hay eventos de seguridad registrados.")
                self._set_status(f"Logs seguridad cargados: {data.get('total_eventos', 0)} eventos")
            except Exception as e:
                self._set_status(f"Error: {e}")
        threading.Thread(target=tarea, daemon=True).start()

    # =========================================================================
    # Pestana 7: Seguridad TLS y Certificados (Actividad 3)
    # =========================================================================

    def _build_seguridad_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Seguridad TLS  ")

        left = Frame(tab, bg=Colors.BG_DARK)
        left.pack(side="left", fill="both", expand=True, padx=(16, 8), pady=16)

        Label(left, text="Configuracion del Canal Seguro (Actividad 3)",
              font=("Segoe UI", 14, "bold"),
              bg=Colors.BG_DARK, fg=Colors.ACCENT_BLUE).pack(anchor="w", pady=(0, 12))

        # Info del certificado
        cert_info = """
  INFORMACION DEL CERTIFICADO TLS
  ================================

  CA Raiz:
    CN: LogiMarket Root CA
    OU: Seguridad
    O:  LogiMarket Peru S.A.C.
    Algoritmo: RSA 4096 bits + SHA-512
    Validez: 365 dias

  Certificado del Servidor:
    CN: localhost
    OU: TI
    O:  LogiMarket Peru S.A.C.
    Algoritmo: RSA 2048 bits + SHA-512
    Validez: 365 dias
    SAN: localhost, *.localhost
         127.0.0.1, ::1

  Protocolo: TLS 1.2+ (minimo configurable)
  Cipher Suites: ECDHE + AES-256-GCM / ChaCha20-Poly1305
  Perfect Forward Secrecy: Habilitado

  Puerto: 8443 (HTTPS unicamente)
  HTTP rechazado en el puerto 8443
        """

        cert_text = scrolledtext.ScrolledText(
            left, height=16, font=("Consolas", 10),
            bg=Colors.BG_MEDIUM, fg=Colors.ACCENT_GREEN,
            insertbackground=Colors.TEXT_PRIMARY, relief="flat", wrap=WORD
        )
        cert_text.pack(fill="x")
        cert_text.insert("1.0", cert_info.strip())
        cert_text.configure(state="disabled")

        # Beneficios
        Label(left, text="Beneficios del Canal Seguro TLS:",
              font=("Segoe UI", 11, "bold"),
              bg=Colors.BG_DARK, fg=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(16, 8))

        beneficios = [
            ("Confidencialidad", "Trafico cifrado extremo a extremo, inaccesible para sniffers"),
            ("Integridad", "HMAC en cada registro TLS garantiza que los datos no fueron alterados"),
            ("Autenticacion", "El certificado del servidor verifica la identidad ante el cliente"),
            ("No Repudio", "Firma digital de la CA raiz vincula el certificado a la organizacion"),
        ]

        for titulo, desc in beneficios:
            row = Frame(left, bg=Colors.BG_DARK)
            row.pack(fill="x", pady=2)
            Label(row, text=f"  {titulo}:", font=("Segoe UI", 9, "bold"),
                  bg=Colors.BG_DARK, fg=Colors.ACCENT_BLUE).pack(side="left")
            Label(row, text=desc, font=("Segoe UI", 9),
                  bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY).pack(side="left")

        # Panel derecho - Pipeline de auditoria + Rate Limiting
        right = Frame(tab, bg=Colors.BG_DARK)
        right.pack(side="right", fill="both", expand=True, padx=(8, 16), pady=16)

        Label(right, text="Arquitectura de Seguridad Integral",
              font=("Segoe UI", 14, "bold"),
              bg=Colors.BG_DARK, fg=Colors.ACCENT_BLUE).pack(anchor="w", pady=(0, 12))

        arch_text = scrolledtext.ScrolledText(
            right, height=20, font=("Consolas", 9),
            bg=Colors.BG_MEDIUM, fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY, relief="flat", wrap=WORD
        )
        arch_text.pack(fill="both", expand=True)

        arquitectura = """
  PIPELINE DE SEGURIDAD - LOGI MARKET
  ====================================

  [PERIMETRO]
  Cliente --> HTTPS :8443 --> API Gateway
                                 |
        +------------------------+------------------------+
        |                        |                        |
  [AUTENTICACION]         [AUTORIZACION]           [PROTECCION]
  Validar JWT HS512       Evaluar RBAC Claims      Rate Limiting
  Verificar exp           Verificar permiso        Token Bucket 60s
  Verificar jti (revoc)   admin/oper/cliente       10-60 req/min
        |                        |                        |
        +------------------------+------------------------+
                                 |
                     [MICROSERVICIOS INTERNOS]
                      Auth | Inventario | Pagos | Logistica
                                 |
                     [AUDITORIA CENTRALIZADA]
                      audit.log + security.log
                      RotatingFileHandler 5MB
                      Retencion 6-18 meses
                      Formato: JSON estructurado

  FLUJO DE PETICION PROTEGIDA:
  ============================
  1. Cliente envia credenciales + MFA
  2. API Gateway autentica y emite JWT
  3. Cliente adjunta Bearer Token en cada request
  4. Gateway valida JWT, RBAC, Rate Limit
  5. Request enrutado a microservicio interno
  6. Respuesta cifrada TLS de vuelta al cliente
  7. Cada paso registrado en auditoria

  ALERTAS AUTOMATIZADAS:
  ======================
  - 5+ fallos login en 15 min --> Email + Slack
  - Rate limit activado --> Slack #operaciones
  - Token revocado reutilizado --> Email + Slack
  - Acceso PII no autorizado --> Email + SMS critico
  - 3+ servicios caidos --> PagerDuty
  - Escaneo de endpoints --> Slack #seguridad
        """
        arch_text.insert("1.0", arquitectura.strip())
        arch_text.configure(state="disabled")

        # Estado TLS
        Label(right, text="Verificar Conexion TLS con el Servidor:",
              font=("Segoe UI", 10, "bold"),
              bg=Colors.BG_DARK, fg=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(12, 4))

        tls_frame = Frame(right, bg=Colors.BG_DARK)
        tls_frame.pack(fill="x")
        ttk.Button(tls_frame, text="Verificar Health Check",
                    command=self._verificar_health).pack(side="left", padx=(0, 6))
        ttk.Button(tls_frame, text="Verificar con curl",
                    command=self._mostrar_comando_curl).pack(side="left")
        self.tls_status = Label(right, text="",
                                font=("Segoe UI", 9),
                                bg=Colors.BG_DARK, fg=Colors.ACCENT_GREEN)
        self.tls_status.pack(anchor="w", pady=(8, 0))

    def _verificar_health(self):
        def tarea():
            try:
                resp = requests.get(f"{API_BASE}/api/health", verify=False, timeout=10)
                data = resp.json()
                self.tls_status.configure(
                    text=f"TLS Activo | Servicio: {data.get('servicio')} | "
                         f"TLS: {data.get('tls')} | Timestamp: {data.get('timestamp')}"
                )
            except Exception as e:
                self.tls_status.configure(text=f"Error de conexion TLS: {e}")
        threading.Thread(target=tarea, daemon=True).start()

    def _mostrar_comando_curl(self):
        ventana = Toplevel(self.root)
        ventana.title("Verificar TLS con OpenSSL")
        ventana.geometry("700x250")
        ventana.configure(bg=Colors.BG_DARK)

        Label(ventana, text="Comandos para verificar el canal TLS:",
              font=("Segoe UI", 12, "bold"),
              bg=Colors.BG_DARK, fg=Colors.ACCENT_BLUE).pack(padx=16, pady=(16, 8))

        cmds = (
            "# Health check\n"
            'curl -k https://localhost:8443/api/health\n\n'
            "# Ver certificado TLS\n"
            'openssl s_client -connect localhost:8443 -showcerts\n\n'
            "# Verificar cifrado\n"
            'openssl s_client -connect localhost:8443 2>&1 | '
            'openssl x509 -text -noout | grep -E "Subject:|DNS:"\n\n'
            "# Login con MFA\n"
            'curl -k -X POST https://localhost:8443/api/auth/login \\\n'
            '  -H "Content-Type: application/json" \\\n'
            '  -d \'{"usuario":"admin","password":"Admin@2026!","mfa_code":"123456"}\''
        )

        cmd_text = scrolledtext.ScrolledText(ventana, height=8, font=("Consolas", 10),
                                             bg=Colors.BG_LIGHT, fg=Colors.ACCENT_GREEN,
                                             relief="flat")
        cmd_text.pack(fill="both", expand=True, padx=16, pady=8)
        cmd_text.insert("1.0", cmds)
        cmd_text.configure(state="disabled")

        ttk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=(0, 16))

    # =========================================================================
    # Metodos de autenticacion
    # =========================================================================

    def _auth_header(self):
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}

    def _login(self):
        def tarea():
            usuario = self.auth_user.get().strip()
            password = self.auth_pass.get().strip()
            mfa = self.auth_mfa.get().strip()

            try:
                resp = requests.post(f"{API_BASE}/api/auth/login",
                                     json={"usuario": usuario,
                                           "password": password,
                                           "mfa_code": mfa},
                                     verify=False, timeout=10)
                data = resp.json()

                self.auth_info_text.configure(state="normal")
                self.auth_info_text.delete("1.0", END)

                if resp.status_code == 200:
                    self.access_token = data["access_token"]
                    self.token_type = data["token_type"]
                    self.usuario_actual = usuario
                    self.rol_actual = data["rol"]

                    self.auth_info_text.insert("1.0", (
                        f"SESION INICIADA\n"
                        f"================\n"
                        f"Usuario: {data['usuario']}\n"
                        f"Rol: {data['rol']}\n"
                        f"Token: {self.access_token[:40]}...\n"
                        f"Expira en: {data['expires_in']} segundos\n"
                        f"Tipo: {data['token_type']}\n\n"
                        f"Puede usar las demas pestanas ahora."
                    ))

                    self.session_dot.itemconfigure(self.session_oval, fill=Colors.ACCENT_GREEN)
                    self.session_label.configure(text=f"Conectado: {usuario} ({data['rol']})",
                                                  fg=Colors.ACCENT_GREEN)
                    self._set_status(f"Login exitoso: {usuario} (rol: {data['rol']})")
                    self._cargar_logs_auditoria()
                else:
                    self.access_token = None
                    self.usuario_actual = None
                    self.rol_actual = None

                    self.auth_info_text.insert("1.0", (
                        f"ERROR DE AUTENTICACION\n"
                        f"=======================\n"
                        f"Codigo: {resp.status_code}\n"
                        f"Mensaje: {data.get('mensaje', data.get('error', 'Desconocido'))}\n\n"
                        f"Verifique usuario, contrasena y codigo MFA."
                    ))
                    self.session_dot.itemconfigure(self.session_oval, fill=Colors.ACCENT_RED)
                    self.session_label.configure(text="Error de autenticacion", fg=Colors.ACCENT_RED)
                    self._set_status(f"Login fallido: {resp.status_code}")
            except Exception as e:
                self.auth_info_text.configure(state="normal")
                self.auth_info_text.delete("1.0", END)
                self.auth_info_text.insert("1.0", f"Error de conexion:\n{e}")
                self._set_status(f"Error de conexion: {e}")

            self.auth_info_text.configure(state="disabled")

        threading.Thread(target=tarea, daemon=True).start()

    def _logout(self):
        if not self.access_token:
            messagebox.showinfo("Info", "No hay sesion activa.")
            return

        def tarea():
            try:
                resp = requests.post(f"{API_BASE}/api/auth/logout",
                                     headers=self._auth_header(),
                                     verify=False, timeout=10)
                self.access_token = None
                self.usuario_actual = None
                self.rol_actual = None

                self.auth_info_text.configure(state="normal")
                self.auth_info_text.delete("1.0", END)
                self.auth_info_text.insert("1.0", "Sesion cerrada exitosamente.\nToken revocado en el servidor.")
                self.auth_info_text.configure(state="disabled")

                self.session_dot.itemconfigure(self.session_oval, fill=Colors.TEXT_MUTED)
                self.session_label.configure(text="No autenticado", fg=Colors.TEXT_MUTED)
                self._set_status("Sesion cerrada")
            except Exception as e:
                self._set_status(f"Error al cerrar sesion: {e}")

        threading.Thread(target=tarea, daemon=True).start()

    def _set_status(self, msg):
        self.status_lbl.configure(text=f"{msg} | API: {API_BASE}")


# =============================================================================
# Punto de entrada
# =============================================================================

def main():
    root = Tk()
    app = LogiMarketApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
