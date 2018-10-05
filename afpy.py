import email
import locale
import os
import time

import docutils.core
import docutils.writers.html5_polyglot
import feedparser
from dateutil.parser import parse
from flask import (Flask, abort, jsonify, redirect, render_template, request,
                   send_from_directory, url_for)
from flask_cache import Cache
from itsdangerous import BadSignature, URLSafeSerializer
from jinja2 import TemplateNotFound

import data_xml as data

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
    'Yaal': 'https://www.yaal.fr/blog/feeds/all.atom.xml',
}

MEETUPS = {
    'amiens': 'https://www.meetup.com/fr-FR/Python-Amiens',
    'bruxelles': 'https://www.meetup.com/fr-FR/'
    'Belgium-Python-Meetup-aka-AperoPythonBe/',
    'grenoble': 'https://www.meetup.com/fr-FR/'
    'Groupe-dutilisateurs-Python-Grenoble/',
    'lille': 'https://www.meetup.com/fr-FR/Lille-py/',
    'lyon': 'https://www.meetup.com/fr-FR/Python-AFPY-Lyon/',
    'nantes': 'https://www.meetup.com/fr-FR/Nantes-Python-Meetup/',
    'montpellier': 'https://www.meetup.com/fr-FR/Meetup-Python-Montpellier/',
}


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def index():
    posts = {}
    for post in data.get_posts(data.POST_ACTUALITIES, end=4):
        timestamp = post[data.TIMESTAMP]
        posts[timestamp] = post
    return render_template(
        'index.html',
        body_id='index',
        name=data.POST_ACTUALITIES,
        posts=posts
    )


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
                settings_overrides={'initial_header_level': 2},
            )
    except FileNotFoundError:
        abort(404)
    return render_template(
        'rst.html',
        body_id=name,
        html=parts['body'],
        title=parts['title']
    )


@app.route('/post/edit/<name>')
@app.route('/post/edit/<name>/token/<token>')
def edit_post(name, token=None):
    if name not in data.POSTS:
        abort(404)
    if token:
        try:
            timestamp = signer.loads(token)
        except BadSignature:
            abort(401)
        post = data.get_post(name, timestamp)
        if not post:
            abort(404)
    else:
        post = {data.STATE: data.STATE_WAITING}
    if post[data.STATE] != data.STATE_WAITING:
        return redirect(url_for('rest', name='already_published'))
    return render_template(
        'edit_post.html',
        body_id='edit-post',
        post=post,
        name=name,
        admin=False,
    )


@app.route('/admin/post/edit/<name>/<timestamp>')
def edit_post_admin(name, timestamp):
    if name not in data.POSTS:
        abort(404)
    post = data.get_post(name, timestamp)
    if not post:
        abort(404)
    return render_template(
        'edit_post.html',
        body_id='edit-post',
        post=post,
        name=name,
        admin=True
    )


@app.route('/post/edit/<name>', methods=['post'])
@app.route('/post/edit/<name>/token/<token>', methods=['post'])
def save_post(name, token=None):
    if name not in data.POSTS:
        abort(404)
    if token:
        try:
            timestamp = signer.loads(token)
        except BadSignature:
            abort(401)
    else:
        timestamp = None
    try:
        post = data.save_post(
            name, timestamp=timestamp, admin=False,
            form=request.form, files=request.files
        )
    except data.DataException as e:
        abort(e.http_code)
    edit_post_url = url_for(
        'edit_post', name=name, token=signer.dumps(post['_timestamp'])
    )
    return render_template(
        'confirmation.html',
        edit_post_url=edit_post_url
    )


@app.route('/admin/post/edit/<name>/<timestamp>', methods=['post'])
def save_post_admin(name, timestamp):
    if name not in data.POSTS:
        abort(404)
    try:
        data.save_post(
            name, timestamp=timestamp, admin=True,
            form=request.form, files=request.files
        )
    except data.DataException as e:
        abort(e.http_code)
    if 'delete_image' in request.form:
        return redirect(request.url)
    return redirect(url_for('admin', name=name))


@app.route('/posts/<name>')
@app.route('/posts/<name>/page/<int:page>')
def posts(name, page=1):
    if name not in data.POSTS:
        abort(404)
    end = page * PAGINATION
    start = end - PAGINATION
    total_pages = (
        data.count_posts(name, data.STATE_PUBLISHED) // PAGINATION
    ) + 1
    posts = {}
    for post in data.get_posts(
        name, data.STATE_PUBLISHED, start=start, end=end
    ):
        timestamp = post[data.TIMESTAMP]
        posts[timestamp] = post
    return render_template(
        'posts.html',
        body_id=name,
        posts=posts,
        title=data.POSTS[name],
        name=name,
        page=page,
        total_pages=total_pages,
    )


@app.route('/admin/posts/<name>')
def admin(name):
    if name not in data.POSTS:
        abort(404)
    posts = {}
    for state in data.STATES:
        posts[state] = state_posts = {}
        for post in data.get_posts(name, state):
            timestamp = post[data.TIMESTAMP]
            state_posts[timestamp] = post
    return render_template(
        'admin.html',
        body_id='admin',
        posts=posts,
        title=data.POSTS[name],
        name=name,
    )


@app.route('/posts/<name>/<timestamp>')
def post(name, timestamp):
    if name not in data.POSTS:
        abort(404)
    post = data.get_post(name, timestamp, data.STATE_PUBLISHED)
    if not post:
        abort(404)
    return render_template(
        'post.html',
        body_id='post',
        post=post,
        name=name
    )


@app.route('/post_image/<path:path>')
def post_image(path):
    if path.count('/') != 3:
        abort(404)
    category, state, timestamp, name = path.split('/')
    if category not in data.POSTS:
        abort(404)
    if state not in data.STATES:
        abort(404)
    return send_from_directory(data.root, path)


@app.route('/feed/<name>/rss.xml')
@cache.cached()
def feed(name):
    if name not in data.POSTS:
        abort(404)
    entries = []
    for post in data.get_posts(name, data.STATE_PUBLISHED, end=50):
        timestamp = post[data.TIMESTAMP]
        post['link'] = url_for(
            'post', name=name, timestamp=timestamp, _external=True
        )
        entries.append({'content': post})
    title = f'{data.POSTS[name]} AFPy.org'
    return render_template(
        'rss.xml',
        entries=entries,
        title=title,
        description=title,
        link=url_for('feed', name=name, _external=True),
    )


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
        'rss.xml',
        entries=entries,
        title='Planet Python francophone',
        description='Nouvelles autour de Python en français',
        link=url_for('planet', _external=True),
    )


@app.route('/rss-jobs/RSS')
def jobs():
    return redirect('https://plone.afpy.org/rss-jobs/RSS', code=307)


@app.route('/status')
def status():
    stats = {}
    for category in data.POSTS:
        stats[category] = {}
        for state in data.STATES:
            stats[category][state] = data.count_posts(category, state)

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
        app.wsgi_app, {'afpy': ('sass', 'static/css', '/static/css')}
    )
