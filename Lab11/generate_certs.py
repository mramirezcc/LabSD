"""
Script de generacion de certificados digitales con Python (cryptography)
Proposito: Crear una CA raiz local, generar clave privada y emitir
           un certificado digital valido para localhost sin depender de OpenSSL.
"""
import os
import sys
from datetime import datetime, timedelta

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


CERT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")
DAYS_VALID = 365


def generar_certificados():
    os.makedirs(CERT_DIR, exist_ok=True)

    print("=== Generacion de Certificados para Canal Seguro TLS (Python) ===\n")

    # 1. Generar clave privada de la CA raiz (4096 bits RSA)
    print("[1/4] Generando clave privada de la CA raiz (RSA 4096)...")
    ca_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend(),
    )
    ca_key_path = os.path.join(CERT_DIR, "ca-key.pem")
    with open(ca_key_path, "wb") as f:
        f.write(ca_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    print(f"      -> {ca_key_path}")

    # 2. Generar certificado autofirmado de la CA raiz
    print("[2/4] Generando certificado autofirmado de la CA raiz...")
    ca_subject = ca_issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "PE"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Arequipa"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Arequipa"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "LogiMarket"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Seguridad"),
        x509.NameAttribute(NameOID.COMMON_NAME, "LogiMarket Root CA"),
    ])
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_subject)
        .issuer_name(ca_issuer)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=DAYS_VALID))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=True,
            key_cert_sign=True,
            crl_sign=True,
            content_commitment=False,
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            encipher_only=False,
            decipher_only=False,
        ), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()), critical=False)
        .sign(private_key=ca_key, algorithm=hashes.SHA512(), backend=default_backend())
    )
    ca_cert_path = os.path.join(CERT_DIR, "ca-cert.pem")
    with open(ca_cert_path, "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
    print(f"      -> {ca_cert_path}")

    # 3. Generar clave privada del servidor (2048 bits RSA)
    print("[3/4] Generando clave privada del servidor (RSA 2048)...")
    server_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )
    server_key_path = os.path.join(CERT_DIR, "server-key.pem")
    with open(server_key_path, "wb") as f:
        f.write(server_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    print(f"      -> {server_key_path}")

    # 4. Generar CSR y firmar certificado del servidor con la CA
    print("[4/4] Firmando certificado del servidor con la CA raiz...")
    server_subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "PE"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Arequipa"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Arequipa"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "LogiMarket"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "TI"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    server_cert = (
        x509.CertificateBuilder()
        .subject_name(server_subject)
        .issuer_name(ca_cert.subject)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=DAYS_VALID))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            data_encipherment=True,
            content_commitment=False,
            key_cert_sign=False,
            crl_sign=False,
            key_agreement=False,
            encipher_only=False,
            decipher_only=False,
        ), critical=True)
        .add_extension(x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("*.localhost"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            x509.IPAddress(ipaddress.IPv6Address("::1")),
        ]), critical=False)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
            critical=False,
        )
        .sign(private_key=ca_key, algorithm=hashes.SHA512(), backend=default_backend())
    )
    server_cert_path = os.path.join(CERT_DIR, "server-cert.pem")
    with open(server_cert_path, "wb") as f:
        f.write(server_cert.public_bytes(serialization.Encoding.PEM))
    print(f"      -> {server_cert_path}")

    print(f"\n=== Certificados generados exitosamente en {CERT_DIR}/ ===")
    print(f"  CA:     {ca_cert_path}")
    print(f"  Server: {server_cert_path}")
    print(f"  Key:    {server_key_path}")
    return True


if __name__ == "__main__":
    import ipaddress
    generar_certificados()
else:
    import ipaddress
