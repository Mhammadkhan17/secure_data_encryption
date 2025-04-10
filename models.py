from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(256))
    salt = db.Column(db.String(64))

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    path = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    key = db.Column(db.String(100))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
