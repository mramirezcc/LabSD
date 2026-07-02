@echo off
REM =============================================================================
REM Script de generacion de certificados digitales con OpenSSL (Windows)
REM Proposito: Crear una CA raiz local, generar clave privada y CSR,
REM            y emitir un certificado digital valido para localhost.
REM =============================================================================

setlocal enabledelayedexpansion

set CERT_DIR=.\certs
set CA_KEY=%CERT_DIR%\ca-key.pem
set CA_CERT=%CERT_DIR%\ca-cert.pem
set SERVER_KEY=%CERT_DIR%\server-key.pem
set SERVER_CSR=%CERT_DIR%\server.csr
set SERVER_CERT=%CERT_DIR%\server-cert.pem
set SERVER_EXT=%CERT_DIR%\server-ext.cnf
set DAYS_VALID=365

echo === Generacion de Certificados para Canal Seguro TLS ===
echo.

if not exist "%CERT_DIR%" mkdir "%CERT_DIR%"

REM 1. Generar clave privada de la CA raiz
echo [1/5] Generando clave privada de la CA raiz...
openssl genrsa -out "%CA_KEY%" 4096
echo       -^> %CA_KEY%

REM 2. Generar certificado autofirmado de la CA raiz
echo [2/5] Generando certificado autofirmado de la CA raiz...
openssl req -x509 -new -nodes -key "%CA_KEY%" -sha512 -days %DAYS_VALID% -out "%CA_CERT%" -subj "/C=PE/ST=Arequipa/L=Arequipa/O=LogiMarket/OU=Seguridad/CN=LogiMarket Root CA"
echo       -^> %CA_CERT%

REM 3. Generar clave privada del servidor
echo [3/5] Generando clave privada del servidor...
openssl genrsa -out "%SERVER_KEY%" 2048
echo       -^> %SERVER_KEY%

REM 4. Generar CSR del servidor
echo [4/5] Generando CSR del servidor...
openssl req -new -key "%SERVER_KEY%" -out "%SERVER_CSR%" -subj "/C=PE/ST=Arequipa/L=Arequipa/O=LogiMarket/OU=TI/CN=localhost"
echo       -^> %SERVER_CSR%

REM 5. Crear archivo de extensiones y firmar certificado
echo [5/5] Creando archivo de extensiones y firmando certificado del servidor...
(
echo authorityKeyIdentifier=keyid,issuer
echo basicConstraints=CA:FALSE
echo keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
echo subjectAltName = @alt_names
echo.
echo [alt_names]
echo DNS.1 = localhost
echo DNS.2 = *.localhost
echo IP.1 = 127.0.0.1
echo IP.2 = ::1
) > "%SERVER_EXT%"

openssl x509 -req -in "%SERVER_CSR%" -CA "%CA_CERT%" -CAkey "%CA_KEY%" -CAcreateserial -out "%SERVER_CERT%" -days %DAYS_VALID% -sha512 -extfile "%SERVER_EXT%"

echo.
echo === Certificados generados exitosamente en %CERT_DIR%\ ===
echo.

REM Verificar
echo --- Verificacion del certificado del servidor ---
openssl verify -CAfile "%CA_CERT%" "%SERVER_CERT%"
echo.

echo Listo. El servidor HTTPS puede iniciarse con:
echo   python app.py

endlocal
