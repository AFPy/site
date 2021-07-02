import os
from dotenv import load_dotenv

AFPY_ROOT = os.path.join(os.path.dirname(__file__), "../")  # refers to application_top

load_dotenv(os.path.join(AFPY_ROOT, ".env"))


def check_vars():
    for item in ["FLASK_DEBUG", "FLASK_HOST", "FLASK_SECRET_KEY", "DB_NAME"]:
        if item not in os.environ:
            raise EnvironmentError(f"{item} is not set in the server's environment or .env file. It is required.")


check_vars()
del check_vars


FLASK_PORT = os.getenv("FLASK_PORT")
FLASK_DEBUG = os.getenv("FLASK_DEBUG").lower() in ("true", "1")
FLASK_HOST = os.getenv("FLASK_HOST")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
DB_NAME = os.getenv("DB_NAME")
NEWS_PER_PAGE = 12
IMAGES_PATH = os.getenv("IMAGES_PATH", f"{AFPY_ROOT}/images/")
