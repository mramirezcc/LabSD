import socket
import threading
import pickle
import struct
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime

from chat_message import ChatMessage


# ── Helpers de red: enviar/recibir con prefijo de longitud (4 bytes) ──────────
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


class ServerGUI:
    WINDOW_TITLE = "Chat Server - Sistemas Distribuidos"
    unique_id = 0

    def __init__(self):
        self.port = 1500
        self.al = []
        self.keep_going = True
        self.notif = " *** "
        self.server_socket = None

        self.root = tk.Tk()
        self.root.title(self.WINDOW_TITLE)
        self.root.geometry("700x500")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.resizable(True, True)

        self._build_control_frame()
        self._build_log_frame()
        self._build_client_list_frame()

        self.root.mainloop()

    def _build_control_frame(self):
        frame = tk.LabelFrame(self.root, text="Control", padx=10, pady=5)
        frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(frame, text="Puerto:").pack(side=tk.LEFT)
        self.port_entry = tk.Entry(frame, width=8)
        self.port_entry.insert(0, "1500")
        self.port_entry.pack(side=tk.LEFT, padx=5)

        self.start_btn = tk.Button(
            frame, text="Iniciar Servidor", command=self._toggle_server,
            bg="#4CAF50", fg="white", width=14
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(frame, text="Detenido", fg="red")
        self.status_label.pack(side=tk.LEFT, padx=15)

        self.client_count_label = tk.Label(frame, text="Clientes: 0")
        self.client_count_label.pack(side=tk.RIGHT, padx=10)

    def _build_log_frame(self):
        frame = tk.LabelFrame(self.root, text="Log del Servidor", padx=5, pady=5)
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_area = scrolledtext.ScrolledText(
            frame, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 10)
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)

        self.log_area.tag_config("info",    foreground="black")
        self.log_area.tag_config("join",    foreground="green")
        self.log_area.tag_config("leave",   foreground="orange")
        self.log_area.tag_config("error",   foreground="red")
        self.log_area.tag_config("private", foreground="purple")
        self.log_area.tag_config("file",    foreground="blue")

    def _build_client_list_frame(self):
        frame = tk.LabelFrame(self.root, text="Clientes Conectados", padx=5, pady=5)
        frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        self.client_listbox = tk.Listbox(frame, height=6, font=("Consolas", 10))
        self.client_listbox.pack(fill=tk.BOTH, expand=True)

    def _toggle_server(self):
        if self.server_socket:
            self._stop_server()
        else:
            self._start_server()

    def _start_server(self):
        try:
            self.port = int(self.port_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Puerto invalido.")
            return

        self.keep_going = True
        threading.Thread(target=self._server_loop, daemon=True).start()

        self.start_btn.config(text="Detener Servidor", bg="#f44336")
        self.port_entry.config(state=tk.DISABLED)
        self.status_label.config(text="Ejecutando...", fg="green")

    def _stop_server(self):
        self.keep_going = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None

        for ct in self.al:
            try:
                ct.socket.close()
            except:
                pass
        self.al.clear()

        self.start_btn.config(text="Iniciar Servidor", bg="#4CAF50")
        self.port_entry.config(state=tk.NORMAL)
        self.status_label.config(text="Detenido", fg="red")
        self.client_count_label.config(text="Clientes: 0")
        self.client_listbox.delete(0, tk.END)
        self._log("*** Servidor detenido ***", "info")

    def _server_loop(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("0.0.0.0", self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)
            self._log(f"Servidor esperando conexiones en puerto {self.port}.", "info")

            while self.keep_going:
                try:
                    client_socket, address = self.server_socket.accept()
                    self._log(f"Conexion aceptada: {address}", "info")
                    t = ClientThreadGUI(self, client_socket, address)
                    self.al.append(t)
                    t.start()
                except socket.timeout:
                    continue
                except:
                    if self.keep_going:
                        self._log("Error aceptando conexion.", "error")
                    break
        except Exception as e:
            self._log(f"Error en el servidor: {e}", "error")
        finally:
            if self.server_socket:
                try:
                    self.server_socket.close()
                except:
                    pass

    # ======================================================
    # BROADCAST / MENSAJES
    # ======================================================

    def broadcast(self, message):
        time = datetime.now().strftime("%H:%M:%S")
        message_lf = f"{time} {message}\n"
        self._log(message, "info")
        disconnected = []
        for ct in self.al:
            if not ct.write_msg(message_lf):
                disconnected.append(ct)
        for ct in disconnected:
            self._remove_client(ct)

    def send_private(self, sender, target_username, message):
        time = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"{time} [PRIVADO] {sender}: {message}"
        found = False
        for ct in self.al:
            if ct.username == target_username:
                ct.write_msg(formatted_msg)
                found = True
                break
        if found:
            for ct in self.al:
                if ct.username == sender:
                    ct.write_msg(formatted_msg)
            self._log(f"Privado: {sender} -> {target_username}: {message}", "private")
        return found

    def send_file(self, sender_thread, target_username, filename, filedata):
        """Reenvía un archivo. target_username=None → todos menos el emisor."""
        size_kb = len(filedata) / 1024

        # El ChatMessage que viaja al receptor lleva sender en extra
        cm = ChatMessage(
            ChatMessage.FILE,
            filename,
            extra={"sender": sender_thread.username, "data": filedata}
        )
        raw = pickle.dumps(cm)

        if target_username:
            found = False
            for ct in self.al:
                if ct.username == target_username:
                    ct.write_raw(raw)
                    found = True
                    break
            if found:
                sender_thread.write_raw(raw)   # confirmación al emisor
                self._log(
                    f"[ARCHIVO] {sender_thread.username} -> {target_username}: "
                    f"{filename} ({size_kb:.1f} KB)", "file"
                )
            else:
                sender_thread.write_msg(
                    f"*** Error: El usuario '{target_username}' no existe ***"
                )
        else:
            self._log(
                f"[ARCHIVO] {sender_thread.username} -> todos: "
                f"{filename} ({size_kb:.1f} KB)", "file"
            )
            disconnected = []
            for ct in self.al:
                if ct is not sender_thread:
                    if not ct.write_raw(raw):
                        disconnected.append(ct)
            sender_thread.write_raw(raw)   # copia al emisor
            for ct in disconnected:
                self._remove_client(ct)

    def _remove_client(self, ct):
        if ct in self.al:
            self.al.remove(ct)
            self._log(f"{ct.username} desconectado y removido.", "leave")
            self._update_client_list()

    def remove(self, thread):
        if thread in self.al:
            name = thread.username
            self.al.remove(thread)
            self._log(f"{name} ha salido del chat.", "leave")
            self._update_client_list()
            self.broadcast(
                self.notif + name + " has left the chat room." + self.notif
            )

    def is_username_taken(self, username):
        for ct in self.al:
            if ct.username.lower() == username.lower():
                return True
        return False

    def _update_client_list(self):
        def _update():
            self.client_listbox.delete(0, tk.END)
            for ct in self.al:
                self.client_listbox.insert(
                    tk.END, f"{ct.username} ({ct.address[0]}:{ct.address[1]})"
                )
            self.client_count_label.config(text=f"Clientes: {len(self.al)}")
        self.root.after(0, _update)

    def _log(self, msg, tag="info"):
        def _append():
            self.log_area.config(state=tk.NORMAL)
            self.log_area.insert(tk.END, msg + "\n", tag)
            self.log_area.see(tk.END)
            self.log_area.config(state=tk.DISABLED)
        self.root.after(0, _append)

    def _on_close(self):
        self._stop_server()
        self.root.destroy()


# ======================================================
# CLIENT THREAD
# ======================================================

class ClientThreadGUI(threading.Thread):
    def __init__(self, server, socket_client, address):
        threading.Thread.__init__(self, daemon=True)
        ServerGUI.unique_id += 1
        self.id = ServerGUI.unique_id
        self.server = server
        self.socket = socket_client
        self.address = address
        self.username = ""
        self.date = str(datetime.now())

    def run(self):
        try:
            username = pickle.loads(recv_packet(self.socket))
        except:
            self.close()
            return

        if self.server.is_username_taken(username):
            try:
                send_packet(self.socket, pickle.dumps("USERNAME_TAKEN"))
            except:
                pass
            self.server._log(f"Nombre duplicado: '{username}'", "error")
            if self in self.server.al:
                self.server.al.remove(self)
            self.close()
            return

        self.username = username
        self.server._log(f"'{self.username}' se ha unido al chat.", "join")
        self.server._update_client_list()

        existing = [ct.username for ct in self.server.al if ct.username != self.username]
        if existing:
            self.write_msg("EXISTING_USERS:" + ",".join(existing))

        self.server.broadcast(
            self.server.notif + self.username +
            " has joined the chat room." + self.server.notif
        )

        while True:
            try:
                cm = pickle.loads(recv_packet(self.socket))
            except:
                break

            msg_type = cm.get_type()
            message  = cm.get_message()

            if msg_type == ChatMessage.MESSAGE:
                if message.startswith("@"):
                    parts = message.split(" ", 1)
                    target = parts[0][1:]
                    body   = parts[1] if len(parts) > 1 else ""
                    if not self.server.send_private(self.username, target, body):
                        self.write_msg(f"*** Error: El usuario '{target}' no existe ***")
                else:
                    self.server.broadcast(self.username + ": " + message)

            elif msg_type == ChatMessage.FILE:
                extra  = cm.get_extra() or {}
                target = extra.get("target")    # None = broadcast
                data   = extra.get("data", b"")
                self.server.send_file(self, target, message, data)

            elif msg_type == ChatMessage.LOGOUT:
                self.server._log(f"{self.username} se desconecto (LOGOUT).", "leave")
                break

            elif msg_type == ChatMessage.WHOISIN:
                self.write_msg(
                    "List of the users connected at " +
                    datetime.now().strftime("%H:%M:%S") + "\n"
                )
                for i, ct in enumerate(self.server.al, 1):
                    self.write_msg(f"{i}) {ct.username} since {ct.date}")

        self.server.remove(self)
        self.close()

    def write_msg(self, msg: str) -> bool:
        return self.write_raw(pickle.dumps(msg))

    def write_raw(self, raw: bytes) -> bool:
        try:
            send_packet(self.socket, raw)
            return True
        except:
            return False

    def close(self):
        try:
            self.socket.close()
        except:
            pass


if __name__ == "__main__":
    ServerGUI()