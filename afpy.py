import datetime
import email
import locale
import time
from pathlib import Path
from xml.etree import ElementTree

import docutils.core
import docutils.writers.html5_polyglot
import feedparser
from flask import Flask, abort, redirect, render_template, request, url_for
from flask_cache import Cache
from jinja2 import TemplateNotFound

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

cache = Cache(config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 600})
app = Flask(__name__)
cache.init_app(app)

PLANET = {
    'Emplois AFPy': 'https://plone.afpy.org/rss-jobs/RSS',
    'Nouvelles AFPy': 'https://plone.afpy.org/rss-actualites/RSS',
    'Anybox': 'https://anybox.fr/site-feed/RSS?set_language=fr',
    'Ascendances': 'https://ascendances.wordpress.com/feed/',
    'Code en Seine': 'https://codeenseine.fr/feeds/all.atom.xml',
    'Yaal': 'https://www.yaal.fr/blog/feeds/all.atom.xml'
}

MEETUPS = {
    'bruxelles': (
        'https://www.meetup.com/fr-FR/'
        'Belgium-Python-Meetup-aka-AperoPythonBe/'),
    'grenoble': (
        'https://www.meetup.com/fr-FR/Groupe-dutilisateurs-Python-Grenoble/'),
    'lille': 'https://www.meetup.com/fr-FR/Lille-py/',
    'lyon': 'https://www.meetup.com/fr-FR/Python-AFPY-Lyon/',
    'nantes': 'https://www.meetup.com/fr-FR/Nantes-Python-Meetup/',
    'montpellier': 'https://www.meetup.com/fr-FR/Meetup-Python-Montpellier/',
}

POSTS = {
    'actualites': 'Actualités',
    'emplois': 'Offres d’emploi',
}


root = Path(__file__).parent / 'posts'
for category in POSTS:
    for status in ('waiting', 'published'):
        (root / category / status).mkdir(parents=True, exist_ok=True)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def index():
    posts = {}
    path = root / 'actualites' / 'published'
    timestamps = sorted(path.iterdir(), reverse=True)[:4]
    for timestamp in timestamps:
        tree = ElementTree.parse(timestamp / 'post.xml')
        posts[timestamp.name] = {item.tag: item.text for item in tree.iter()}
    return render_template(
        'index.html', body_id='index', name='actualites', posts=posts)


@app.route('/<name>')
def pages(name):
    if name == 'index':
        return redirect(url_for('index'))
    try:
        return render_template(f'{name}.html', body_id=name, meetups=MEETUPS)
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


@app.route('/post/edit/<name>')
@app.route('/admin/post/edit/<name>/<timestamp>')
def edit_post(name, timestamp=None):
    if name not in POSTS:
        abort(404)
    if timestamp is None:
        state = 'waiting'
        post = {}
    else:
        for state in ('published', 'waiting'):
            if (root / name / state / timestamp / 'post.xml').is_file():
                path = (root / name / state / timestamp / 'post.xml')
                break
        else:
            abort(404)
        tree = ElementTree.parse(path)
        post = {item.tag: (item.text or '').strip() for item in tree.iter()}
    return render_template(
        'edit_post.html', body_id='edit-post', post=post, name=name,
        state=state)


@app.route('/post/edit/<name>', methods=['post'])
@app.route('/admin/post/edit/<name>/<timestamp>', methods=['post'])
def save_post(name, timestamp=None):
    original_timestamp = timestamp
    if name not in POSTS:
        abort(404)
    if timestamp is None:
        timestamp = str(int(time.time()))
        status = 'waiting'
        folder = root / name / 'waiting' / timestamp
        folder.mkdir()
        post = folder / 'post.xml'
    elif (root / name / 'waiting' / timestamp / 'post.xml').is_file():
        status = 'waiting'
    elif (root / name / 'published' / timestamp / 'post.xml').is_file():
        status = 'published'
    else:
        abort(404)
    post = root / name / status / timestamp / 'post.xml'
    tree = ElementTree.Element('item')
    for key in ('title', 'description', 'content', 'email'):
        element = ElementTree.SubElement(tree, key)
        element.text = request.form[key]
    element = ElementTree.SubElement(tree, 'pubDate')
    element.text = email.utils.formatdate(
        int(timestamp) if timestamp else time.time())
    ElementTree.ElementTree(tree).write(post)
    if original_timestamp:
        if 'publish' in request.form and status == 'waiting':
            (root / name / 'waiting' / timestamp).rename(
                root / name / 'published' / timestamp)
        elif 'unpublish' in request.form and status == 'published':
            (root / name / 'published' / timestamp).rename(
                root / name / 'waiting' / timestamp)
        return redirect(url_for('admin'))
    return redirect(url_for('rest', name='confirmation'))


