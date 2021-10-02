from flask import abort
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from peewee import DoesNotExist
from werkzeug.utils import secure_filename

from afpy.forms.NewsEntry import NewsEntryForm
from afpy.models.NewsEntry import NewsEntry
from afpy import config

posts_bp = Blueprint("posts", __name__)


@posts_bp.route("/actualites/<int:post_id>")
def post_render(post_id: int):
    try:
        post = NewsEntry.get_by_id(post_id)
    except DoesNotExist:
        abort(404)
    return render_template("pages/post.html", body_id="actualites", post=post, name=post.title)


@posts_bp.route("/actualites")
@posts_bp.route("/actualites/page/<int:current_page>")
def posts_page(current_page: int = 1):
    total_pages = (NewsEntry.select().where(NewsEntry.state == "published").count() // config.NEWS_PER_PAGE) + 1
    posts = (
        NewsEntry.select()
        .where(NewsEntry.state == "published")
        .order_by(NewsEntry.dt_submitted.desc())
        .paginate(current_page, config.NEWS_PER_PAGE)
    )
    return render_template(
        "pages/posts.html",
        body_id="actualites",
        posts=posts,
        title="Actualités",
        current_page=current_page,
        total_pages=total_pages,
    )


@posts_bp.route("/actualites/new", methods=["GET", "POST"])
def new_post():
    form = NewsEntryForm()
    if form.validate_on_submit():
        title = form.title.data
        summary = form.summary.data
        content = form.content.data
        author = form.author.data
        author_email = form.author_email.data

        new_post = NewsEntry.create(
            title=title, summary=summary, content=content, author=author, author_email=author_email
        )
        flash("Merci ! Votre article apparaîtra après validation par un des administrateurs.", "success")

        if form.image.data:
            extension = secure_filename(form.image.data.filename).split(".")[-1].lower()
            filename = f"emplois.{new_post.id}.{extension}"
            filepath = f"{config.IMAGES_PATH}/{filename}"
            request.files[form.image.name].save(filepath)
            new_post.image_path = filename
            new_post.save()
        return redirect(url_for("posts.posts_page", current_page=1))
    return render_template("pages/edit_post.html", form=form, post=None, body_id="edit-post")
