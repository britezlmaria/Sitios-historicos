from datetime import timedelta
from os import environ


class Config:
    TESTING = False
    SECRET_KEY = environ.get("SECRET_KEY")
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_TYPE = "filesystem"
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_NAME= "access_token_cookie"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_SECRET_KEY = environ.get("JWT_SECRET_KEY") or "test"

    GOOGLE_CLIENT_ID = environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = environ.get("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = environ.get("GOOGLE_REDIRECT_URI")

    FRONTEND_ORIGIN = environ.get("FRONTEND_ORIGIN")

    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_COOKIE_SAMESITE = "Lax" 
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = False

    


class ProductionConfig(Config):
    MINIO_SERVER = environ.get("MINIO_SERVER")
    MINIO_ACCESS_KEY = environ.get("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = environ.get("MINIO_SECRET_KEY")
    MINIO_SECURE = True
    MINIO_BUCKET = "grupo05"
    
    SQLALCHEMY_ENGINES = {"default": environ.get("DATABASE_URL")}
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_ENGINES["default"]
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 60,
        "pool_pre_ping": True,
    }
    JWT_COOKIE_SECURE = True
    FRONTEND_ORIGIN = environ.get("FRONTEND_ORIGIN") or "http://127.0.0.1:5173"
    GOOGLE_REDIRECT_URI = environ.get("GOOGLE_REDIRECT_URI") or "http://127.0.0.1:5000/api/auth/google/callback"
    JWT_COOKIE_CSRF_PROTECT = environ.get("JWT_COOKIE_CSRF_PROTECT", "True") == "True"
    JWT_COOKIE_DOMAIN = ".proyecto2025.linti.unlp.edu.ar"
    SESSION_COOKIE_DOMAIN = ".proyecto2025.linti.unlp.edu.ar"

class DevelopmentConfig(Config):
    
    MINIO_SERVER = environ.get("MINIO_SERVER") or "localhost:9000"
    MINIO_ACCESS_KEY = environ.get("MINIO_ACCESS_KEY") or "minioadmin"
    MINIO_SECRET_KEY = environ.get("MINIO_SECRET_KEY") or "minioadmin"
    MINIO_SECURE = environ.get("MINIO_SECURE", "false").lower() == "true"
    MINIO_BUCKET = environ.get("MINIO_BUCKET") or "grupo05"
    
    DB_USER = environ.get("POSTGRES_USER") or "admin"
    DB_PASSWORD = environ.get("POSTGRES_PASSWORD") or "admin"
    DB_HOST = environ.get("DB_HOST") or "localhost"
    DB_PORT = environ.get("DB_PORT") or "5433"
    DB_NAME = environ.get("POSTGRES_DB") or "grupo05"
    DB_SCHEME = "postgresql+psycopg2"
    JWT_COOKIE_SECURE = False
    FRONTEND_ORIGIN = environ.get("FRONTEND_ORIGIN") or "http://127.0.0.1:5173"
    GOOGLE_REDIRECT_URI = environ.get("GOOGLE_REDIRECT_URI") or "http://127.0.0.1:5000/api/auth/google/callback"
    JWT_COOKIE_CSRF_PROTECT = environ.get("JWT_COOKIE_CSRF_PROTECT", "True") == "True"


    SQLALCHEMY_ENGINES = {
        "default": f"{DB_SCHEME}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    }
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_ENGINES["default"]


class TestingConfig(Config):
    TESTING = True
    JWT_COOKIE_CSRF_PROTECT = False
    DB_USER = environ.get("POSTGRES_USER") or "admin"
    DB_PASSWORD = environ.get("POSTGRES_PASSWORD") or "admin"
    DB_HOST = environ.get("DB_HOST") or "localhost"
    DB_PORT = environ.get("DB_PORT") or "5433"
    DB_NAME = environ.get("POSTGRES_TEST_DB") or "grupo05_test"
    DB_SCHEME = "postgresql+psycopg2"

    SQLALCHEMY_ENGINES = {
        "default": f"{DB_SCHEME}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    }
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_ENGINES["default"]


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
