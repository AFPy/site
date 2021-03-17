from datetime import datetime

from flask_admin.contrib.peewee import ModelView
from flask_login import current_user
from peewee import CharField
from peewee import DateTimeField
from peewee import TextField
from werkzeug.security import generate_password_hash

from afpy.models import BaseModel


class AdminUser(BaseModel):
    username = CharField(null=False, help_text="Username of admin user", verbose_name="Username")
    email = CharField(null=False, help_text="Email of admin user", verbose_name="Email")
    password = TextField(null=False, help_text="Hashed password of admin user", verbose_name="Password")
    dt_added = DateTimeField(
        null=False, default=datetime.now, help_text="When was the admin user entry added", verbose_name="Datetime Added"
    )

    def get_id(self) -> int:
        return int(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    # Required for administrative interface
    def __unicode__(self):
        return self.username


class AdminUser_Admin(ModelView):
    model_class = AdminUser

    def is_accessible(self):
        return current_user.is_authenticated


if not AdminUser.table_exists():
    AdminUser.create_table()
    try:
        AdminUser.get_by_id(1)
    except AdminUser.DoesNotExist:
        AdminUser.create(
            email="admin@admin.org",
            username="admin",
            password=generate_password_hash("password"),
            dt_added=datetime.now(),
        ).save()
