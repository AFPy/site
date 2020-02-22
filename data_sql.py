# coding: utf-8
import datetime
import time
import peewee as pw
import os
import shutil
from dateutil.parser import parse

import common
import data_xml


database = pw.SqliteDatabase('database.db', pragmas=(
    ('cache_size', -1024 * 64),
    ('journal_mode', 'wal'),
    ('foreign_keys', 1)))


class Article(pw.Model):
    category = pw.CharField(
        max_length=max(map(len, common.CATEGORIES)),
        choices=common.CATEGORIES.items(),
        index=True)
    state = pw.CharField(
        max_length=max(map(len, common.STATES)),
        choices=common.STATES.items(),
        index=True)
    timestamp = pw.BigIntegerField(
        default=lambda: int(time.time()),
        unique=True,
        index=True)
    title = pw.TextField()
    summary = pw.TextField(null=True)
    content = pw.TextField(null=True)
    contact = pw.CharField(max_length=100, null=True)
    company = pw.CharField(max_length=100, null=True)
    address = pw.CharField(max_length=200, null=True)
    phone = pw.CharField(max_length=20, null=True)
    email = pw.CharField(max_length=300, null=True)
    image = pw.CharField(max_length=100, null=True)
    published = pw.DateTimeField(
        default=datetime.datetime.now,
        index=True)

    def __getitem__(self, item):
        return getattr(self, item, None)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    @property
    def _state(self):
        return self.state

    @property
    def _timestamp(self):
        return self.timestamp

    @property
    def _image(self):
        return self.image

    class Meta:
        database = database
        indexes = (
            (('category', 'timestamp'), False),
            (('category', 'timestamp', 'state'), False),
        )


try:
    Article.create_table(safe=False)
    for category in common.CATEGORIES:
        for state in common.STATES:
            for post in data_xml.get_posts(category, state):
                try:
                    timestamp = post.get(common.FIELD_TIMESTAMP)
                    if post.get(common.FIELD_IMAGE):
                        image = common.POSTS_DIR / post.get(common.FIELD_IMAGE)
                        name, ext = os.path.splitext(post.get(common.FIELD_IMAGE))
                        post['image'] = f"{category}.{timestamp}{ext}"
                        shutil.copy(str(image), str(common.IMAGE_DIR / post['image']))
                    Article.create(
                        category=category,
                        state=state,
                        timestamp=timestamp,
                        title=post.get('title'),
                        summary=post.get('summary'),
                        content=post.get('content'),
                        contact=post.get('contact'),
                        company=post.get('company'),
                        address=post.get('address'),
                        phone=post.get('phone'),
                        email=post.get('email'),
                        image=post.get('image'),
                        published=parse(post.get('published')).replace(tzinfo=None),
                    )
                except Exception as ex:
                    print(f"[{post.get(common.FIELD_TIMESTAMP)}] {ex}")
except pw.OperationalError:
    pass


def count_posts(category, state=common.STATE_PUBLISHED):
    return Article.select().where(
        Article.category == category,
        Article.state == state
    ).count()


def get_posts(category, state=common.STATE_PUBLISHED, page=None, end=None):
    articles = Article.select().where(
        Article.category == category,
        Article.state == state
    ).order_by(Article.timestamp.desc())
    if end:
        articles = articles.limit(end)
    elif page:
        articles = articles.paginate(page=page, paginate_by=common.PAGINATION)
    for article in articles:
        yield article


def get_post(category, timestamp, states=None):
    if states:
        states = tuple([states] if isinstance(states, str) else states)
        return Article.select().where(
            Article.category == category,
            Article.timestamp == timestamp,
            Article.state.in_(states)
        ).first()
    else:
        return Article.select().where(
            Article.category == category,
            Article.timestamp == timestamp,
        ).first()


def save_post(category, timestamp, admin, form, files):
    timestamp = timestamp or int(time.time())
    article = Article.get_or_none(
        category=category,
        timestamp=timestamp)

    if not article:
        article = Article(
            category=category,
            timestamp=timestamp,
            state=common.STATE_WAITING)

    if article.state == common.STATE_PUBLISHED and not admin:
        raise common.DataException(http_code=401)

    for key, value in form.items():
        if key.startswith('_'):
            continue
        setattr(article, key, value)

    uploaded_image = 'image' in files and files['image'].filename
    if (common.ACTION_DELETE_IMAGE in form or uploaded_image) and article.image:
        image_path = common.IMAGE_DIR / article.image
        if image_path.exists():
            image_path.unlink()
            article.image = None
    if uploaded_image:
        post_image = files['image']
        name, ext = os.path.splitext(post_image.filename)
        filename = f"{category}.{timestamp}{ext}"
        post_image.save(str(common.IMAGE_DIR / filename))
        article.image = filename

    if common.ACTION_TRASH in form \
            and article.state == common.STATE_PUBLISHED:
        article.state = common.STATE_TRASHED
    elif common.ACTION_EDIT in form \
            and article.state == common.STATE_PUBLISHED:
        article.state = common.STATE_WAITING
    elif admin and common.ACTION_PUBLISH in form \
            and article.state == common.STATE_WAITING:
        article.state = common.STATE_PUBLISHED
    elif admin and common.ACTION_UNPUBLISH in form \
            and article.state == common.STATE_PUBLISHED:
        article.state = common.STATE_WAITING
    elif admin and common.ACTION_UNPUBLISH in form \
            and article.state == common.STATE_TRASHED:
        article.state = common.STATE_PUBLISHED

    article.save()
    return article
