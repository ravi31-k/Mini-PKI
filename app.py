from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
import subprocess
from sign_csr import sign_csr  

app = Flask(__name__)
app.secret_key = "your_secret_key"

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

if __name__ == "__main__":
    app.run(debug=True)
