from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
import datetime
import sys
import os

def validate_certificate(username):
    user_cert_path = f"users/{username}/certificate.pem"
    ca_cert_path = "ca/ca_cert.pem"
    revoked_file_path = "revoked.txt"

    # Load CA certificate
    with open(ca_cert_path, "rb") as f:
        ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())

    # Load user certificate
    if not os.path.exists(user_cert_path):
        print(f"[!] Certificate for user '{username}' not found.")
        return 1

    with open(user_cert_path, "rb") as f:
        user_cert = x509.load_pem_x509_certificate(f.read(), default_backend())

    # Check issuer
    if user_cert.issuer != ca_cert.subject:
        print("[!] Certificate issuer does not match the CA.")
        return 1

    # Check revoked
    revoked_serials = set()
    if os.path.exists(revoked_file_path):
        try:
            with open(revoked_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(revoked_file_path, "r", encoding="utf-16") as f:
                lines = f.readlines()
        revoked_serials = {int(line.strip()) for line in lines if line.strip().isdigit()}

    if user_cert.serial_number in revoked_serials:
        print("[!] Certificate has been REVOKED.")
        return 2

    # Check validity
    now = datetime.datetime.now(datetime.timezone.utc)
    if now < user_cert.not_valid_before_utc or now > user_cert.not_valid_after_utc:
        print("[!] Certificate is expired or not yet valid.")
        return 3

    # Verify signature
    try:
        ca_cert.public_key().verify(
            user_cert.signature,
            user_cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            user_cert.signature_hash_algorithm
        )
        print("[+] Certificate is VALID, AUTHENTIC, and SIGNED by trusted CA.")
        return 0
    except Exception as e:
        print("[!] Signature verification failed:", e)
        return 4

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_cert.py <username>")
        sys.exit(1)

    result = validate_certificate(sys.argv[1])
    sys.exit(result)
