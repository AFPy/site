from datetime import datetime

from flask_admin.contrib.peewee import ModelView
from peewee import CharField
from peewee import DateTimeField
from peewee import TextField

from afpy.models import BaseModel


class AdminUser(BaseModel):
    username = CharField(null=False, help_text="Username of admin user", verbose_name="Username")
    email = CharField(null=False, help_text="Email of admin user", verbose_name="Email")
    password = TextField(null=False, help_text="Hashed password of admin user", verbose_name="Password")
    dt_added = DateTimeField(
        null=False, default=datetime.now, help_text="When was the admin user entry added", verbose_name="Datetime Added"
    )


class AdminUser_Admin(ModelView):
    model_class = AdminUser

    def is_accessible(self):
        # return login.current_user.is_authenticated
        return True


if not AdminUser.table_exists():
    AdminUser.create_table()
