import json

from docutils.core import publish_parts
from docutils.writers import html5_polyglot
from flask import abort
from flask import Blueprint
from flask import render_template
from flask import send_from_directory
from peewee import DoesNotExist

from afpy.models.NewsEntry import NewsEntry
from afpy.static import AFPY_ROOT
from afpy.static import IMAGES_PATH
from afpy.static import NEWS_PER_PAGE

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home_page():
    all_news = NewsEntry.select().where(NewsEntry.state == "published").order_by(NewsEntry.dt_submitted.desc()).limit(4)
    return render_template("pages/index.html", body_id="index", posts=all_news)


@home_bp.route("/communaute")
def community_page():
    with open(f"{AFPY_ROOT}/afpy/data/data.json", "r") as handle:
        meetups = json.load(handle)["meetups"]
    return render_template("pages/communaute.html", body_id="communaute", meetups=meetups)


@home_bp.route("/adherer")
def adhere_page():
    return render_template("pages/adhesions.html", body_id="adhesions")


@home_bp.route("/discussion")
def discussion_page():
    return render_template("pages/discussion.html", body_id="discussion")


@home_bp.route("/docs/<name>")
def render_rest(name):
    try:
        with open(f"{AFPY_ROOT}/afpy/templates/rest/{name}.rst") as fd:
            parts = publish_parts(
                source=fd.read(), writer=html5_polyglot.Writer(), settings_overrides={"initial_header_level": 2}
            )
    except FileNotFoundError:
        abort(404)
    return render_template("pages/rst.html", body_id=name, html=parts["body"], title=parts["title"])


@home_bp.route("/posts/<int:post_id>")
def post_render(post_id: int):
    try:
        post = NewsEntry.get_by_id(post_id)
    except DoesNotExist:
        abort(404)
    return render_template("pages/post.html", body_id="post", post=post, name=post.title)


@home_bp.route("/posts/page/<int:current_page>")
def posts_page(current_page: int = 1):
    total_pages = (NewsEntry.select().where(NewsEntry.state == "published").count() // NEWS_PER_PAGE) + 1
    posts = NewsEntry.select().where(NewsEntry.state == "published").paginate(current_page, NEWS_PER_PAGE)
    return render_template(
        "pages/posts.html",
        body_id="posts",
        posts=posts,
        title="Actualités",
        current_page=current_page,
        total_pages=total_pages,
    )


@home_bp.route("/post_image/<path:path>")
def get_image(path):
    # if path.count("/") != 3:
    #     abort(404)
    # category, state, timestamp, name = path.split("/")
    # if category not in data.POSTS:
    #     abort(404)
    # if state not in data.STATES:
    #     abort(404)
    return send_from_directory(IMAGES_PATH, path)
