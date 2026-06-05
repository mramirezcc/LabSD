from flask import Flask, render_template, request, jsonify
import psycopg2

app = Flask(__name__)

# Configuración de conexiones a los contenedores de Docker
DB_AREQUIPA = {
    "dbname": "almacen_arequipa", "user": "postgres", 
    "password": "password123", "host": "localhost", "port": "5433"
}
DB_LIMA = {
    "dbname": "almacen_lima", "user": "postgres", 
    "password": "password123", "host": "localhost", "port": "5434"
}

def obtener_stocks():
    """Consulta el stock actual de ambos nodos de forma independiente"""
    stock = {"arequipa": "Inaccesible", "lima": "Inaccesible"}
    try:
        conn = psycopg2.connect(**DB_AREQUIPA)
        cur = conn.cursor()
        cur.execute("SELECT stock FROM inventario WHERE producto = 'Paracetamol';")
        stock["arequipa"] = cur.fetchone()[0]
        cur.close(); conn.close()
    except: pass

    try:
        conn = psycopg2.connect(**DB_LIMA)
        cur = conn.cursor()
        cur.execute("SELECT stock FROM inventario WHERE producto = 'Paracetamol';")
        stock["lima"] = cur.fetchone()[0]
        cur.close(); conn.close()
    except: pass
    
    return stock

@app.route('/')
def inicio():
    stocks = obtener_stocks()
    return render_template('index.html', stocks=stocks)

@app.route('/transferir', methods=['POST'])
def transferir():
    datos = request.json
    cantidad = int(datos.get('cantidad', 0))
    simular_fallo = datos.get('simular_fallo', False)
    
    conn_aqp = None
    conn_lima = None
    bitacora = []

    try:
        bitacora.append("Fase 1: Iniciando conexión con los nodos...")
        conn_aqp = psycopg2.connect(**DB_AREQUIPA)
        conn_lima = psycopg2.connect(**DB_LIMA)
        
        conn_aqp.autocommit = False
        conn_lima.autocommit = False
        
        cur_aqp = conn_aqp.cursor()
        cur_lima = conn_lima.cursor()

        # Paso A: Verificar Stock
        cur_aqp.execute("SELECT stock FROM inventario WHERE producto = 'Paracetamol';")
        stock_aqp = cur_aqp.fetchone()[0]
        
        if stock_aqp < cantidad:
            raise Exception(f"Stock insuficiente en Arequipa ({stock_aqp} disponibles).")

        # Paso B: Descontar Origen
        bitacora.append(f"[Arequipa] Solicitud de descuento aprobada. Restando {cantidad} unidades...")
        cur_aqp.execute("UPDATE inventario SET stock = stock - %s WHERE producto = 'Paracetamol';", (cantidad,))

        # Paso C: Simulación del fallo (Ejercicio 2)
        if simular_fallo:
            bitacora.append("⚠️ [Simulación] Cortando comunicación de red con el Nodo Lima...")
            raise psycopg2.OperationalError("Error de comunicación: El nodo de destino no responde.")

        # Paso D: Incrementar Destino
        bitacora.append(f"[Lima] Solicitud de incremento aprobada. Sumando {cantidad} unidades...")
        cur_lima.execute("UPDATE inventario SET stock = stock + %s WHERE producto = 'Paracetamol';", (cantidad,))

        # FASE 2: Commit Global
        bitacora.append("Fase 2: Todos los nodos listos (Voto SÍ). Ejecutando COMMIT global...")
        conn_aqp.commit()
        conn_lima.commit()
        bitacora.append("¡Transacción distribuida completada con ÉXITO!")
        exito = True

    except Exception as e:
        exito = False
        bitacora.append(f"ERROR: {str(e)}")
        bitacora.append("Fase 2: Fallo detectado. Ejecutando ROLLBACK global...")
        
        if conn_aqp:
            conn_aqp.rollback()
            bitacora.append("[Arequipa] Cambios revertidos (Rollback exitoso).")
        if conn_lima and not simular_fallo:
            conn_lima.rollback()
            bitacora.append("[Lima] Cambios revertidos (Rollback exitoso).")
        elif simular_fallo:
            bitacora.append("[Lima] Nodo caído. No requiere rollback local (el bloqueo expirará).")

    finally:
        if conn_aqp: conn_aqp.close()
        if conn_lima: conn_lima.close()

    return jsonify({"exito": exito, "bitacora": bitacora, "stocks": obtener_stocks()})

if __name__ == '__main__':
    app.run(debug=True, port=5000)