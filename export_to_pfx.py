# export_to_pfx.py

from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import serialization
from cryptography import x509
import os

def create_pfx(username, password):
    user_path = os.path.join("users", username)

    private_key_path = os.path.join(user_path, "private_key.pem")
    certificate_path = os.path.join(user_path, "certificate.pem")
    ca_cert_path = os.path.join(user_path, "ca_cert.pem")

    # Load private key
    if not os.path.exists(private_key_path):
        raise FileNotFoundError(f"Private key not found: {private_key_path}")
    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    # Load user's signed certificate
    if not os.path.exists(certificate_path):
        raise FileNotFoundError(f"Certificate not found: {certificate_path}")
    with open(certificate_path, "rb") as f:
        certificate = x509.load_pem_x509_certificate(f.read())

    # Load CA certificate
    if not os.path.exists(ca_cert_path):
        raise FileNotFoundError(f"CA certificate not found: {ca_cert_path}")
    with open(ca_cert_path, "rb") as f:
        ca_certificate = x509.load_pem_x509_certificate(f.read())

    # Create the .pfx file using the provided password
    pfx_data = pkcs12.serialize_key_and_certificates(
        name=username.encode(),
        key=private_key,
        cert=certificate,
        cas=[ca_certificate],
        encryption_algorithm=serialization.BestAvailableEncryption(password)
    )

    output_path = os.path.join(user_path, f"{username}.pfx")
    with open(output_path, "wb") as f:
        f.write(pfx_data)

    print(f"✅ PFX file created: {output_path}")
