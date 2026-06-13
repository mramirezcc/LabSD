"""
Main Launcher - LogiFresh S.A.
Inicia todos los microservicios y la interfaz grafica.
Gestion profesional de procesos con health checks y graceful shutdown.
"""
import subprocess
import threading
import time
import sys
import os
import socket
import signal
import atexit
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SERVICES = [
    {"module": "services.inventario",   "name": "Inventario",   "port": 5002, "color": "92"},
    {"module": "services.facturacion",  "name": "Facturacion",  "port": 5003, "color": "93"},
    {"module": "services.transporte",   "name": "Transporte",   "port": 5004, "color": "94"},
    {"module": "services.notificaciones","name": "Notificaciones","port": 5005, "color": "95"},
    {"module": "services.pedidos",      "name": "Pedidos",      "port": 5001, "color": "96"},
]

processes = []
shutdown_flag = False

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def cprint(msg, color=bcolors.ENDC):
    print(f"{color}{msg}{bcolors.ENDC}")

def is_port_open(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def kill_port(port):
    try:
        if sys.platform == "win32":
            subprocess.run(
                f'for /f "tokens=5" %a in (\'netstat -ano ^| findstr :{port} ^| findstr LISTENING\') do taskkill /F /PID %a >nul 2>&1',
                shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        pass

def start_service(svc):
    env = os.environ.copy()
    env["PYTHONPATH"] = BASE_DIR
    proc = subprocess.Popen(
        [sys.executable, "-m", svc["module"]],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        env=env,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )
    return proc

def wait_for_service(port, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"http://127.0.0.1:{port}/health", timeout=1)
            if r.status_code == 200:
                return True
        except:
            pass
        time.sleep(0.3)
    return False

def shutdown():
    global shutdown_flag
    if shutdown_flag:
        return
    shutdown_flag = True

    print(f"\n{bcolors.DIM}{'='*60}{bcolors.ENDC}")
    cprint("  Deteniendo servicios...", bcolors.YELLOW)

    for name, proc, port in processes:
        try:
            proc.terminate()
            proc.wait(timeout=3)
            cprint(f"  [OK] {name:20s} detenido", bcolors.GREEN)
        except:
            try:
                proc.kill()
                cprint(f"  [OK] {name:20s} forzado", bcolors.YELLOW)
            except:
                cprint(f"  [--] {name:20s} ya detenido", bcolors.DIM)

    cprint(f"  {'='*60}", bcolors.DIM)
    cprint("  LogiFresh S.A. - Sistema detenido.", bcolors.CYAN)

atexit.register(shutdown)

def main():
    print()
    cprint(f"  {'='*60}", bcolors.CYAN)
    cprint(f"  {bcolors.BOLD}LogiFresh S.A. - Sistema Distribuido de Distribucion{bcolors.ENDC}", bcolors.CYAN)
    cprint(f"  Alimentos Refrigerados | Arquitectura de Microservicios", bcolors.DIM)
    cprint(f"  {'='*60}", bcolors.CYAN)
    print(f"  {bcolors.DIM}Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{bcolors.ENDC}")
    print(f"  {bcolors.DIM}Directorio: {BASE_DIR}{bcolors.ENDC}")
    print()

    for svc in SERVICES:
        if is_port_open("127.0.0.1", svc["port"]):
            cprint(f"  [!] Puerto {svc['port']} ocupado. Liberando...", bcolors.YELLOW)
            kill_port(svc["port"])
            time.sleep(0.3)

    print(f"  {bcolors.BOLD}Iniciando microservicios...{bcolors.ENDC}")

    all_started = True
    for svc in SERVICES:
        cprint(f"  [..] {svc['name']:20s} :{svc['port']} iniciando...", bcolors.DIM)
        proc = start_service(svc)
        processes.append((svc["name"], proc, svc["port"]))
        time.sleep(0.5)

    print()
    print(f"  {bcolors.BOLD}Verificando health checks...{bcolors.ENDC}")

    for name, proc, port in processes:
        if wait_for_service(port, timeout=10):
            cprint(f"  [{bcolors.GREEN}\u2713{bcolors.ENDC}] {name:20s} :{port}  ONLINE", bcolors.GREEN)
        else:
            cprint(f"  [{bcolors.RED}\u2717{bcolors.ENDC}] {name:20s} :{port}  OFFLINE", bcolors.RED)
            all_started = False

    print()
    if all_started:
        cprint(f"  {bcolors.GREEN}{bcolors.BOLD} Todos los servicios iniciados correctamente.{bcolors.ENDC}", bcolors.GREEN)
    else:
        cprint(f"  {bcolors.YELLOW}{bcolors.BOLD} AVISO: Algunos servicios no respondieron.{bcolors.ENDC}", bcolors.YELLOW)

    cprint(f"  {bcolors.DIM}Abriendo interfaz grafica...{bcolors.ENDC}")
    cprint(f"  {bcolors.DIM}{'='*60}{bcolors.ENDC}")
    print()

    try:
        import tkinter as tk
        from gui.app import LogiFreshApp
        root = tk.Tk()
        app = LogiFreshApp(root)
        root.mainloop()
    except Exception as e:
        cprint(f"  Error al iniciar la GUI: {e}", bcolors.RED)

if __name__ == "__main__":
    main()
