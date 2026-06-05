import psycopg2
import time

# Configuración de conexiones
DB_AREQUIPA = {
    "dbname": "almacen_arequipa", "user": "postgres", 
    "password": "password123", "host": "localhost", "port": "5433"
}

DB_LIMA = {
    "dbname": "almacen_lima", "user": "postgres", 
    "password": "password123", "host": "localhost", "port": "5434"
}

def ejecutar_transferencia(cantidad, simular_fallo_lima=False):
    conn_aqp = None
    conn_lima = None
    
    print(f"\n=== INICIANDO TRANSFERENCIA DE {cantidad} UNIDADES ===")
    if simular_fallo_lima:
        print("[ALERTA] Modo: Simulación de fallo en Nodo Lima activo.")

    try:
        # 1. CONEXIÓN E INICIO DE TRANSACCIÓN 
        conn_aqp = psycopg2.connect(**DB_AREQUIPA)
        conn_lima = psycopg2.connect(**DB_LIMA)
        
        # Desactivamos el autocommit para controlar la transacción manualmente
        conn_aqp.autocommit = False
        conn_lima.autocommit = False
        
        cursor_aqp = conn_aqp.cursor()
        cursor_lima = conn_lima.cursor()
        
        # --- PASO A: Verificar Stock en Origen (Arequipa) ---
        cursor_aqp.execute("SELECT stock FROM inventario WHERE producto = 'Paracetamol';")
        stock_aqp = cursor_aqp.fetchone()[0]
        print(f"[Arequipa] Stock actual disponible: {stock_aqp}")
        
        if stock_aqp < cantidad:
            raise Exception("Stock insuficiente en el nodo de origen (Arequipa).")
        
        # --- PASO B: Modificar Stock en Origen ---
        print("[Arequipa] Descontando stock...")
        cursor_aqp.execute(
            "UPDATE inventario SET stock = stock - %s WHERE producto = 'Paracetamol';", 
            (cantidad,)
        )
        
        # --- PASO C: Modificar Stock en Destino (Lima) ---
        if simular_fallo_lima:
            # Simulamos que el nodo Lima deja de responder o se cae la red antes de procesar
            raise psycopg2.OperationalError("Error de conexión simulado: El nodo Lima no responde.")
        
        print("[Lima] Incrementando stock...")
        cursor_lima.execute(
            "UPDATE inventario SET stock = stock + %s WHERE producto = 'Paracetamol';", 
            (cantidad,)
        )
        
        # FASE 2: COMMIT GLOBAL 
        print("\n--> FASE 2: Ambos nodos listos. Ejecutando COMMIT global...")
        conn_aqp.commit()
        conn_lima.commit()
        print("¡Transacción Distribuida Exitosa!")
        
    except Exception as e:
        # FASE 2: ROLLBACK GLOBAL 
        print(f"\ [ERROR DETECTADO]: {e}")
        print("--> FASE 2: Ejecutando ROLLBACK global para garantizar Atomicidad...")
        
        if conn_aqp:
            conn_aqp.rollback()
            print("[Arequipa] Cambios revertidos.")
        if conn_lima:
            try:
                conn_lima.rollback()
                print("[Lima] Cambios revertidos.")
            except:
                print("[Lima] No se pudo hacer rollback en Lima (nodo inaccesible), pero se garantizó que no se guardó nada.")
                
    finally:
        # Cerrar conexiones de forma segura
        if conn_aqp: cursor_aqp.close(); conn_aqp.close()
        if conn_lima: cursor_lima.close(); conn_lima.close()

def consultar_stocks():
    """Función auxiliar para ver cómo quedaron los datos"""
    print("\n--- ESTADO ACTUAL DEL STOCK EN LOS NODOS ---")
    try:
        conn = psycopg2.connect(**DB_AREQUIPA)
        cur = conn.cursor()
        cur.execute("SELECT stock FROM inventario WHERE producto = 'Paracetamol';")
        print(f"Nodo Arequipa Stock: {cur.fetchone()[0]}")
        cur.close(); conn.close()
        
        conn = psycopg2.connect(**DB_LIMA)
        cur = conn.cursor()
        cur.execute("SELECT stock FROM inventario WHERE producto = 'Paracetamol';")
        print(f"Nodo Lima Stock: {cur.fetchone()[0]}")
        cur.close(); conn.close()
    except Exception as e:
        print(f"Error al consultar stocks: {e}")

# ==========================================
# EJECUCIÓN DE LOS EJERCICIOS
# ==========================================
if __name__ == "__main__":
    # Ver estado inicial
    consultar_stocks()
    
    # --- EJERCICIO 1: Transferencia Exitosa ---
    ejecutar_transferencia(cantidad=20, simular_fallo_lima=False)
    consultar_stocks()
    
    # --- EJERCICIO 2: Simulación de Fallo ---
    # Intentamos transferir 10 unidades pero simulando que Lima se cae
    ejecutar_transferencia(cantidad=10, simular_fallo_lima=True)
    consultar_stocks()