from flask_wtf import FlaskForm
from wtforms import FileField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms import validators
from wtforms.validators import DataRequired


def validate_email_or_phone(form, field):
    if not form.email.data and not form.phone.data:
        raise validators.ValidationError("Must have phone or email")


class JobPostForm(FlaskForm):
    title = StringField("Titre", validators=[DataRequired()])
    summary = StringField("Résumé (optionnel)")
    content = TextAreaField("Content", validators=[DataRequired()])
    company = StringField("Entreprise", validators=[DataRequired()])
    location = StringField("Addresse", validators=[DataRequired()])
    contact_info = StringField("Personne à contacter", validators=[DataRequired()])
    email = StringField("Email", validators=[validate_email_or_phone])
    phone = StringField("Téléphone", validators=[validate_email_or_phone])
    image = FileField("Image (optionnel)")
