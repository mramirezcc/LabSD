from flask import Flask, render_template, request, jsonify, session
from two_phase_commit import TwoPhaseCommit
import psycopg2
import psycopg2.extras
import os
import logging
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sistema_bancario_cooperativo_2026'
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de conexiones (igual que en coordinator.py)
DB_CONFIGS = {
    'arequipa': {
        'host': os.getenv('DB_AR EQUIPA_HOST', 'localhost'),
        'port': 5433,
        'database': 'banco_arequipa',
        'user': 'admin',
        'password': 'admin123'
    },
    'cusco': {
        'host': os.getenv('DB_CUSCO_HOST', 'localhost'),
        'port': 5434,
        'database': 'banco_cusco',
        'user': 'admin',
        'password': 'admin123'
    },
    'trujillo': {
        'host': os.getenv('DB_TRUJILLO_HOST', 'localhost'),
        'port': 5435,
        'database': 'banco_trujillo',
        'user': 'admin',
        'password': 'admin123'
    },
    'logs': {
        'host': os.getenv('DB_LOGS_HOST', 'localhost'),
        'port': 5436,
        'database': 'banco_logs',
        'user': 'admin',
        'password': 'admin123'
    }
}

coordinator = TwoPhaseCommit(DB_CONFIGS['logs'])

# Variables para simulación de fallos
failure_mode = {
    'enabled': False,
    'type': None,  # 'network', 'node_crash', 'timeout'
    'affected_node': None
}

@app.route('/')
def index():
    """Página principal con interfaz gráfica"""
    return render_template('index.html')

@app.route('/api/dashboard')
def dashboard():
    """Obtener estado actual de todos los nodos"""
    result = {
        'nodes': {},
        'transactions': [],
        'system_health': 'healthy'
    }
    
    for nodo in ['arequipa', 'cusco', 'trujillo']:
        try:
            conn = psycopg2.connect(**DB_CONFIGS[nodo])
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT numero_cuenta, titular, saldo, ciudad 
                FROM cuentas 
                ORDER BY id
            """)
            cuentas = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            result['nodes'][nodo] = {
                'status': 'online',
                'cuentas': cuentas,
                'total_cuentas': len(cuentas),
                'saldo_total': sum(c['saldo'] for c in cuentas)
            }
        except Exception as e:
            result['nodes'][nodo] = {'status': 'offline', 'error': str(e)}
            result['system_health'] = 'degraded'
    
    # Obtener transacciones recientes del log
    try:
        conn = psycopg2.connect(**DB_CONFIGS['logs'])
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""
            SELECT transaccion_id, estado, origen_nodo, destino_nodo, 
                   monto, timestamp_inicio, timestamp_fin
            FROM transacciones_2pc 
            ORDER BY timestamp_inicio DESC 
            LIMIT 10
        """)
        result['transactions'] = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error obteniendo transacciones: {e}")
    
    return jsonify(result)

@app.route('/api/transfer', methods=['POST'])
def transfer():
    """Realizar transferencia distribuida"""
    global failure_mode
    
    data = request.json
    cuenta_origen = data.get('cuenta_origen')
    cuenta_destino = data.get('cuenta_destino')
    monto = float(data.get('monto', 0))
    simular_fallo = data.get('simular_fallo', None)
    
    if not all([cuenta_origen, cuenta_destino, monto]):
        return jsonify({'error': 'Faltan parámetros'}), 400
    
    if monto <= 0:
        return jsonify({'error': 'Monto debe ser positivo'}), 400
    
    # Configurar simulación de fallo si se solicita
    if simular_fallo and simular_fallo != 'none':
        failure_mode['enabled'] = True
        failure_mode['type'] = simular_fallo
        logger.warning(f"⚠️ SIMULACIÓN ACTIVADA: {simular_fallo}")
    
    try:
        # Ejecutar transacción 2PC
        success, message, tx_id = coordinator.execute_transaction_with_failure(
            DB_CONFIGS['arequipa'],
            DB_CONFIGS['cusco'],
            cuenta_origen,
            cuenta_destino,
            monto,
            failure_mode if failure_mode['enabled'] else None
        )
        
        return jsonify({
            'success': success,
            'message': message,
            'transaction_id': tx_id,
            'failure_simulated': failure_mode['enabled']
        })
        
    except Exception as e:
        logger.error(f"Error en transferencia: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        # Resetear simulación
        failure_mode = {'enabled': False, 'type': None, 'affected_node': None}

@app.route('/api/failure/simulate', methods=['POST'])
def simulate_failure():
    """Activar simulación de fallo específico"""
    global failure_mode
    data = request.json
    failure_mode['enabled'] = True
    failure_mode['type'] = data.get('type')
    failure_mode['affected_node'] = data.get('node')
    
    return jsonify({
        'status': 'simulation_active',
        'type': failure_mode['type'],
        'node': failure_mode['affected_node']
    })

@app.route('/api/failure/reset', methods=['POST'])
def reset_failure():
    """Desactivar simulación de fallos"""
    global failure_mode
    failure_mode = {'enabled': False, 'type': None, 'affected_node': None}
    return jsonify({'status': 'simulation_reset'})

@app.route('/api/recovery/execute', methods=['POST'])
def execute_recovery():
    """Ejecutar recuperación post-fallo"""
    try:
        conn = psycopg2.connect(**DB_CONFIGS['logs'])
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Buscar transacciones inconclusas
        cursor.execute("""
            SELECT * FROM transacciones_2pc 
            WHERE estado IN ('PREPARING', 'COMMITTING', 'INIT')
            AND timestamp_fin IS NULL
        """)
        
        pending = cursor.fetchall()
        recovered = []
        
        for tx in pending:
            logger.info(f"Recuperando transacción: {tx['transaccion_id']}")
            # Verificar votos
            cursor.execute("""
                SELECT voto FROM participantes_votos 
                WHERE transaccion_id = %s
            """, (tx['transaccion_id'],))
            votos = [row['voto'] for row in cursor.fetchall()]
            
            if votos and all(v == 'YES' for v in votos):
                recovered.append({
                    'id': tx['transaccion_id'],
                    'action': 'COMMITTED'
                })
            else:
                recovered.append({
                    'id': tx['transaccion_id'],
                    'action': 'ABORTED'
                })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'recovery_completed',
            'recovered_count': len(recovered),
            'transactions': recovered
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)