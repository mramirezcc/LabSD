"""
Lanzador del Sistema de Seguridad - Logi Market Peru S.A.C.
Lab11 - Seguridad Informatica en Sistemas Distribuidos

Inicia el API Gateway HTTPS con TLS, JWT, RBAC y auditoria.
Luego lanza la interfaz grafica Tkinter para interactuar con el sistema.
"""
import subprocess
import threading
import time
import sys
import os
import signal
import atexit
import socket
from datetime import datetime

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =============================================================================
# Configuracion
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_HOST = "127.0.0.1"
API_PORT = 8443
API_URL = f"https://{API_HOST}:{API_PORT}"
CERT_DIR = os.path.join(BASE_DIR, "certs")
SERVER_CERT = os.path.join(CERT_DIR, "server-cert.pem")
SERVER_KEY = os.path.join(CERT_DIR, "server-key.pem")

processes = []
shutdown_flag = False


class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def cprint(color, msg):
    print(f"{color}{msg}{bcolors.ENDC}")


# =============================================================================
# Utilidades de red
# =============================================================================

def is_port_open(host, port):
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def kill_port(port):
    try:
        for conn in subprocess.check_output(
            ["lsof", "-i", f"tcp:{port}"], stderr=subprocess.DEVNULL
        ).decode().splitlines()[1:]:
            pid = int(conn.split()[1])
            os.kill(pid, signal.SIGTERM)
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError, ValueError):
        pass


def wait_for_service(url, timeout=30, interval=1):
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(url, verify=False, timeout=2)
            if resp.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(interval)
    return False


# =============================================================================
# Inicio del servidor
# =============================================================================

def start_api_server():
    cprint(bcolors.BLUE, "[SERVIDOR] Iniciando API Gateway HTTPS en puerto 8443...")

    python_exe = sys.executable

    proc = subprocess.Popen(
        [python_exe, os.path.join(BASE_DIR, "app.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=BASE_DIR,
    )
    processes.append(proc)

    def log_output():
        for line in iter(proc.stdout.readline, ""):
            if shutdown_flag:
                break
            line = line.rstrip()
            if line:
                print(f"  {bcolors.YELLOW}[API]{bcolors.ENDC} {line}")
        proc.stdout.close()

    threading.Thread(target=log_output, daemon=True).start()

    cprint(bcolors.BLUE, f"[SERVIDOR] Esperando que {API_URL}/api/health responda...")
    if wait_for_service(f"{API_URL}/api/health", timeout=30):
        cprint(bcolors.GREEN, "[SERVIDOR] API Gateway listo y respondiendo.")
        return True
    else:
        cprint(bcolors.RED, "[ERROR] El servidor no respondio en 30 segundos.")
        return False


# =============================================================================
# Inicio de la GUI
# =============================================================================

def start_gui():
    cprint(bcolors.BLUE, "[GUI] Iniciando interfaz grafica Tkinter...")
    from gui.app import main as gui_main
    gui_main()


# =============================================================================
# Limpieza al cerrar
# =============================================================================

def shutdown():
    global shutdown_flag
    shutdown_flag = True
    cprint(bcolors.YELLOW, "\n[SHUTDOWN] Cerrando servicios...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            try:
                proc.kill()
            except OSError:
                pass
    cprint(bcolors.GREEN, "[SHUTDOWN] Servicios detenidos.")


atexit.register(shutdown)


def signal_handler(sig, frame):
    shutdown()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# =============================================================================
# Main
# =============================================================================

def main():
    print("=" * 60)
    cprint(bcolors.BOLD + bcolors.BLUE,
           "  Logi Market Peru S.A.C. - Sistema de Seguridad Distribuida")
    cprint(bcolors.BOLD + bcolors.BLUE,
           "  Lab11: Seguridad Informatica en Sistemas Distribuidos")
    print("=" * 60)
    print(f"  Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Directorio base: {BASE_DIR}")
    print("=" * 60)
    print("")

    # Verificar o generar certificados
    if not (os.path.exists(SERVER_CERT) and os.path.exists(SERVER_KEY)):
        cprint(bcolors.YELLOW, "[CERTS] Certificados no encontrados. Generando automaticamente...")
        try:
            import ipaddress
            from generate_certs import generar_certificados
            generar_certificados()
            cprint(bcolors.GREEN, "[CERTS] Certificados generados exitosamente.")
        except Exception as e:
            cprint(bcolors.RED, f"[ERROR] No se pudieron generar los certificados: {e}")
            cprint(bcolors.RED, "[ERROR] Ejecute manualmente: python generate_certs.py")
            return
    else:
        cprint(bcolors.GREEN, "[CERTS] Certificados encontrados en ./certs/")

    # Liberar puerto si esta ocupado
    if is_port_open(API_HOST, API_PORT):
        cprint(bcolors.YELLOW, f"[PUERTO] Puerto {API_PORT} ocupado. Liberando...")
        kill_port(API_PORT)
        time.sleep(1)

    # Iniciar API Gateway
    if not start_api_server():
        cprint(bcolors.RED, "[ERROR] No se pudo iniciar el API Gateway. Abortando.")
        shutdown()
        return

    print("")
    cprint(bcolors.GREEN, "  Servidor listo. Iniciando GUI...")
    cprint(bcolors.BLUE, f"  API: {API_URL}")
    cprint(bcolors.BLUE, "  Usuarios: admin/Admin@2026! | operador/Oper@dor#2026 | cliente/Client3$2026")
    print("")

    # Lanzar GUI
    start_gui()

    shutdown()


if __name__ == "__main__":
    main()
