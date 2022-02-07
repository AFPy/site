import json
import time

import feedparser
from flask import abort
from flask import Blueprint
from flask import render_template
from flask import url_for

from afpy.models.JobPost import JobPost
from afpy.models.NewsEntry import NewsEntry
from afpy import config


rss_bp = Blueprint("rss", __name__)


@rss_bp.route("/feed/<type>/rss.xml")
def feed_rss(type):
    name = ""
    entries = []
    if type == "emplois":
        name = "Emplois"
        entries = JobPost.select().where(JobPost.state == "published")
    elif type == "actualites":
        name = "Actualités"
        entries = NewsEntry.select().where(NewsEntry.state == "published")
    else:
        abort(404)
    title = f"{name} AFPy.org"
    return render_template(
        "pages/rss.xml",
        entries=entries,
        title=title,
        description=title,
        link=url_for("rss.feed_rss", type=type, _external=True),
        type=type,
    )
