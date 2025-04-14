# 🛡️ Mini PKI System

A lightweight, Flask-based Public Key Infrastructure (PKI) system that allows users to generate Certificate Signing Requests (CSRs) and private keys, issue digital certificates, validate or revoke them, and manage keys through an interactive admin dashboard. It also includes an AI-powered cybersecurity chatbot to answer security-related queries.

This project demonstrates practical PKI concepts using Python and OpenSSL, and is ideal for learning, testing, or as a base for integrating PKI into real applications.
## ✨ Features

🔐 **User CSR & Key Generation**  
Users can register by entering their name to generate a Certificate Signing Request (CSR) and a private key using OpenSSL.

📜 **Certificate Signing**  
Admins can sign CSRs, generating `.pem` certificates and `.pfx` bundles (including certificate + private key) with password protection.

📥 **Download Center**  
Each user can download their `.pem`, `.pfx`, and `.csr` files from a secure page.

✅ **Certificate Validation**  
Check whether a certificate is valid, revoked, or expired using OpenSSL verification and CRL checks.

⛔ **Certificate Revocation**  
Revoke certificates through user or admin interfaces, and maintain a Certificate Revocation List (CRL).

🧑‍💻 **Admin Dashboard**  
Admins can:
- View all user certificates and their status (Valid/Revoked)
- Manage keys (View/Delete/Download)
- Revoke certificates
- Log in securely via an admin panel

🧠 **AI-Powered Cybersecurity Chatbot**  
A GPT-based chatbot answers cybersecurity-related questions from users via OpenRouter integration.

🗂️ **File System-Based Storage**  
All keys, CSRs, and certificates are stored securely under a `users/` directory.

🎨 **Modern UI with Bootstrap**  
Clean, dark-themed UI for an intuitive experience.

## 🗂️ Project Structure

## 🔐 Cryptographic Algorithms Used

This Mini PKI system leverages industry-standard cryptographic algorithms to ensure secure certificate handling, authentication, and encryption.

### 1. RSA (Rivest–Shamir–Adleman)
- **Purpose**: Used for key generation, digital signatures, and encryption.
- **Why RSA?**
  - It is asymmetric: uses a **public key** for encryption and a **private key** for decryption.
  - It's widely supported and secure when using key sizes like 2048 or 4096 bits.
- **Where used?**
  - When generating private/public key pairs (`generate_csr.py`)
  - In signing the Certificate Signing Request (CSR)
  - To verify digital signatures during certificate validation

### 2. X.509 Certificates
- **Purpose**: Standard format for public key certificates.
- **Components**:
  - Subject (owner of certificate)
  - Issuer (CA - Certificate Authority)
  - Public key
  - Validity period
  - Signature of the issuer
- **Where used?**
  - `.pem` files created by the CA
  - Used during certificate validation and SSL/TLS handshakes

### 3. SHA-256 (Secure Hash Algorithm)
- **Purpose**: Hashing algorithm used in digital signatures.
- **Where used?**
  - When signing CSRs, SHA-256 is used to hash the certificate content before it is signed by the CA's private key.

### 4. PKCS#12 (.pfx files)
- **Purpose**: Bundles the private key and certificate into a secure file.
- **Where used?**
  - After signing, certificates and private keys are exported as `.pfx` (PKCS#12) files using a user-defined password.

### 5. CRL (Certificate Revocation List)
- **Purpose**: Allows the CA to revoke compromised or expired certificates.
- **Where used?**
  - A revoked certificate’s serial number is added to `crl.pem`.
  - During validation, the certificate’s serial is checked against this list.

## 🛠️ How It Works (System Flow)

This section outlines the flow of the Mini PKI system, from the generation of key pairs to signing, certificate revocation, and management.

### 1. **User Registration (Generate CSR)**
   - **Flow**:
     1. The user submits their **name** via a registration form.
     2. A **CSR** (Certificate Signing Request) and **private key** are generated using the `generate_csr.py` script.
     3. The CSR and private key are stored under the `users/{username}` directory, while the private key is never exposed.
   - **Algorithms**: RSA for key generation (2048-bit or 4096-bit).

### 2. **Signing the CSR (Sign Certificate)**
   - **Flow**:
     1. The user submits their **name** and **PFX password**.
     2. The CSR is signed using the **private key of the Certificate Authority (CA)** and a **validity period** is assigned to the certificate.
     3. The signed certificate is bundled into a **PFX** file, which contains both the certificate and the private key.
     4. The user is given the option to **download** the PFX file.
   - **Algorithms**: RSA for signing and SHA-256 for hashing.

### 3. **Certificate Validation**
   - **Flow**:
     1. A user submits their **certificate name** for validation.
     2. The certificate is verified:
        - It is checked for **expiration**.
        - It is checked for **revocation** by comparing the certificate's serial number against the **Certificate Revocation List (CRL)**.
     3. The result is displayed: valid, expired, or revoked.
   - **Algorithms**: SHA-256 for the hash and RSA for verifying the signature.

### 4. **Revoking a Certificate**
   - **Flow**:
     1. An **admin** marks a certificate for **revocation**.
     2. The certificate’s **serial number** is added to the **CRL** (Certificate Revocation List).
     3. The certificate is no longer valid for use.
   - **Algorithms**: RSA for signing the CRL.

### 5. **Admin Key Management**
   - **Flow**:
     1. Admins can **view, download, or delete** private keys for users.
     2. Admins can also **export** the private key, allowing secure handling and backup.
   - **Actions**:
     - **View**: Admins can view key contents (i.e., private key or certificate content).
     - **Download**: Admins can download key files for further use.
     - **Delete**: Admins can delete key files from the server.
   - **Security**: Each key is only accessible to admins with proper authentication.

### 6. **AI-Powered Cybersecurity Chat**
   - **Flow**:
     1. Users can interact with the chatbot through the `/cyberchat` route.
     2. The chatbot uses an AI model to answer questions related to cybersecurity topics.
   - **Integration**: Uses the `ask_ai` function, powered by the AI model to generate responses based on the user’s query.

# Mini PKI System

A Mini Public Key Infrastructure (PKI) system built with **Flask** and **Python** for managing user certificates, key files, and providing certificate signing functionality. The system includes features like user registration, certificate validation, revocation, and an admin dashboard for managing keys and certificates.

---

## ⚙️ Setup and Installation

This section outlines the steps to set up the Mini PKI system on your local machine or server. The system is built using **Flask**, **Python**, and cryptographic libraries for key management and certificate signing.

### Prerequisites

- **Python 3.7+**
- **pip** (Python package installer)
- **Flask**
- **OpenSSL** (for certificate generation and signing)

### Clone the Repository

Start by cloning the repository to your local machine:

git clone [https://github.com/yourusername/mini-pki.git](https://github.com/ravi31-k/Mini-PKI.git)
cd mini-pki

### Install Dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

### Running the Application
python app.py

# To access the Admin Dashboard, log in using the credentials provided in app.py:
Username: admin
Password: admin123
