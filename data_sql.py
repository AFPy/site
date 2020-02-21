# coding: utf-8
import datetime
import time
import peewee as pw
import os
from dateutil.parser import parse

import common


database = pw.SqliteDatabase('database.db', pragmas=(
    ('cache_size', -1024 * 64),
    ('journal_mode', 'wal'),
    ('foreign_keys', 1)))


class Article(pw.Model):
    category = pw.CharField(
        max_length=max(len(c) for c in common.CATEGORIES),
        choices=common.CATEGORIES.items(),
        index=True)
    state = pw.CharField(
        max_length=max(len(s) for s in common.STATES),
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
            (('category', 'state', 'timestamp'), False),
        )


try:
    Article.create_table(safe=False)
    import data_xml as data
    for category in common.CATEGORIES:
        for state in common.STATES:
            for post in data.get_posts(category, state):
                try:
                    timestamp = post.get(common.FIELD_TIMESTAMP)
                    if post.get(common.FIELD_IMAGE):
                        image = common.POSTS_DIR / post.get(common.FIELD_IMAGE)
                        name, ext = os.path.splitext(post.get(common.FIELD_IMAGE))
                        post['image'] = f"{category}.{timestamp}{ext}"
                        image.rename(common.IMAGE_DIR / post['image'])
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


def get_posts(category, state=common.STATE_PUBLISHED, page=1, end=None):
    articles = Article.select().where(
        Article.category == category,
        Article.state == state
    ).order_by(Article.timestamp.desc())
    if end:
        articles = articles.limit(end)
    else:
        articles = articles.paginate(page=page, paginate_by=common.PAGINATION)
    for article in articles:
        yield article


def get_post(category, timestamp, states=None):
    states = tuple(
        states if isinstance(states, (tuple, list)) else
        [states] if isinstance(states, str) else common.STATES.keys()
    )
    return Article.select().where(
        Article.category == category,
        Article.timestamp == timestamp,
        Article.state.in_(states)
    ).first()


def save_post(category, timestamp, admin, form, files):
    # TODO:
    pass
