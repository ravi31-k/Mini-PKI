from flask import Flask, render_template, request, send_file, flash, redirect, url_for, session
import os
import subprocess
from functools import wraps
from sign_csr import sign_csr
from orchatbot import ask_ai

app = Flask(__name__)
app.secret_key = "your_secret_key"

# --- Admin Access Decorator ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin"):
            flash("Admin access required.", "danger")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function

# --- Public Routes ---

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        os.system(f'python generate_csr.py "{name}"')
        flash(f"CSR and private key generated for {name}.", "success")
        return redirect(url_for("home"))
    return render_template("register.html")

@app.route("/sign", methods=["GET", "POST"])
def sign():
    if request.method == "POST":
        name = request.form["name"]
        pfx_password = request.form["pfx_password"].encode()

        try:
            sign_csr(name, pfx_password)
            flash(f"Certificate signed and PFX generated for {name}.", "success")
            return redirect(url_for("download_page", username=name))
        except Exception as e:
            flash(f"Error signing certificate: {str(e)}", "danger")
            return redirect(url_for("home"))
    return render_template("sign.html")

@app.route("/downloads/<username>")
def download_page(username):
    user_path = os.path.join("users", username)
    files = []

    if os.path.exists(user_path):
        for file in os.listdir(user_path):
            if file.endswith((".pem", ".csr", ".pfx")):
                files.append(file)
    else:
        flash("User folder not found.", "danger")
        return redirect(url_for("home"))

    return render_template("download.html", username=username, files=files)

@app.route("/download/<username>/<filename>")
def download_file(username, filename):
    path = os.path.join("users", username, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        flash("File not found.", "danger")
        return redirect(url_for("download_page", username=username))

@app.route("/validate", methods=["GET", "POST"])
def validate():
    if request.method == "POST":
        name = request.form["name"]
        result = subprocess.run(
            ["python", "validate_cert.py", name],
            capture_output=True,
            text=True
        )
        output = result.stdout.strip()
        exit_code = result.returncode

        if exit_code == 0:
            flash(f"[VALID] {output}", "success")
        elif exit_code == 2:
            flash(f"[REVOKED] {output}", "danger")
        elif exit_code == 3:
            flash(f"[EXPIRED] {output}", "warning")
        else:
            flash(f"[INVALID] {output}", "danger")

        return redirect(url_for("validate"))
    return render_template("validate.html")

@app.route("/revoke", methods=["POST"])
def revoke():
    name = request.form["name"]
    os.system(f'python revoke_cert.py "{name}"')
    flash(f"Certificate revoked for {name}.", "danger")
    return redirect(url_for("home"))

@app.route("/cyberchat", methods=["GET", "POST"])
def cyberchat():
    response = None
    if request.method == "POST":
        question = request.form["question"]
        try:
            response = ask_ai(question)
        except Exception as e:
            flash(f"Error getting response: {e}", "danger")
    return render_template("cyberchat.html", response=response)

# --- Admin Routes ---

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "admin123":
            session["admin"] = True
            flash("Admin login successful.", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials.", "danger")
    return render_template("admin_login.html")

@app.route("/admin/logout")
@admin_required
def admin_logout():
    session.pop("admin", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("home"))

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    cert_data = []
    base_path = "users"
    if os.path.exists(base_path):
        for user in os.listdir(base_path):
            user_path = os.path.join(base_path, user)
            files = os.listdir(user_path)
            cert_file = next((f for f in files if f.endswith(".pem")), None)
            if cert_file:
                status = "Revoked" if "revoked" in cert_file.lower() else "Valid"
                cert_data.append({
                    "username": user,
                    "cert_file": cert_file,
                    "status": status
                })
    return render_template("admin_dashboard.html", cert_data=cert_data)

@app.route("/admin/revoke/<username>")
@admin_required
def admin_revoke(username):
    os.system(f'python revoke_cert.py "{username}"')
    flash(f"Certificate revoked for {username}.", "warning")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/keys")
@admin_required
def admin_keys():
    key_data = []
    base_path = "users"

    if os.path.exists(base_path):
        for user in os.listdir(base_path):
            user_path = os.path.join(base_path, user)
            if os.path.isdir(user_path):
                for file in os.listdir(user_path):
                    if file.endswith(".key") or "private" in file.lower():
                        key_data.append({"username": user, "key_name": file})

    return render_template("admin_keys.html", key_data=key_data)

@app.route("/admin/keys/view/<username>/<key_name>")
@admin_required
def view_key(username, key_name):
    path = os.path.join("users", username, key_name)
    if os.path.exists(path):
        with open(path, "r") as f:
            content = f.read()
        return render_template("view_key.html", username=username, key_name=key_name, content=content)
    else:
        flash("Key file not found.", "danger")
        return redirect(url_for("admin_keys"))

@app.route("/admin/keys/download/<username>/<key_name>")
@admin_required
def download_key(username, key_name):
    path = os.path.join("users", username, key_name)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        flash("Key file not found.", "danger")
        return redirect(url_for("admin_keys"))

@app.route("/admin/keys/delete/<username>/<key_name>")
@admin_required
def delete_key(username, key_name):
    path = os.path.join("users", username, key_name)
    if os.path.exists(path):
        os.remove(path)
        flash(f"Key {key_name} deleted for user {username}.", "warning")
    else:
        flash("Key file not found.", "danger")
    return redirect(url_for("admin_keys"))

if __name__ == "__main__":
    app.run(debug=True)
