from flask import Flask, request, jsonify, send_file
from utils import *
from io import BytesIO

app = Flask(__name__)
create_db()

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username, password = data["username"], data["password"]
    hash_, salt = hash_password(password)
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", (username, hash_, salt))
            conn.commit()
            return jsonify({"msg": "User registered"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username, password = data["username"], data["password"]
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT password_hash, salt FROM users WHERE username=?", (username,))
        row = c.fetchone()
        if row and verify_password(password, *row):
            token = create_jwt(username)
            return jsonify({"token": token})
        return jsonify({"error": "Invalid credentials"}), 401

@app.route("/upload", methods=["POST"])
def upload():
    token = request.headers.get("Authorization")
    payload = verify_jwt(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 403

    user = payload["username"]
    file = request.files["file"]
    data = file.read()
    encrypted = encrypt_file(data)

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=?", (user,))
        user_id = c.fetchone()[0]
        filename = file.filename
        path = os.path.join(UPLOAD_FOLDER, filename)
        with open(path, "wb") as f:
            f.write(encrypted)
        c.execute("INSERT INTO files (user_id, filename, filepath, upload_date) VALUES (?, ?, ?, datetime('now'))",
                  (user_id, filename, path))
        conn.commit()
        return jsonify({"msg": "File uploaded"})

@app.route("/files", methods=["GET"])
def list_files():
    token = request.headers.get("Authorization")
    payload = verify_jwt(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 403
    user = payload["username"]
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=?", (user,))
        user_id = c.fetchone()[0]
        c.execute("SELECT id, filename, upload_date FROM files WHERE user_id=?", (user_id,))
        files = c.fetchall()
        return jsonify([{"id": f[0], "filename": f[1], "date": f[2]} for f in files])

@app.route("/download/<int:file_id>", methods=["GET"])
def download(file_id):
    token = request.headers.get("Authorization")
    payload = verify_jwt(token)
    if not payload:
        return jsonify({"error": "Unauthorized"}), 403

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT filepath, filename FROM files WHERE id=?", (file_id,))
        row = c.fetchone()
        if not row:
            return jsonify({"error": "File not found"}), 404

        with open(row[0], "rb") as f:
            encrypted_data = f.read()
        decrypted = decrypt_file(encrypted_data)
        return send_file(BytesIO(decrypted), download_name=row[1], as_attachment=True)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))