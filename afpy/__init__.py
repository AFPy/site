import os

from dotenv import load_dotenv
from flask import Flask


AFPY_ROOT = os.path.join(os.path.dirname(__file__), "../")  # refers to application_top
dotenv_path = os.path.join(AFPY_ROOT, ".env")
load_dotenv(dotenv_path)

REQUIRED_ENV_VARS = [
    "FLASK_PORT",
    "FLASK_DEBUG",
    "FLASK_HOST",
    "FLASK_SECRET_KEY",
    "DB_HOST",
    "DB_PORT",
    "DB_USER",
    "DB_PASSWORD",
    "DB_NAME",
]

for item in REQUIRED_ENV_VARS:
    if item not in os.environ:
        raise EnvironmentError(f"{item} is not set in the server's environment or .env file. It is required.")

from afpy.static import FLASK_SECRET_KEY

# DB_NAME,
# DB_USER,
# DB_PASSWORD,
# DB_PORT,
# DB_HOST,

application = Flask(__name__)

if os.getenv("FLASK_DEBUG", "false") == "true" or os.getenv("FLASK_DEBUG", "false") == "1":
    application.debug = True
else:
    application.debug = False

application.secret_key = FLASK_SECRET_KEY
application.config.update(FLASK_SECRET_KEY=FLASK_SECRET_KEY)


from afpy.routes.home import home_bp

application.register_blueprint(home_bp)
