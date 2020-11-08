from datetime import datetime

from flask_admin.contrib.peewee import ModelView
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
        AdminUser, backref="adminuser", help_text="Who approved the news entry", verbose_name="Approved by"
    )
    author = CharField(null=False, default="Admin", help_text="Author of the news entry", verbose_name="Author")
    image_url = TextField(null=True, help_text="Image for the news entry", verbose_name="Image URL")


class NewsEntry_Admin(ModelView):
    model_class = NewsEntry

    def is_accessible(self):
        # return login.current_user.is_authenticated
        return True


if not NewsEntry.table_exists():
    NewsEntry.create_table()
