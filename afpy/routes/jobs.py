from flask import abort
from flask import Blueprint
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


@jobs_bp.route("/emplois/page/<int:current_page>")
def jobs_page(current_page: int = 1):
    submitted = request.args.get("submitted", False)
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
        submitted=submitted,
    )


@jobs_bp.route("/emplois/new", methods=["GET", "POST"])
def new_job():
    form = JobPostForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        company = form.company.data
        location = form.location.data
        contact_info = form.contact_info.data
        email = form.email.data
        phone = form.phone.data
        summary = form.summary.data

        new_job = JobPost.create(
            title=title,
            content=content,
            company=company,
            location=location,
            contact_info=contact_info,
            email=email,
            phone=phone,
            summary=summary,
        )

        if form.image.data:
            extension = secure_filename(form.image.data.filename).split(".")[-1].lower()
            filename = f"emplois.{new_job.id}.{extension}"
            filepath = f"{config.IMAGES_PATH}/{filename}"
            request.files[form.image.name].save(filepath)
            new_job.image_path = filename
            new_job.save()
        return redirect(url_for("jobs.jobs_page", current_page=1, submitted=True))
    return render_template("pages/edit_job.html", form=form, post=None, body_id="edit-post")
