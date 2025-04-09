# sign_csr.py

from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from datetime import datetime, timedelta
import os
from export_to_pfx import create_pfx

def sign_csr(username, password):
    user_path = f"users/{username}"
    ca_path = "ca"

    # Load CA private key
    with open(os.path.join(ca_path, "ca_key.pem"), "rb") as f:
        ca_private_key = serialization.load_pem_private_key(f.read(), password=None)

    # Load CA certificate
    with open(os.path.join(ca_path, "ca_cert.pem"), "rb") as f:
        ca_certificate = x509.load_pem_x509_certificate(f.read())

    # Load CSR
    with open(os.path.join(user_path, "request.csr"), "rb") as f:
        csr = x509.load_pem_x509_csr(f.read())

    # Create certificate
    certificate = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(ca_certificate.subject)
        .public_key(csr.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .sign(ca_private_key, hashes.SHA256())
    )

    # Save certificate
    cert_path = os.path.join(user_path, "certificate.pem")
    with open(cert_path, "wb") as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM))

    # Save CA certificate copy
    with open(os.path.join(user_path, "ca_cert.pem"), "wb") as f:
        f.write(ca_certificate.public_bytes(serialization.Encoding.PEM))

    print(f"✅ Certificate signed and saved at: {cert_path}")

    # Generate PFX using provided password
    create_pfx(username, password)

if __name__ == "__main__":
    username = input("Enter the username to sign the CSR: ")
    password = input("Enter PFX export password: ").encode()
    sign_csr(username, password)
