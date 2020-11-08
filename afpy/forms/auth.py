# Copyright (C) 2020 ExploRêve
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from peewee import DoesNotExist
from werkzeug.security import check_password_hash
from wtforms import fields
from wtforms import form
from wtforms import validators

from afpy.models.AdminUser import AdminUser


def validate_email_or_username(form, field):
    try:
        AdminUser.get(AdminUser.email == field.data)
    except DoesNotExist:
        try:
            AdminUser.get(AdminUser.username == field.data)
        except DoesNotExist:
            raise validators.ValidationError("Unknown email or username")


def validate_password(form, field):
    try:
        user = AdminUser.get(AdminUser.email == field.data)
    except DoesNotExist:
        pass
    else:
        if not check_password_hash(user.password, form.password.data):
            raise validators.ValidationError("Invalid password")


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    email_or_username = fields.StringField(
        "Email or Username", validators=[validators.required(), validate_email_or_username]
    )
    password = fields.PasswordField(validators=[validators.required(), validate_password])


def validate_email_taken(form, field):
    try:
        AdminUser.get(AdminUser.email == field.data)
    except DoesNotExist:
        pass
    else:
        raise validators.ValidationError("Email taken")


class RegistrationForm(form.Form):
    username = fields.StringField(validators=[validators.required()])
    email = fields.StringField(validators=[validators.email(), validators.input_required(), validate_email_taken])
    password = fields.PasswordField(validators=[validators.required()])
