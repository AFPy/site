from datetime import datetime
from typing import Optional

from flask_admin.contrib.peewee import ModelView
from flask_login import current_user
from peewee import CharField
from peewee import DateTimeField
from peewee import ForeignKeyField
from peewee import TextField

from afpy.models import BaseModel
from afpy.models.AdminUser import AdminUser


class NewsEntry(BaseModel):
    title = TextField(null=False, help_text="Title of the news entry", verbose_name="Title")
    summary = TextField(null=True, help_text="Summary of the news entry", verbose_name="Summary")
    content = TextField(null=False, help_text="Content of the news entry", verbose_name="Content")
    dt_submitted = DateTimeField(
        null=False,
        default=datetime.now,
        help_text="When was the news entry submitted",
        verbose_name="Datetime Submitted",
    )
    dt_updated = DateTimeField(
        null=False, default=datetime.now, help_text="When was the news entry updated", verbose_name="Datetime Updated"
    )
    dt_published = DateTimeField(
        null=True, help_text="When was the news entry published", verbose_name="Datetime Published"
    )
    state = CharField(
        null=False,
        default="waiting",
        choices=[("waiting", "waiting"), ("published", "published"), ("rejected", "rejected")],
        help_text="Current state of the news entry",
        verbose_name="State",
    )
    approved_by = ForeignKeyField(
        AdminUser,
        null=True,
        default=None,
        backref="adminuser",
        help_text="Who approved the news entry",
        verbose_name="Approved by",
    )
    author = CharField(null=False, default="Admin", help_text="Author of the news entry", verbose_name="Author")
    author_email = CharField(null=True, help_text="Author email", verbose_name="Author Email")
    image_path = CharField(null=True, help_text="Image for the news entry", verbose_name="Image Path in filesystem")

    @classmethod
    def create(
        cls,
        title: str,
        content: str,
        author: str,
        author_email: Optional[str] = None,
        image_path: Optional[str] = None,
        summary: Optional[str] = None,
        dt_submitted: Optional[datetime] = None,
        dt_updated: Optional[datetime] = None,
        dt_published: Optional[datetime] = None,
        state: str = "waiting",
        approved_by: Optional[AdminUser] = None,
    ):
        if not dt_submitted:
            dt_submitted = datetime.now()
        if not dt_updated:
            dt_updated = datetime.now()
        new_article = super().create(
            title=title,
            content=content,
            author=author,
            author_email=author_email,
            image_path=image_path,
            summary=summary,
            dt_submitted=dt_submitted,
            dt_updated=dt_updated,
            dt_published=dt_published,
            state=state,
            approved_by=approved_by,
        )
        new_article.save()
        return new_article


class NewsEntry_Admin(ModelView):
    model_class = NewsEntry

    def is_accessible(self):
        return current_user.is_authenticated


if not NewsEntry.table_exists():
    NewsEntry.create_table()
