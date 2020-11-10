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


class ChangePasswordForm(form.Form):
    old_password = fields.PasswordField(validators=[validators.required()])
    new_password = fields.PasswordField(validators=[validators.required()])
    new_password_confirmation = fields.PasswordField(validators=[validators.required()])
