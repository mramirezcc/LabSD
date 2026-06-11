-- Base de datos: banco_logs
-- Recuperación y trazabilidad distribuida

CREATE TABLE IF NOT EXISTS transacciones_2pc (
    id SERIAL PRIMARY KEY,
    transaccion_id VARCHAR(50) UNIQUE NOT NULL,
    estado VARCHAR(20), -- 'INIT', 'PREPARING', 'COMMITTING', 'COMMITTED', 'ABORTING', 'ABORTED'
    origen_nodo VARCHAR(50),
    destino_nodo VARCHAR(50),
    cuenta_origen VARCHAR(20),
    cuenta_destino VARCHAR(20),
    monto DECIMAL(15,2),
    fase_actual VARCHAR(20),
    timestamp_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timestamp_fin TIMESTAMP,
    error_mensaje TEXT
);

CREATE TABLE IF NOT EXISTS participantes_votos (
    id SERIAL PRIMARY KEY,
    transaccion_id VARCHAR(50),
    participante_nodo VARCHAR(50),
    voto VARCHAR(10), -- 'YES', 'NO'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recovery_checkpoints (
    id SERIAL PRIMARY KEY,
    checkpoint_id VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_sistema JSONB
);

-- Índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_transacciones_estado ON transacciones_2pc(estado);
CREATE INDEX IF NOT EXISTS idx_transacciones_id_log ON transacciones_2pc(transaccion_id);
CREATE INDEX IF NOT EXISTS idx_votos_transaccion ON participantes_votos(transaccion_id);

-- Vista para reporte de transacciones pendientes
CREATE OR REPLACE VIEW vw_transacciones_pendientes AS
SELECT 
    transaccion_id,
    estado,
    fase_actual,
    origen_nodo,
    destino_nodo,
    monto,
    timestamp_inicio,
    EXTRACT(EPOCH FROM (NOW() - timestamp_inicio)) AS segundos_transcurridos
FROM transacciones_2pc
WHERE estado IN ('PREPARING', 'COMMITTING')
AND timestamp_fin IS NULL;