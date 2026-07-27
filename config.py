import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "customerpulse-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///customerpulse.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False