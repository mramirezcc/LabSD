#!/bin/bash
# =============================================================================
# Script de generacion de certificados digitales con OpenSSL
# Proposito: Crear una CA raiz local, generar clave privada y CSR,
#            y emitir un certificado digital valido para localhost.
# =============================================================================

set -e

CERT_DIR="./certs"
CA_KEY="${CERT_DIR}/ca-key.pem"
CA_CERT="${CERT_DIR}/ca-cert.pem"
SERVER_KEY="${CERT_DIR}/server-key.pem"
SERVER_CSR="${CERT_DIR}/server.csr"
SERVER_CERT="${CERT_DIR}/server-cert.pem"
SERVER_EXT="${CERT_DIR}/server-ext.cnf"
DAYS_VALID=365

echo "=== Generacion de Certificados para Canal Seguro TLS ==="
echo ""

mkdir -p "${CERT_DIR}"

# 1. Generar clave privada de la Entidad Certificadora (CA) raiz
echo "[1/5] Generando clave privada de la CA raiz..."
openssl genrsa -out "${CA_KEY}" 4096
echo "      -> ${CA_KEY}"

# 2. Generar certificado autofirmado de la CA raiz
echo "[2/5] Generando certificado autofirmado de la CA raiz..."
openssl req -x509 -new -nodes -key "${CA_KEY}" -sha512 -days "${DAYS_VALID}" \
    -out "${CA_CERT}" \
    -subj "/C=PE/ST=Arequipa/L=Arequipa/O=LogiMarket/OU=Seguridad/CN=LogiMarket Root CA"
echo "      -> ${CA_CERT}"

# 3. Generar clave privada del servidor
echo "[3/5] Generando clave privada del servidor..."
openssl genrsa -out "${SERVER_KEY}" 2048
echo "      -> ${SERVER_KEY}"

# 4. Generar solicitud de firma de certificado (CSR) del servidor
echo "[4/5] Generando CSR del servidor..."
openssl req -new -key "${SERVER_KEY}" -out "${SERVER_CSR}" \
    -subj "/C=PE/ST=Arequipa/L=Arequipa/O=LogiMarket/OU=TI/CN=localhost"
echo "      -> ${SERVER_CSR}"

# 5. Crear archivo de extensiones para SAN (Subject Alternative Name)
echo "[5/5] Creando archivo de extensiones y firmando certificado del servidor..."
cat > "${SERVER_EXT}" << EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

# 6. Firmar el certificado del servidor con la CA raiz
openssl x509 -req -in "${SERVER_CSR}" -CA "${CA_CERT}" -CAkey "${CA_KEY}" \
    -CAcreateserial -out "${SERVER_CERT}" -days "${DAYS_VALID}" -sha512 \
    -extfile "${SERVER_EXT}"

echo ""
echo "=== Certificados generados exitosamente en ${CERT_DIR}/ ==="
echo ""

# Verificar certificados generados
echo "--- Verificacion del certificado del servidor ---"
openssl verify -CAfile "${CA_CERT}" "${SERVER_CERT}"
echo ""

echo "--- Informacion del certificado del servidor ---"
openssl x509 -in "${SERVER_CERT}" -text -noout | grep -E "Subject:|Issuer:|Not Before|Not After|DNS:|IP Address:"
echo ""
echo "Listo. El servidor HTTPS puede iniciarse con:"
echo "  python app.py"
