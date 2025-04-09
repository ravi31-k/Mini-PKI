from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
import os

def create_ca():
    # Step 1: Generate private key for CA
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Step 2: Define certificate subject and issuer (self-signed)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Uttar Pradesh"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Greater Noida"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ShadowShield CA"),
        x509.NameAttribute(NameOID.COMMON_NAME, "ShadowShield Root CA"),
    ])

    # Step 3: Build self-signed certificate
    valid_from = datetime.datetime.now(datetime.timezone.utc)
    valid_to = valid_from + datetime.timedelta(days=3650)

    cert = x509.CertificateBuilder()\
        .subject_name(subject)\
        .issuer_name(issuer)\
        .public_key(key.public_key())\
        .serial_number(x509.random_serial_number())\
        .not_valid_before(valid_from)\
        .not_valid_after(valid_to)\
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)\
        .sign(private_key=key, algorithm=hashes.SHA256())


    # Step 4: Save private key and certificate
    os.makedirs("ca", exist_ok=True)

    with open("ca/ca_key.pem", "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open("ca/ca_cert.pem", "wb") as f:
        f.write(cert.public_bytes(encoding=serialization.Encoding.PEM))

    print("[+] Root CA private key and certificate generated in 'ca/' folder.")

if __name__ == "__main__":
    create_ca()
    