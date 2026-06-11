-- Base de datos: banco_cusco
-- Nodo destino de la transacción

CREATE TABLE IF NOT EXISTS cuentas (
    id SERIAL PRIMARY KEY,
    numero_cuenta VARCHAR(20) UNIQUE NOT NULL,
    titular VARCHAR(100) NOT NULL,
    saldo DECIMAL(15,2) DEFAULT 0 CHECK (saldo >= 0),
    ciudad VARCHAR(50) DEFAULT 'Cusco',
    estado VARCHAR(20) DEFAULT 'activa',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transacciones_log (
    id SERIAL PRIMARY KEY,
    transaccion_id VARCHAR(50),
    tipo VARCHAR(20),
    monto DECIMAL(15,2),
    estado VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar cuentas de ejemplo en Cusco
INSERT INTO cuentas (numero_cuenta, titular, saldo) 
VALUES ('2001-1111', 'Empresa Turística Machu Picchu', 75000.00)
ON CONFLICT (numero_cuenta) DO NOTHING;

INSERT INTO cuentas (numero_cuenta, titular, saldo) 
VALUES ('2001-2222', 'Cervecería del Cusco', 120000.00)
ON CONFLICT (numero_cuenta) DO NOTHING;

-- Función para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER update_cuentas_timestamp
    BEFORE UPDATE ON cuentas
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_timestamp();

-- Índices
CREATE INDEX IF NOT EXISTS idx_cuentas_numero ON cuentas(numero_cuenta);
CREATE INDEX IF NOT EXISTS idx_transacciones_id ON transacciones_log(transaccion_id);