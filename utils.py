import os
import hashlib
import binascii
import sqlite3
import jwt
import datetime
from cryptography.fernet import Fernet

SECRET_KEY = "supersecretkey"
FERNET_KEY = Fernet.generate_key()
cipher = Fernet(FERNET_KEY)
DB_PATH = "database.db"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def create_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT,
            filepath TEXT,
            upload_date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

def hash_password(password, salt=None):
    if not salt:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return binascii.hexlify(pwd_hash).decode(), binascii.hexlify(salt).decode()

def verify_password(password, stored_hash, salt):
    new_hash, _ = hash_password(password, binascii.unhexlify(salt))
    return new_hash == stored_hash

def create_jwt(username):
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_jwt(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None

def encrypt_file(data):
    return cipher.encrypt(data)

def decrypt_file(data):
    return cipher.decrypt(data)