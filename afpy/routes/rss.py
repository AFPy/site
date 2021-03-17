import json
import time

import feedparser
from flask import abort
from flask import Blueprint
from flask import render_template
from flask import url_for

from afpy.models.JobPost import JobPost
from afpy.models.NewsEntry import NewsEntry
from afpy.static import AFPY_ROOT


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


@rss_bp.route("/planet/")
@rss_bp.route("/planet/rss.xml")
def planet_rss():
    entries = []
    with open(f"{AFPY_ROOT}/afpy/data/data.json", "r") as handle:
        planet_items = json.load(handle)["planet"]
    for name, url in planet_items.items():
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
        "pages/planet_rss.xml",
        entries=entries,
        title="Planet Python francophone",
        description="Nouvelles autour de Python en français",
        link=url_for("rss.planet_rss", _external=True),
    )
