# coding: utf-8
import os
import shutil
from pathlib import Path
from xml.etree import ElementTree

from dateutil.parser import parse
from html2text import html2text

from afpy.models.AdminUser import AdminUser
from afpy.models.JobPost import JobPost
from afpy.models.NewsEntry import NewsEntry
from afpy.models.Slug import Slug

PAGINATION = 12

CATEGORY_ACTUALITIES = "actualites"
CATEGORY_JOBS = "emplois"

CATEGORIES = {CATEGORY_ACTUALITIES: "Actualités", CATEGORY_JOBS: "Offres d’emploi"}

STATE_WAITING = "waiting"
STATE_PUBLISHED = "published"
STATE_TRASHED = "trashed"
STATES = {STATE_WAITING: "En attente", STATE_PUBLISHED: "Publié", STATE_TRASHED: "Supprimé"}

FIELD_IMAGE = "_image"
FIELD_TIMESTAMP = "_timestamp"
FIELD_STATE = "_state"
FIELD_PATH = "_path"
FIELD_DIR = "_dir"

BASE_DIR = "posts"
BASE_FILE = "post.xml"
BASE_IMAGE = "post.jpg"

ROOT_DIR = Path(__file__).parent
POSTS_DIR = ROOT_DIR / BASE_DIR
IMAGE_DIR = ROOT_DIR / "images"
IMAGE_DIR.mkdir(exist_ok=True)


def get_posts(category, state=STATE_PUBLISHED, page=None, end=None):
    start = 0
    if page and not end:
        end = page * PAGINATION
        start = end - PAGINATION
    path = POSTS_DIR / category / state
    timestamps = sorted(path.iterdir(), reverse=True)
    timestamps = timestamps[start:end] if end else timestamps[start:]
    for timestamp in timestamps:
        post = get_post(category, timestamp.name, state)
        if post:
            yield post


def get_post(category, timestamp, states=None):
    states = tuple(
        states if isinstance(states, (tuple, list)) else [states] if isinstance(states, str) else STATES.keys()
    )
    for state in states:
        dir = POSTS_DIR / category / state / timestamp
        path = dir / BASE_FILE
        if path.is_file():
            break
    else:
        return None
    tree = ElementTree.parse(path)
    post = {item.tag: (item.text or "").strip() for item in tree.iter()}

    # Calculated fields
    image = post.get("image") or post.get("old_image") or BASE_IMAGE
    if (dir / image).is_file():
        post[FIELD_IMAGE] = "/".join((category, state, timestamp, image))
    post[FIELD_TIMESTAMP] = timestamp
    post[FIELD_STATE] = state
    post[FIELD_DIR] = dir
    post[FIELD_PATH] = path
    return post


if __name__ == "__main__":
    admin_1 = AdminUser.get_by_id(1)
    for category in CATEGORIES:
        for state in STATES:
            for post in get_posts(category, state):
                timestamp = post.get(FIELD_TIMESTAMP)
                if post.get(FIELD_IMAGE):
                    image = POSTS_DIR / post.get(FIELD_IMAGE)
                    name, ext = os.path.splitext(post.get(FIELD_IMAGE))
                    post["image"] = f"{category}.{timestamp}{ext}"
                    shutil.copy(str(image), str(IMAGE_DIR / post["image"]))
                if category == "actualites":
                    new_post = NewsEntry.create(
                        title=post.get("title", "(untitled)"),
                        summary=post.get("summary"),
                        content=html2text(post.get("content", "")),
                        author="Admin",
                        author_email=post.get("email"),
                        image_path=post.get("image"),
                        dt_published=parse(post.get("published")).replace(tzinfo=None)
                        if state == "published"
                        else None,
                        dt_submitted=parse(post.get("published")).replace(tzinfo=None),
                        dt_updated=parse(post.get("published")).replace(tzinfo=None),
                        state=state,
                        approved_by=admin_1 if state == "published" or state == "rejected" else None,
                    )
                    Slug.create(url=f"/posts/actualites/{post.get(FIELD_TIMESTAMP)}", newsentry=new_post)
                    post_id = post.get("id")
                    if post_id:
                        Slug.create(url=post_id.split("afpy.org")[-1], newsentry=new_post)
                else:
                    new_job = JobPost.create(
                        title=post.get("title", "(untitled)"),
                        summary=post.get("summary"),
                        content=html2text(post.get("content", "")),
                        company=post.get("company", "(unknown)"),
                        email=post.get("email"),
                        phone=post.get("phone", "(no phone)" if post.get("email") is None else None),
                        location=post.get("address", "(no addr)"),
                        contact_info=post.get("contact"),
                        dt_published=parse(post.get("published")).replace(tzinfo=None)
                        if state == "published"
                        else None,
                        dt_submitted=parse(post.get("published")).replace(tzinfo=None),
                        dt_updated=parse(post.get("published")).replace(tzinfo=None),
                        state=state,
                        approved_by=admin_1 if state == "published" or state == "rejected" else None,
                        image_path=post.get("image"),
                    )
                    Slug.create(url=f"/posts/emplois/{post.get(FIELD_TIMESTAMP)}", jobpost=new_job)
                    post_id = post.get("id")
                    if post_id:
                        Slug.create(url=post_id.split("afpy.org")[-1], jobpost=new_job)
