import socket
import threading
import pickle
import struct
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog

from chat_message import ChatMessage


# ── Helpers de red: mismos que el servidor ────────────────────────────────────
def send_packet(sock, data: bytes):
    sock.sendall(struct.pack(">I", len(data)) + data)

def recv_packet(sock) -> bytes:
    raw_len = _recv_exactly(sock, 4)
    n = struct.unpack(">I", raw_len)[0]
    return _recv_exactly(sock, n)

def _recv_exactly(sock, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Conexion cerrada")
        buf += chunk
    return buf
# ─────────────────────────────────────────────────────────────────────────────


class ClientGUI:
    WINDOW_TITLE = "Chat Client - Sistemas Distribuidos"

    def __init__(self):
        self.client = None
        self.running = True

        self.root = tk.Tk()
        self.root.title(self.WINDOW_TITLE)
        self.root.geometry("700x480")
        self.root.minsize(500, 350)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.resizable(True, True)

        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)
        self.root.columnconfigure(0, weight=1)

        self._build_connection_frame()
        self._build_middle_frame()
        self._build_input_frame()

        self.root.mainloop()

    # ======================================================
    # BUILD UI
    # ======================================================

    def _build_connection_frame(self):
        frame = tk.LabelFrame(self.root, text="Conexion", padx=5, pady=4)
        frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 2))

        tk.Label(frame, text="Servidor:").grid(row=0, column=0, sticky=tk.W)
        self.server_entry = tk.Entry(frame, width=14)
        self.server_entry.insert(0, "localhost")
        self.server_entry.grid(row=0, column=1, padx=4)

        tk.Label(frame, text="Puerto:").grid(row=0, column=2, sticky=tk.W)
        self.port_entry = tk.Entry(frame, width=6)
        self.port_entry.insert(0, "1500")
        self.port_entry.grid(row=0, column=3, padx=4)

        tk.Label(frame, text="Usuario:").grid(row=0, column=4, sticky=tk.W)
        self.username_entry = tk.Entry(frame, width=12)
        self.username_entry.insert(0, "Usuario")
        self.username_entry.grid(row=0, column=5, padx=4)

        self.connect_btn = tk.Button(
            frame, text="Conectar", command=self._toggle_connection,
            bg="#4CAF50", fg="white", width=10
        )
        self.connect_btn.grid(row=0, column=6, padx=8)

        self.status_label = tk.Label(frame, text="Desconectado", fg="red")
        self.status_label.grid(row=0, column=7, padx=4)

    def _build_middle_frame(self):
        middle = tk.Frame(self.root)
        middle.grid(row=1, column=0, sticky="nsew", padx=8, pady=2)
        middle.rowconfigure(0, weight=1)
        middle.columnconfigure(0, weight=1)
        middle.columnconfigure(1, weight=0)

        chat_frame = tk.LabelFrame(middle, text="Mensajes", padx=4, pady=4)
        chat_frame.grid(row=0, column=0, sticky="nsew")
        chat_frame.rowconfigure(0, weight=1)
        chat_frame.columnconfigure(0, weight=1)

        self.chat_area = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 10)
        )
        self.chat_area.grid(row=0, column=0, sticky="nsew")

        self.chat_area.tag_config("system",  foreground="gray")
        self.chat_area.tag_config("private", foreground="purple")
        self.chat_area.tag_config("mine",    foreground="blue")
        self.chat_area.tag_config("other",   foreground="black")
        self.chat_area.tag_config("error",   foreground="red")
        self.chat_area.tag_config("file",    foreground="#0077aa")

        users_frame = tk.LabelFrame(middle, text="En linea", padx=4, pady=4)
        users_frame.grid(row=0, column=1, sticky="ns", padx=(4, 0))

        self.users_listbox = tk.Listbox(users_frame, width=16, font=("Consolas", 10))
        self.users_listbox.pack(fill=tk.BOTH, expand=True)
        self.users_listbox.bind("<Double-Button-1>", self._select_user)

    def _build_input_frame(self):
        frame = tk.Frame(self.root, padx=8, pady=6)
        frame.grid(row=2, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=0, column=1, padx=(4, 0))

        # Botón para adjuntar archivo
        self.file_btn = tk.Button(
            btn_frame, text="Archivo", command=self._send_file,
            bg="#9C27B0", fg="white", width=8
        )
        self.file_btn.pack(side=tk.LEFT, padx=2)
        self.file_btn.config(state=tk.DISABLED)

        tk.Button(
            btn_frame, text="WHOISIN", command=lambda: self._send_command("WHOISIN"),
            bg="#FF9800", fg="white", width=8
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="LOGOUT", command=self._logout,
            bg="#f44336", fg="white", width=8
        ).pack(side=tk.LEFT, padx=2)

        self.send_btn = tk.Button(
            frame, text="Enviar", command=self._send_message,
            bg="#2196F3", fg="white", width=8
        )
        self.send_btn.grid(row=0, column=2, padx=(4, 0))
        self.send_btn.config(state=tk.DISABLED)

        self.msg_entry = tk.Entry(frame, font=("Consolas", 11))
        self.msg_entry.grid(row=0, column=0, sticky="ew")
        self.msg_entry.bind("<Return>", lambda e: self._send_message())
        self.msg_entry.config(state=tk.DISABLED)

    # ======================================================
    # CONNECTION
    # ======================================================

    def _toggle_connection(self):
        if self.client and self.client.socket:
            self._disconnect()
        else:
            self._connect()

    def _connect(self):
        server   = self.server_entry.get().strip()
        username = self.username_entry.get().strip()
        try:
            port = int(self.port_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Puerto invalido.")
            return

        if not username:
            messagebox.showerror("Error", "Ingrese un nombre de usuario.")
            return

        self.client = ClientGUIWrapper(server, port, username, self._on_message)
        result = self.client.start()

        if result == "USERNAME_TAKEN":
            self.client = None
            messagebox.showerror(
                "Nombre en uso",
                f"El usuario '{username}' ya está conectado.\nElige otro nombre."
            )
            return
        elif not result:
            self.client = None
            messagebox.showerror("Error", "No se pudo conectar al servidor.")
            return

        self.connect_btn.config(text="Desconectar", bg="#f44336")
        self.status_label.config(text=f"Conectado: {username}", fg="green")
        for w in (self.server_entry, self.port_entry, self.username_entry):
            w.config(state=tk.DISABLED)
        self.msg_entry.config(state=tk.NORMAL)
        self.send_btn.config(state=tk.NORMAL)
        self.file_btn.config(state=tk.NORMAL)
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state=tk.DISABLED)
        self.users_listbox.delete(0, tk.END)
        self._append_system("*** Bienvenido al chat ***")
        self.msg_entry.focus_set()

    def _disconnect(self):
        if self.client:
            try:
                self.client.send_message(ChatMessage(ChatMessage.LOGOUT, ""))
            except:
                pass
            self.client.disconnect()
            self.client = None

        self.connect_btn.config(text="Conectar", bg="#4CAF50")
        self.status_label.config(text="Desconectado", fg="red")
        for w in (self.server_entry, self.port_entry, self.username_entry):
            w.config(state=tk.NORMAL)
        self.msg_entry.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)
        self.file_btn.config(state=tk.DISABLED)
        self.users_listbox.delete(0, tk.END)
        self._append_system("*** Desconectado del servidor ***")

    # ======================================================
    # MENSAJES DE TEXTO
    # ======================================================

    def _send_message(self):
        msg = self.msg_entry.get().strip()
        if not msg or not self.client:
            return

        upper = msg.upper()
        if upper == "LOGOUT":
            self._logout()
        elif upper == "WHOISIN":
            self.client.send_message(ChatMessage(ChatMessage.WHOISIN, ""))
        else:
            self.client.send_message(ChatMessage(ChatMessage.MESSAGE, msg))

        self.msg_entry.delete(0, tk.END)

    def _send_command(self, cmd):
        if not self.client:
            return
        if cmd == "WHOISIN":
            self.client.send_message(ChatMessage(ChatMessage.WHOISIN, ""))

    # ======================================================
    # ENVÍO DE ARCHIVOS
    # ======================================================

    def _send_file(self):
        if not self.client:
            return

        filepath = filedialog.askopenfilename(title="Seleccionar archivo")
        if not filepath:
            return

        filename = os.path.basename(filepath)
        try:
            with open(filepath, "rb") as f:
                filedata = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")
            return

        # Límite de 50 MB para no saturar la red
        MAX_BYTES = 50 * 1024 * 1024
        if len(filedata) > MAX_BYTES:
            messagebox.showerror("Error", "El archivo supera el límite de 50 MB.")
            return

        # Determinar destinatario: si hay @usuario en el entry, es privado
        target = None
        text_in_entry = self.msg_entry.get().strip()
        if text_in_entry.startswith("@"):
            target = text_in_entry.split()[0][1:]   # quitar @

        cm = ChatMessage(
            ChatMessage.FILE,
            filename,
            extra={"target": target, "data": filedata}
        )
        self.client.send_message(cm)

        dest = f"@{target}" if target else "todos"
        size_kb = len(filedata) / 1024
        self._append(
            f"[Archivo enviado a {dest}] {filename} ({size_kb:.1f} KB)\n", "file"
        )
        self.msg_entry.delete(0, tk.END)

    # ======================================================
    # RECEPCIÓN DE ARCHIVOS
    # ======================================================

    def _receive_file(self, cm):
        extra    = cm.get_extra() or {}
        sender   = extra.get("sender", "desconocido")
        filedata = extra.get("data", b"")
        filename = cm.get_message()
        size_kb  = len(filedata) / 1024

        my_username = self.client.username if self.client else ""
        is_mine = (sender == my_username)

        if is_mine:
            # Es la copia de confirmación al emisor — ya se mostró en _send_file
            return

        # Notificar en el chat con botón para guardar
        self._append(
            f"[Archivo recibido de {sender}] {filename} ({size_kb:.1f} KB) — "
            f"haz clic en 'Guardar' para descargarlo.\n",
            "file"
        )

        # Preguntar dónde guardar
        save_path = filedialog.asksaveasfilename(
            title=f"Guardar archivo de {sender}",
            initialfile=filename
        )
        if not save_path:
            return

        try:
            with open(save_path, "wb") as f:
                f.write(filedata)
            self._append(f"[Guardado en: {save_path}]\n", "file")
        except Exception as e:
            self._append_error(f"Error al guardar '{filename}': {e}")

    # ======================================================
    # LISTA DE USUARIOS
    # ======================================================

    def _select_user(self, event):
        selection = self.users_listbox.curselection()
        if selection:
            username = self.users_listbox.get(selection[0]).strip()
            self.msg_entry.config(state=tk.NORMAL)
            self.msg_entry.delete(0, tk.END)
            self.msg_entry.insert(0, f"@{username} ")
            self.msg_entry.focus_set()

    def _logout(self):
        if not self.client:
            return
        self.client.send_message(ChatMessage(ChatMessage.LOGOUT, ""))
        self._disconnect()

    # ======================================================
    # CALLBACK DESDE EL HILO DE RED
    # ======================================================

    def _on_message(self, payload):
        self.root.after(0, self._process_payload, payload)

    def _process_payload(self, payload):
        # El payload puede ser un ChatMessage (archivo) o un string (texto)
        if isinstance(payload, ChatMessage):
            if payload.get_type() == ChatMessage.FILE:
                self._receive_file(payload)
            return

        # A partir de aquí es string
        msg = str(payload).strip()
        if not msg:
            return

        if msg.startswith("EXISTING_USERS:"):
            for u in msg[len("EXISTING_USERS:"):].split(","):
                u = u.strip()
                if u and u not in self.users_listbox.get(0, tk.END):
                    self.users_listbox.insert(tk.END, u)
            return

        if msg.startswith("List of the users connected at"):
            self.users_listbox.delete(0, tk.END)
            return

        parts = msg.split(") ", 1)
        if len(parts) == 2 and parts[0].isdigit():
            usr = parts[1].split(" since ")[0] if " since " in parts[1] else parts[1]
            self.users_listbox.insert(tk.END, usr)
            return

        if "[PRIVADO]" in msg:
            self._append(msg + "\n", "private")
            return

        if "has joined the chat room" in msg:
            try:
                notif_start = msg.index("***") + 3
                notif_end   = msg.index(" has joined")
                name = msg[notif_start:notif_end].strip()
            except (ValueError, IndexError):
                name = ""
            self._append_system(msg)
            if name and name not in self.users_listbox.get(0, tk.END):
                self.users_listbox.insert(tk.END, name)
            return

        if "has left the chat room" in msg:
            try:
                notif_start = msg.index("***") + 3
                notif_end   = msg.index(" has left")
                name = msg[notif_start:notif_end].strip()
            except (ValueError, IndexError):
                name = ""
            self._append_system(msg)
            if name:
                try:
                    idx = list(self.users_listbox.get(0, tk.END)).index(name)
                    self.users_listbox.delete(idx)
                except ValueError:
                    pass
            return

        if "Sorry. No such user exists." in msg:
            self._append_error("No existe ese usuario.")
            return

        if ": " in msg:
            after_ts  = msg[9:] if len(msg) > 9 else msg
            colon_idx = after_ts.find(": ")
            if colon_idx != -1:
                sender = after_ts[:colon_idx].strip()
                text   = after_ts[colon_idx + 2:].strip()
                my_username = self.client.username if self.client else ""
                tag    = "mine"  if sender == my_username else "other"
                label  = "Tu"    if sender == my_username else sender
                self._append_message(label, text, tag)
            else:
                self._append_system(msg)
            return

        self._append_system(msg)

    # ======================================================
    # UI HELPERS
    # ======================================================

    def _append_system(self, text):
        self._append(text + "\n", "system")

    def _append_error(self, text):
        self._append(text + "\n", "error")

    def _append_message(self, sender, text, tag):
        self._append(f"{sender}: {text}\n", tag)

    def _append(self, text, tag):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, text, tag)
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def _on_close(self):
        self.running = False
        if self.client:
            try:
                self.client.send_message(ChatMessage(ChatMessage.LOGOUT, ""))
            except:
                pass
            self.client.disconnect()
        self.root.destroy()


