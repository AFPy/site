import datetime
from pathlib import Path

import xmltodict
from tqdm import tqdm

from afpy.models.AdminUser import AdminUser
from afpy.models.JobPost import JobPost
from afpy.models.NewsEntry import NewsEntry

FOLDER_TO_READ = "posts"


def get_summary(xmldict) -> str:

    try:
        summ = xmldict["summary"]
    except KeyError:
        pass
    else:
        return summ

    try:
        summ = xmldict["summary"]["#text"]
    except KeyError:
        pass
    else:
        return summ

    try:
        summ = xmldict["summary"]["#html"]
    except KeyError:
        pass
    else:
        return summ

    raise ValueError("Found no summary")


def get_updated_submitted_dt(xmldict):
    try:
        dt_upd = datetime.datetime.strptime(xmldict["updated"][:19], "%Y-%m-%dT%H:%M:%S")
    except KeyError:
        dt_upd = datetime.datetime.now()

    try:
        dt_pub = datetime.datetime.strptime(xmldict["published"][:19], "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        dt_pub = datetime.datetime.strptime(xmldict["published"][:25], "%a, %d %b %Y %H:%M:%S")

    return dt_upd, dt_pub


def get_content(xmldict) -> str:
    try:
        cont = xmldict["content"]
    except KeyError:
        pass
    else:
        return cont

    try:
        cont = xmldict["content"]["#text"]
    except KeyError:
        pass
    else:
        return cont

    try:
        cont = xmldict["content"]["#html"]
    except KeyError:
        pass
    else:
        return cont

    raise ValueError("Found no content")


if __name__ == "__main__":
    admin_1 = AdminUser.get_by_id(1)
    for path in tqdm(Path(FOLDER_TO_READ).rglob("*.xml")):
        with open(path, "r", encoding="utf-8") as handle:
            xmldict = xmltodict.parse(handle.read(), encoding="utf-8")["entry"]

        dt_updated, dt_published = get_updated_submitted_dt(xmldict)
        dt_submitted = dt_published
        summary = get_summary(xmldict)
        content = get_content(xmldict)

        try:
            author = xmldict["author"]["name"]
        except KeyError:
            author = "Admin"

        location = xmldict.get("location")
        if not location:
            location = "Unknown"

        if "actualites" in str(path):
            if "published" in str(path):
                NewsEntry.create(
                    title=xmldict["title"],
                    summary=summary,
                    content=content,
                    author=author,
                    author_email=xmldict["email"],
                    image_url=None,
                    dt_published=dt_published,
                    dt_submitted=dt_submitted,
                    dt_updated=dt_updated,
                    state="published",
                    approved_by=admin_1,
                )
            elif "rejected" in str(path):
                NewsEntry.create(
                    title=xmldict["title"],
                    summary=summary,
                    content=content,
                    author=author,
                    author_email=xmldict["email"],
                    image_url=None,
                    dt_published=None,
                    dt_submitted=dt_submitted,
                    dt_updated=dt_updated,
                    state="rejected",
                    approved_by=admin_1,
                )
            elif "waiting" in str(path):
                NewsEntry.create(
                    title=xmldict["title"],
                    summary=summary,
                    content=content,
                    author=author,
                    author_email=xmldict["email"],
                    image_url=None,
                    dt_published=None,
                    dt_submitted=dt_submitted,
                    dt_updated=dt_updated,
                    state="waiting",
                    approved_by=None,
                )
        elif "emplois" in str(path):
            if "published" in str(path):
                JobPost.create(
                    title=xmldict["title"],
                    content=content,
                    company=xmldict["company"],
                    location=location,
                    contact_info=xmldict["contact"],
                    email=xmldict["email"],
                    phone=xmldict["phone"],
                    summary=summary,
                    dt_submitted=dt_submitted,
                    dt_updated=dt_updated,
                    dt_published=dt_published,
                    state="published",
                    approved_by=admin_1,
                )
            elif "rejected" in str(path):
                JobPost.create(
                    title=xmldict["title"],
                    content=content,
                    company=xmldict["company"],
                    location=location,
                    contact_info=xmldict["contact"],
                    email=xmldict["email"],
                    phone=xmldict["phone"],
                    summary=summary,
                    dt_submitted=dt_submitted,
                    dt_updated=dt_updated,
                    dt_published=None,
                    state="rejected",
                    approved_by=admin_1,
                )
            elif "waiting" in str(path):
                JobPost.create(
                    title=xmldict["title"],
                    content=content,
                    company=xmldict["company"],
                    location=location,
                    contact_info=xmldict["contact"],
                    email=xmldict["email"],
                    phone=xmldict["phone"],
                    summary=summary,
                    dt_submitted=dt_submitted,
                    dt_updated=dt_updated,
                    dt_published=None,
                    state="waiting",
                    approved_by=None,
                )
        else:
            raise ValueError("Invalid path")

# if __name__ == '__main__':
#     import json
#     with open("posts/actualites/published/1423208987/post.xml", "r") as handle:
#             xmldict = xmltodict.parse(handle.read(), encoding="utf-8")["entry"]
#             print(json.dumps(xmldict))
