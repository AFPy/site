import datetime
import locale

import docutils.core
import docutils.writers.html5_polyglot
import feedparser
from flask import Flask, abort, render_template
from jinja2 import TemplateNotFound

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

app = Flask(__name__)

FEEDS = {
    'emplois': 'https://www.afpy.org/rss-jobs/RSS',
    'planet': 'https://www.afpy.org/planet/rss.xml',
}

MEETUPS = {
    'bruxelles': (
        'https://www.meetup.com/fr-FR/'
        'Belgium-Python-Meetup-aka-AperoPythonBe/events/rss/'),
    'grenoble': (
        'https://www.meetup.com/fr-FR/'
        'Groupe-dutilisateurs-Python-Grenoble/events/rss/'),
    'lille': 'https://www.meetup.com/fr-FR/Lille-py/events/rss/',
    'lyon': 'https://www.meetup.com/fr-FR/Python-AFPY-Lyon/events/rss/',
    'nantes': 'https://www.meetup.com/fr-FR/Nantes-Python-Meetup/events/rss/',
    'montpellier': (
        'https://www.meetup.com/fr-FR/Meetup-Python-Montpellier/events/rss/'),
}

for city, url in MEETUPS.items():
    FEEDS[f'meetup_{city}'] = url


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
@app.route('/<name>')
def pages(name='index'):
    entries = ()
    if name == 'index':
        entries = feedparser.parse(FEEDS['planet']).entries
    try:
        return render_template(
            f'{name}.html', body_id=name, meetups=MEETUPS, entries=entries)
    except TemplateNotFound:
        abort(404)


@app.route('/docs/<name>')
def rest(name):
    try:
        with open(f'templates/{name}.rst') as fd:
            parts = docutils.core.publish_parts(
                source=fd.read(),
                writer=docutils.writers.html5_polyglot.Writer(),
                settings_overrides={'initial_header_level': 2})
    except FileNotFoundError:
        abort(404)
    return render_template(
        'rst.html', body_id=name, html=parts['body'], title=parts['title'])


@app.route('/feed/<name>')
def feed(name):
    try:
        feed = feedparser.parse(FEEDS[name])
    except KeyError:
        abort(404)
    return render_template(
        'feed.html', body_id=name, entries=feed.entries,
        title=feed.feed.get('title'))


@app.template_filter('datetime')
def format_datetime(time_struct, format_):
    return datetime.datetime(*time_struct[:6]).strftime(format_)


if __name__ == '__main__':  # pragma: no cover
    from sassutils.wsgi import SassMiddleware
    app.wsgi_app = SassMiddleware(
        app.wsgi_app, {'afpy': ('sass', 'static/css', '/static/css')})
    app.run(debug=True)
