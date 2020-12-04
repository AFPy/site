from flask_admin.contrib.peewee import ModelView
from flask_login import current_user
from peewee import BooleanField
from peewee import CharField
from peewee import ForeignKeyField

from afpy.models import BaseModel
from afpy.models.JobPost import JobPost
from afpy.models.NewsEntry import NewsEntry


class Slug(BaseModel):
    url = CharField(null=False, help_text="From URL", verbose_name="From URL", unique=True, index=True)
    jobpost = ForeignKeyField(JobPost, backref="slug", null=True)
    newsentry = ForeignKeyField(NewsEntry, backref="slug", null=True)
    canonical = BooleanField(default=True)


class SlugAdmin(ModelView):
    model_class = Slug

    def is_accessible(self):
        return current_user.is_authenticated


if not Slug.table_exists():
    Slug.create_table()
