from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import FileField
from wtforms import StringField
from wtforms.validators import DataRequired


class NewsEntryForm(FlaskForm):
    title = StringField("Titre", validators=[DataRequired()])
    summary = StringField("Résumé (optionnel)")
    content = PageDownField("Contenu de l'article", validators=[DataRequired()])
    author = StringField("Auteur", validators=[DataRequired()])
    author_email = StringField("Email (optionnel)")
    image = FileField("Image (optionnel)")