@app.route('/posts/<name>')
def posts(name):
    if name not in POSTS:
        abort(404)
    path = root / name / 'published'
    timestamps = sorted(path.iterdir(), reverse=True)[:12]
    posts = {}
    for timestamp in timestamps:
        tree = ElementTree.parse(timestamp / 'post.xml')
        posts[timestamp.name] = {item.tag: item.text for item in tree.iter()}
    return render_template(
        'posts.html', body_id=name, posts=posts, title=POSTS[name], name=name)


@app.route('/admin/posts')
def admin():
    posts = {}
    for name, label in POSTS.items():
        posts[(name, label)] = name_posts = {}
        for state in ('waiting', 'published'):
            name_posts[state] = state_posts = {}
            timestamps = sorted((root / name / state).iterdir(), reverse=True)
            for timestamp in timestamps:
                tree = ElementTree.parse(timestamp / 'post.xml')
                state_posts[timestamp.name] = {
                    item.tag: item.text for item in tree.iter()}
    return render_template('admin.html', body_id='admin', posts=posts)


@app.route('/posts/<name>/<timestamp>')
def post(name, timestamp):
    if name not in POSTS:
        abort(404)
    try:
        tree = ElementTree.parse(
            root / name / 'published' / timestamp / 'post.xml')
    except Exception:
        abort(404)
    post = {item.tag: item.text for item in tree.iter()}
    return render_template('post.html', body_id='post', post=post)


@app.route('/feed/<name>/rss.xml')
@cache.cached()
def feed(name):
    if name not in POSTS:
        abort(404)
    path = root / name / 'published'
    timestamps = sorted(path.iterdir(), reverse=True)[:12]
    entries = []
    for timestamp in timestamps:
        tree = ElementTree.parse(timestamp / 'post.xml')
        entry = {item.tag: item.text for item in tree.iter()}
        entry['timestamp'] = int(timestamp.name)
        entry['link'] = url_for(
            'post', name=name, timestamp=timestamp.name, _external=True)
        entries.append({'content': entry})
    title = f'{POSTS[name]} AFPy.org'
    return render_template(
        'rss.xml', entries=entries, title=title, description=title,
        link=url_for('feed', name=name, _external=True))


@app.route('/planet/')
@app.route('/planet/rss.xml')
@cache.cached()
def planet():
    entries = []
    for name, url in PLANET.items():
        for entry in feedparser.parse(url).entries:
            date = getattr(entry, 'published_parsed', entry.updated_parsed)
            entry['timestamp'] = time.mktime(date)
            entries.append({'feed': name, 'content': entry})
    entries.sort(reverse=True, key=lambda entry: entry['content']['timestamp'])
    return render_template(
        'rss.xml', entries=entries, title='Planet Python francophone',
        description='Nouvelles autour de Python en français',
        link=url_for('planet', _external=True))


@app.route('/rss-jobs/RSS')
def jobs():
    return redirect('https://plone.afpy.org/rss-jobs/RSS', code=307)


@app.template_filter('parse_rfc822_datetime')
def parse_rfc822_datetime(rfc822_datetime):
    return email.utils.parsedate_tz(rfc822_datetime)


@app.template_filter('datetime')
def format_datetime(time_struct, format_):
    return datetime.datetime(*time_struct[:6]).strftime(format_)


@app.template_filter('rfc822_datetime')
def format_rfc822_datetime(timestamp):
    return email.utils.formatdate(timestamp)


if app.env == 'development':  # pragma: no cover
    from sassutils.wsgi import SassMiddleware
    app.wsgi_app = SassMiddleware(
        app.wsgi_app, {'afpy': ('sass', 'static/css', '/static/css')})
