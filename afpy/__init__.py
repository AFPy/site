import email
import os
import os.path as op

from flask import abort
from flask import Flask
from flask import render_template
from flask import request
from flask_admin import Admin
from flask_login import LoginManager
from flask_pagedown import PageDown
from peewee import DoesNotExist
from peewee import SqliteDatabase

from afpy import config
from afpy.utils import markdown_to_html

database = SqliteDatabase(database=config.DB_NAME)

application = Flask(__name__)

pagedown = PageDown(application)

application.debug = config.FLASK_DEBUG
application.secret_key = config.FLASK_SECRET_KEY
application.config["FLASK_ADMIN_SWATCH"] = "darkly"


# Initializes the login manager used for the admin
login_manager = LoginManager()
login_manager.init_app(application)


# Loads the user when a request is done to a protected page
@login_manager.user_loader
def load_user(uid):
    try:
        return AdminUser.get_by_id(uid)
    except DoesNotExist:
        return None


@application.errorhandler(404)
def page_not_found(e):
    return render_template("pages/404.html"), 404


from afpy.routes.home import home_bp
from afpy.routes.posts import posts_bp, post_render
from afpy.routes.jobs import jobs_bp, jobs_render
from afpy.routes.rss import rss_bp

application.register_blueprint(home_bp)
application.register_blueprint(posts_bp)
application.register_blueprint(jobs_bp)
application.register_blueprint(rss_bp)


from afpy.models.AdminUser import AdminUser, AdminUser_Admin
from afpy.models.NewsEntry import NewsEntry, NewsEntry_Admin
from afpy.models.JobPost import JobPost, JobPost_Admin
from afpy.models.Slug import Slug, SlugAdmin


from afpy.routes.admin import (
    AdminIndexView,
    NewAdminView,
    ChangePasswordView,
    JobsModerateView,
    NewsModerateView,
    CustomFileAdmin,
)

# Creates the Admin manager
admin = Admin(
    application,
    name="Afpy Admin",
    template_mode="bootstrap4",
    index_view=AdminIndexView(),
    base_template="admin/admin_master.html",
)

# Registers the views for each table
admin.add_view(JobsModerateView(name="Moderate Jobs", endpoint="jobs_moderation", category="Moderate"))
admin.add_view(NewsModerateView(name="Moderate News", endpoint="news_moderation", category="Moderate"))
admin.add_view(NewsEntry_Admin(NewsEntry))
admin.add_view(JobPost_Admin(JobPost))
admin.add_view(SlugAdmin(Slug))
admin.add_view(CustomFileAdmin(config.IMAGES_PATH, "/images/", name="Images Files"))
admin.add_view(NewAdminView(name="New Admin", endpoint="register_admin", category="Admin"))
admin.add_view(ChangePasswordView(name="Change password", endpoint="change_password", category="Admin"))
admin.add_view(AdminUser_Admin(AdminUser, category="Admin"))


@application.template_filter("rfc822_datetime")
def format_rfc822_datetime(timestamp):
    return email.utils.formatdate(int(timestamp))


@application.template_filter("md2html")
def format_markdown2html(content):
    return markdown_to_html(content)


@application.template_filter("slug_url")
def get_slug_url(item):
    url_root = request.url_root
    slug = item.slug.where(Slug.canonical == True).first()  # noqa
    if not slug:
        if isinstance(item, JobPost):
            return url_root[:-1] + "/emplois/" + str(item.id)
        else:
            return url_root[:-1] + "/actualites/" + str(item.id)
    else:
        return url_root[:-1] + slug.url


@application.route("/<path:slug>")
def slug_fallback(slug):
    slug = Slug.get_or_none(url="/" + slug)
    if not slug:
        abort(404)
    if slug.newsentry:
        return post_render(slug.newsentry.id)
    elif slug.jobpost:
        return jobs_render(slug.jobpost.id)
