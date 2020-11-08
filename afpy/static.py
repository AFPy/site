import os

FLASK_PORT = os.getenv("FLASK_PORT")
FLASK_DEBUG = os.getenv("FLASK_DEBUG")
FLASK_HOST = os.getenv("FLASK_HOST")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

AFPY_ROOT = os.path.join(os.path.dirname(__file__), "../")  # refers to application_top
