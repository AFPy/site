from flask_wtf import FlaskForm
from wtforms import FileField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired


class NewsEntryForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    summary = StringField("Summary")
    content = TextAreaField("Content", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    author_email = StringField("Email address")
    image = FileField("Image")
