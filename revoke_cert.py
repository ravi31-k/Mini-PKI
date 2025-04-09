from cryptography import x509
from cryptography.hazmat.backends import default_backend

def revoke_certificate(username):
    # Load user certificate
    with open(f"users/{username}/certificate.pem", "rb") as f:
        user_cert = x509.load_pem_x509_certificate(f.read(), default_backend())

    serial_number = user_cert.serial_number
    serial_str = str(serial_number)

    # Open and append to revoked.txt only if not already listed
    try:
        with open("revoked.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    existing_serials = {line.strip() for line in lines}
    if serial_str not in existing_serials:
        with open("revoked.txt", "a", encoding="utf-8") as f:
            f.write(f"{serial_str}\n")
        print(f"[+] Certificate for '{username}' revoked successfully.")
    else:
        print(f"[!] Certificate for '{username}' is already revoked.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python revoke_cert.py <username>")
        sys.exit(1)
    
    revoke_certificate(sys.argv[1])
