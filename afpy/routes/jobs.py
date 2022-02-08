from flask import abort
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from peewee import DoesNotExist
from werkzeug.utils import secure_filename

from afpy.forms.JobPost import JobPostForm
from afpy.models.JobPost import JobPost
from afpy import config


jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("/emplois/<int:post_id>")
def jobs_render(post_id: int):
    try:
        job = JobPost.get_by_id(post_id)
    except DoesNotExist:
        abort(404)
    return render_template("pages/job.html", body_id="emplois", job=job, name=job.title)


@jobs_bp.route("/emplois")
@jobs_bp.route("/emplois/page/<int:current_page>")
def jobs_page(current_page: int = 1):
    total_pages = (JobPost.select().where(JobPost.state == "published").count() // config.NEWS_PER_PAGE) + 1
    jobs = (
        JobPost.select()
        .where(JobPost.state == "published")
        .order_by(JobPost.dt_submitted.desc())
        .paginate(current_page, config.NEWS_PER_PAGE)
    )
    return render_template(
        "pages/jobs.html",
        body_id="emplois",
        jobs=jobs,
        title="Offres d'emploi",
        current_page=current_page,
        total_pages=total_pages,
    )


@jobs_bp.route("/emplois/new", methods=["GET"])
def new_job():
    return render_template("pages/edit_job.html")
