# coding: utf-8
import datetime
import time
import peewee as db

from dateutil.parser import parse

import common


database = db.SqliteDatabase('database.db', pragmas=(
    ('cache_size', -1024 * 64),
    ('journal_mode', 'wal'),
    ('foreign_keys', 1)))


class Article(db.Model):
    category = db.CharField(
        max_length=max(len(c) for c in common.CATEGORIES),
        choices=common.CATEGORIES.items(),
        index=True)
    state = db.CharField(
        max_length=max(len(s) for s in common.STATES),
        choices=common.STATES.items(),
        index=True)
    timestamp = db.BigIntegerField(
        default=lambda: int(time.time()),
        unique=True,
        index=True)
    title = db.TextField()
    summary = db.TextField(null=True)
    content = db.TextField(null=True)
    contact = db.CharField(
        max_length=100,
        null=True)
    company = db.CharField(
        max_length=100,
        null=True)
    address = db.CharField(
        max_length=200,
        null=True)
    phone = db.CharField(
        max_length=20,
        null=True)
    email = db.CharField(
        max_length=300,
        null=True)
    image = db.CharField(
        max_length=100,
        null=True)
    published = db.DateTimeField(
        default=datetime.datetime.now,
        index=True)

    def __getitem__(self, item):
        return getattr(self, item, None)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

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
                print(category, state, post[common.FIELD_TIMESTAMP])
                Article.create(
                    category=category,
                    state=state,
                    timestamp=post.get(common.FIELD_TIMESTAMP),
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
except db.OperationalError:
    pass


def count_posts(category, state=common.STATE_PUBLISHED):
    return Article.select().where(
        Article.category == category,
        Article.state == state
    ).count()


def get_posts(category, state=common.STATE_PUBLISHED, start=0, end=None):
    articles = Article.select().where(
        Article.category == category,
        Article.state == state
    ).order_by(Article.timestamp.desc())
    if end:
        articles = articles.limit(end)
    for article in articles:
        yield article


def get_post(category, timestamp, states=None):
    states = tuple(
        states
        if isinstance(states, (tuple, list))
        else [states]
        if isinstance(states, str)
        else common.STATES.keys()
    )
    return Article.select().where(
        Article.category == category,
        Article.timestamp == timestamp,
        Article.state.in_(states)
    ).first()


def save_post(category, timestamp, admin, **data):
    # TODO:
    pass


def add_image(category, state, timestamp, image):
    # TODO:
    pass
