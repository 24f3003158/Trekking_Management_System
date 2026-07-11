import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey_for_trekking_app')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///trekking_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt_secret_token_key')
    REDIS_URL = "redis://localhost:6379/0"