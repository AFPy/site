from flask import Blueprint
from flask import render_template

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home_page():
    return render_template("pages/index.html")


@home_bp.route("/communaute")
def community_page():
    return render_template("pages/communaute.html")


@home_bp.route("/adherer")
def adhere():
    return render_template("pages/adhesions.html")
