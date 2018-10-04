import email
import locale
import os
import time
from pathlib import Path
from xml.etree import ElementTree

import docutils.core
import docutils.writers.html5_polyglot
import feedparser
from dateutil.parser import parse
from flask import (Flask, abort, jsonify, redirect, render_template, request,
                   send_from_directory, url_for)
from flask_cache import Cache
from itsdangerous import BadSignature, URLSafeSerializer
from jinja2 import TemplateNotFound

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

cache = Cache(config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 600})
signer = URLSafeSerializer(os.environ.get('SECRET', 'changeme!'))
app = Flask(__name__)
cache.init_app(app)

PAGINATION = 12

PLANET = {
    'Emplois AFPy': 'https://www.afpy.org/feed/emplois/rss.xml',
    'Nouvelles AFPy': 'https://www.afpy.org/feed/actualites/rss.xml',
    'Anybox': 'https://anybox.fr/site-feed/RSS?set_language=fr',
    'Ascendances': 'https://ascendances.wordpress.com/feed/',
    'Code en Seine': 'https://codeenseine.fr/feeds/all.atom.xml',
    'Yaal': 'https://www.yaal.fr/blog/feeds/all.atom.xml'
}

MEETUPS = {
    'amiens': 'https://www.meetup.com/fr-FR/Python-Amiens',
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
    for status in ('waiting', 'published', 'trash'):
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
        if (timestamp / 'post.jpg').is_file():
            posts[timestamp.name]['image'] = '/'.join((
                'actualites', 'published', timestamp.name))
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


def _get_post(name, timestamp):
    for state in ('waiting', 'published', 'trash'):
        path = (root / name / state / timestamp / 'post.xml')
        if path.is_file():
            break
    else:
        return None
    tree = ElementTree.parse(path)
    post = {item.tag: (item.text or '').strip() for item in tree.iter()}
    post['state'] = state
    post['timestamp'] = timestamp
    return post


@app.route('/post/edit/<name>')
@app.route('/post/edit/<name>/token/<token>')
def edit_post(name, token=None):
    if name not in POSTS:
        abort(404)
    if token:
        try:
            timestamp = signer.loads(token)
        except BadSignature:
            abort(401)
        post = _get_post(name, timestamp)
        if not post:
            abort(404)
    else:
        post = {'state': 'waiting'}
    if post['state'] != 'waiting':
        return redirect(url_for('rest', name='already_published'))
    return render_template(
        'edit_post.html', body_id='edit-post', post=post, name=name,
        admin=False)


@app.route('/admin/post/edit/<name>/<timestamp>')
def edit_post_admin(name, timestamp):
    if name not in POSTS:
        abort(404)
    post = _get_post(name, timestamp)
    if not post:
        abort(404)
    return render_template(
        'edit_post.html', body_id='edit-post', post=post, name=name,
        admin=True)


def _save_post(name, timestamp, admin):
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
    elif (root / name / 'trash' / timestamp / 'post.xml').is_file():
        status = 'trash'
    else:
        abort(404)

    if status == 'published' and not admin:
        abort(401)

    post = root / name / status / timestamp / 'post.xml'
    tree = ElementTree.Element('entry')
    for key, value in request.form.items():
        element = ElementTree.SubElement(tree, key)
        element.text = value
    element = ElementTree.SubElement(tree, 'published')
    element.text = email.utils.formatdate(
        int(timestamp) if timestamp else time.time())
    ElementTree.ElementTree(tree).write(post)

    if admin:
        if 'publish' in request.form and status == 'waiting':
            (root / name / 'waiting' / timestamp).rename(
                root / name / 'published' / timestamp)
        elif 'unpublish' in request.form and status == 'published':
            (root / name / 'published' / timestamp).rename(
                root / name / 'trash' / timestamp)
        elif 'republish' in request.form and status == 'trash':
            (root / name / 'trash' / timestamp).rename(
                root / name / 'published' / timestamp)

    return _get_post(name, timestamp)


@app.route('/post/edit/<name>', methods=['post'])
@app.route('/post/edit/<name>/token/<token>', methods=['post'])
def save_post(name, token=None):
    if name not in POSTS:
        abort(404)
    if token:
        try:
            timestamp = signer.loads(token)
        except BadSignature:
            abort(401)
    else:
        timestamp = None
    post = _save_post(name, timestamp=timestamp, admin=False)
    edit_post_url = url_for(
        'edit_post', name=name, token=signer.dumps(post['timestamp']))
    return render_template('confirmation.html', edit_post_url=edit_post_url)


@app.route('/admin/post/edit/<name>/<timestamp>', methods=['post'])
def save_post_admin(name, timestamp):
    if name not in POSTS:
        abort(404)
    _save_post(name, timestamp=timestamp, admin=True)
    return redirect(url_for('admin', name=name))


@app.route('/posts/<name>')
@app.route('/posts/<name>/page/<int:page>')
def posts(name, page=1):
    if name not in POSTS:
        abort(404)
    path = root / name / 'published'
    timestamps = sorted(path.iterdir(), reverse=True)
    end = page * PAGINATION
    start = end - PAGINATION
    total_pages = (len(timestamps) // PAGINATION) + 1
    posts = {}
    for timestamp in timestamps[start:end]:
        tree = ElementTree.parse(timestamp / 'post.xml')
        posts[timestamp.name] = {item.tag: item.text for item in tree.iter()}
        if (timestamp / 'post.jpg').is_file():
            posts[timestamp.name]['image'] = '/'.join((
                name, 'published', timestamp.name))
    return render_template(
        'posts.html', body_id=name, posts=posts, title=POSTS[name], name=name,
        page=page, total_pages=total_pages)


@app.route('/admin/posts/<name>')
def admin(name):
    if name not in POSTS:
        abort(404)
    posts = {}
    for state in ('waiting', 'published', 'trash'):
        posts[state] = state_posts = {}
        timestamps = sorted((root / name / state).iterdir(), reverse=True)
        for timestamp in timestamps:
            tree = ElementTree.parse(timestamp / 'post.xml')
            state_posts[timestamp.name] = {
                item.tag: item.text for item in tree.iter()}
    return render_template(
        'admin.html', body_id='admin', posts=posts, title=POSTS[name],
        name=name)


@app.route('/posts/<name>/<timestamp>')
def post(name, timestamp):
    if name not in POSTS:
        abort(404)
    try:
        path = root / name / 'published' / timestamp
        tree = ElementTree.parse(path / 'post.xml')
    except Exception:
        abort(404)
    post = {item.tag: item.text for item in tree.iter()}
    if (path / 'post.jpg').is_file():
        post['image'] = '/'.join((name, 'published', timestamp))
    return render_template('post.html', body_id='post', post=post, name=name)


@app.route('/post_image/<path:path>/post.jpg')
def post_image(path):
    if path.count('/') != 2:
        abort(404)
    name, status, timestamp = path.split('/')
    if name not in POSTS:
        abort(404)
    if status not in ('published', 'waiting'):
        abort(404)
    return send_from_directory(root / path, 'post.jpg')


@app.route('/feed/<name>/rss.xml')
@cache.cached()
def feed(name):
    if name not in POSTS:
        abort(404)
    path = root / name / 'published'
    timestamps = sorted(path.iterdir(), reverse=True)[:50]
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


@app.route('/status')
def status():
    stats = {}
    for category in POSTS:
        stats[category] = {}
        for status in ('waiting', 'published'):
            stats[category][status] = len(list(
                (root / category / status).iterdir()))

    os_stats = os.statvfs(__file__)
    stats['disk_free'] = os_stats.f_bavail * os_stats.f_frsize
    stats['disk_total'] = os_stats.f_blocks * os_stats.f_frsize
    stats['load_avg'] = os.getloadavg()

    return jsonify(stats)


@app.template_filter('rfc822_datetime')
def format_rfc822_datetime(timestamp):
    return email.utils.formatdate(timestamp)


@app.template_filter('parse_iso_datetime')
def parse_iso_datetime(iso_datetime, format_):
    return parse(iso_datetime).strftime(format_)


if app.env == 'development':  # pragma: no cover
    from sassutils.wsgi import SassMiddleware
    app.wsgi_app = SassMiddleware(
        app.wsgi_app, {'afpy': ('sass', 'static/css', '/static/css')})
