import email
import locale
import os
import time
from datetime import datetime

from dateutil.parser import parse
import docutils.core
import docutils.writers.html5_polyglot
import feedparser
from flask import (
    Flask,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_caching import Cache
from itsdangerous import BadSignature, URLSafeSerializer
from jinja2 import TemplateNotFound

import common
# import data_xml as data
import data_sql as data


try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    sentry_sdk.init(integrations=[FlaskIntegration()])
except ImportError:
    sentry_sdk = None


locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")

cache = Cache(config={"CACHE_TYPE": "simple", "CACHE_DEFAULT_TIMEOUT": 600})
signer = URLSafeSerializer(os.environ.get("SECRET", "changeme!"))
app = Flask(__name__)
cache.init_app(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.route("/")
def index():
    posts = {}
    for post in data.get_posts(common.CATEGORY_ACTUALITIES, end=4):
        timestamp = post[common.FIELD_TIMESTAMP]
        posts[timestamp] = post
    return render_template(
        "index.html",
        body_id="index",
        category=common.CATEGORY_ACTUALITIES,
        posts=posts
    )


@app.route("/<name>")
def pages(name):
    if name == "index":
        return redirect(url_for("index"))
    try:
        return render_template(f"{name}.html", body_id=name, meetups=common.MEETUPS)
    except TemplateNotFound:
        return abort(404)


@app.route("/docs/<name>")
def rest(name):
    try:
        with open(f"templates/{name}.rst") as fd:
            parts = docutils.core.publish_parts(
                source=fd.read(),
                writer=docutils.writers.html5_polyglot.Writer(),
                settings_overrides={"initial_header_level": 2},
            )
    except FileNotFoundError:
        return abort(404)
    return render_template(
        "rst.html", body_id=name, html=parts["body"], title=parts["title"]
    )


@app.route("/post/edit/<category>")
@app.route("/post/edit/<category>/token/<token>")
def edit_post(category, token=None):
    if category not in common.CATEGORIES:
        return abort(404)
    if token:
        try:
            timestamp = signer.loads(token)
        except BadSignature:
            return abort(401)
        post = data.get_post(category, timestamp)
        if not post:
            return abort(404)
    else:
        post = {common.FIELD_STATE: common.STATE_WAITING}
    if post[common.FIELD_STATE] == common.STATE_TRASHED:
        return redirect(url_for("rest", name="already_trashed"))
    return render_template(
        "edit_post.html",
        body_id="edit-post",
        post=post,
        category=category,
        admin=False
    )


@app.route("/admin/post/edit/<category>/<timestamp>")
def edit_post_admin(category, timestamp):
    if category not in common.CATEGORIES:
        return abort(404)
    post = data.get_post(category, timestamp)
    if not post:
        return abort(404)
    return render_template(
        "edit_post.html",
        body_id="edit-post",
        post=post,
        category=category,
        admin=True
    )


@app.route("/post/edit/<category>", methods=["post"])
@app.route("/post/edit/<category>/token/<token>", methods=["post"])
def save_post(category, token=None):
    if category not in common.CATEGORIES:
        return abort(404)
    if token:
        try:
            timestamp = signer.loads(token)
        except BadSignature:
            return abort(401)
    else:
        timestamp = None
    try:
        post = data.save_post(
            category,
            timestamp=timestamp,
            admin=False,
            form=request.form,
            files=request.files,
        )
    except common.DataException as e:
        return abort(e.http_code)

    edit_post_url = url_for(
        "edit_post",
        category=category,
        token=signer.dumps(post["_timestamp"])
    )

    if post[common.FIELD_STATE] == common.STATE_TRASHED:
        return redirect(url_for("rest", category="already_trashed"))
    return render_template("confirmation.html", edit_post_url=edit_post_url)


@app.route("/admin/post/edit/<category>/<timestamp>", methods=["post"])
def save_post_admin(category, timestamp):
    if category not in common.CATEGORIES:
        return abort(404)
    try:
        data.save_post(
            category,
            timestamp=timestamp,
            admin=True,
            form=request.form,
            files=request.files,
        )
    except common.DataException as e:
        return abort(e.http_code)
    if "delete_image" in request.form:
        return redirect(request.url)
    return redirect(url_for("admin", category=category))


@app.route("/posts/<category>")
@app.route("/posts/<category>/page/<int:page>")
def posts(category, page=1):
    if category not in common.CATEGORIES:
        return abort(404)
    total_pages = (
        data.count_posts(category, common.STATE_PUBLISHED) // common.PAGINATION
    ) + 1
    posts = {}
    for post in data.get_posts(category, common.STATE_PUBLISHED, page=page):
        timestamp = post[common.FIELD_TIMESTAMP]
        posts[timestamp] = post
    return render_template(
        'posts.html',
        body_id=category,
        posts=posts,
        title=common.CATEGORIES[category],
        category=category,
        page=page,
        total_pages=total_pages,
    )


@app.route("/admin/posts/<category>")
def admin(category):
    if category not in common.CATEGORIES:
        return abort(404)
    posts = {}
    for state in common.STATES:
        posts[state] = state_posts = {}
        for post in data.get_posts(category, state):
            timestamp = post[common.FIELD_TIMESTAMP]
            state_posts[timestamp] = post
    return render_template(
        "admin.html",
        body_id="admin",
        posts=posts,
        title=common.CATEGORIES[category],
        category=category,
    )


@app.route("/posts/<category>/<timestamp>")
def post(category, timestamp):
    if category not in common.CATEGORIES:
        return abort(404)
    post = data.get_post(category, timestamp, common.STATE_PUBLISHED)
    if not post:
        return abort(404)
    return render_template(
        "post.html",
        body_id="post",
        post=post,
        category=category,
    )


@app.route("/post_image/<path:path>")
def post_image(path):
    if path.count("/") == 0:
        return send_from_directory(common.IMAGE_DIR, path)
    if path.count("/") != 3:
        return abort(404)
    category, state, timestamp, name = path.split("/")
    if category not in common.CATEGORIES:
        return abort(404)
    if state not in common.STATES:
        return abort(404)
    return send_from_directory(common.POSTS_DIR, path)


@app.route("/feed/<category>/rss.xml")
@cache.cached()
def feed(category):
    if category not in common.CATEGORIES:
        return abort(404)
    entries = []
    for post in data.get_posts(category, common.STATE_PUBLISHED, end=50):
        post["timestamp"] = post[common.FIELD_TIMESTAMP]
        post["link"] = url_for(
            "post",
            name=category,
            timestamp=post["timestamp"],
            _external=True,
        )
        entries.append({"content": post})
    title = f"{common.CATEGORIES[category]} AFPy.org"
    return render_template(
        "rss.xml",
        entries=entries,
        title=title,
        description=title,
        link=url_for(
            "feed",
            category=category,
            _external=True,
        ),
    )


@app.route("/planet/")
@app.route("/planet/rss.xml")
@cache.cached()
def planet():
    entries = []
    for name, url in common.PLANET.items():
        for entry in feedparser.parse(url).entries:
            if hasattr(entry, "updated_parsed"):
                date = entry.updated_parsed
            elif hasattr(entry, "published_parsed"):
                date = entry.published_parsed
            else:
                date = time.time()
            entry["timestamp"] = time.mktime(date) if date else time.time()
            entries.append({"feed": name, "content": entry})
    entries.sort(reverse=True, key=lambda entry: entry["content"]["timestamp"])
    return render_template(
        "rss.xml",
        entries=entries,
        title="Planet Python francophone",
        description="Nouvelles autour de Python en français",
        link=url_for("planet", _external=True),
    )


@app.route("/rss-jobs/RSS")
def jobs():
    return redirect("https://plone.afpy.org/rss-jobs/RSS", code=307)


@app.route("/status")
def status():
    stats = {}
    for category in common.CATEGORIES:
        stats[category] = {}
        for state in common.STATES:
            stats[category][state] = data.count_posts(category, state)

    os_stats = os.statvfs(__file__)
    stats["disk_free"] = os_stats.f_bavail * os_stats.f_frsize
    stats["disk_total"] = os_stats.f_blocks * os_stats.f_frsize
    stats["load_avg"] = os.getloadavg()
    return jsonify(stats)


@app.template_filter("rfc822_datetime")
def format_rfc822_datetime(timestamp):
    return email.utils.formatdate(int(timestamp))


@app.template_filter("parse_iso_datetime")
def parse_iso_datetime(iso_datetime, format_):
    if isinstance(iso_datetime, datetime):
        return iso_datetime.strftime(format_)
    return parse(iso_datetime).strftime(format_)


if app.env == "development":  # pragma: no cover
    from sassutils.wsgi import SassMiddleware
    app.wsgi_app = SassMiddleware(
        app.wsgi_app, {"afpy": ("sass", "static/css", "/static/css")}
    )
