import os

FLASK_PORT = os.getenv("FLASK_PORT")
FLASK_DEBUG = os.getenv("FLASK_DEBUG")
FLASK_HOST = os.getenv("FLASK_HOST")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

DB_NAME = os.getenv("DB_NAME")

NEWS_PER_PAGE = 12

AFPY_ROOT = os.path.join(os.path.dirname(__file__), "../")  # refers to application_top

IMAGES_PATH = os.getenv("IMAGES_PATH", f"{AFPY_ROOT}/images/")
