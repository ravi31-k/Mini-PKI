from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
import os
import sys

def create_user_csr(username):
    # Step 1: Generate private key
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Step 2: Define CSR subject (user info)
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Uttar Pradesh"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Greater Noida"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ShadowShield Users"),
        x509.NameAttribute(NameOID.COMMON_NAME, username),
    ])).sign(key, hashes.SHA256())

    # Step 3: Save private key and CSR
    user_dir = f"users/{username}"
    os.makedirs(user_dir, exist_ok=True)

    with open(f"{user_dir}/private_key.pem", "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(f"{user_dir}/request.csr", "wb") as f:
        f.write(csr.public_bytes(encoding=serialization.Encoding.PEM))

    print(f"[+] CSR and private key generated for user: {username}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Error: Please provide a username.")
    else:
        username = sys.argv[1]
        create_user_csr(username)