# ======================================================
# CLIENT WRAPPER
# ======================================================

class ClientGUIWrapper:
    def __init__(self, server, port, username, callback):
        self.server   = server
        self.port     = port
        self.username = username
        self.callback = callback
        self.socket   = None
        self.listener = None

    def start(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server, self.port))
        except Exception:
            return False

        # Enviar nombre de usuario
        try:
            send_packet(self.socket, pickle.dumps(self.username))
        except:
            self.disconnect()
            return False

        # Esperar primera respuesta del servidor (USERNAME_TAKEN o primer msg)
        try:
            self.socket.settimeout(3.0)
            first = pickle.loads(recv_packet(self.socket))
            self.socket.settimeout(None)

            if first == "USERNAME_TAKEN":
                self.disconnect()
                return "USERNAME_TAKEN"

            # Primer mensaje válido → procesarlo
            self.callback(first)
        except socket.timeout:
            self.socket.settimeout(None)
        except Exception:
            self.disconnect()
            return False

        self.listener = threading.Thread(target=self._listen, daemon=True)
        self.listener.start()
        return True

    def _listen(self):
        while True:
            try:
                payload = pickle.loads(recv_packet(self.socket))
                self.callback(payload)
            except:
                self.callback("*** Conexion con el servidor cerrada ***")
                break

    def send_message(self, msg):
        try:
            send_packet(self.socket, pickle.dumps(msg))
        except:
            pass

    def disconnect(self):
        try:
            if self.socket:
                self.socket.close()
                self.socket = None
        except:
            pass


if __name__ == "__main__":
    ClientGUI()