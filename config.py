import os

SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")
JWT_SECRET = os.environ.get("JWT_SECRET", "your-jwt-secret")
SQLALCHEMY_DATABASE_URI = "sqlite:///vault.db"
UPLOAD_FOLDER = "uploads"
