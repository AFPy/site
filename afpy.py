import docutils.core
import docutils.writers.html5_polyglot
import feedparser
from flask import Flask, render_template

app = Flask(__name__)

FEEDS = {
    'news': 'https://www.afpy.org/rss-actualites/RSS',
    'jobs': 'https://www.afpy.org/rss-jobs/RSS',
    'planet': 'https://www.afpy.org/planet/rss.xml',
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/docs/<name>')
def rest(name):
    with open(f'templates/{name}.rst') as fd:
        html = docutils.core.publish_parts(
            source=fd.read(),
            writer=docutils.writers.html5_polyglot.Writer(),
            settings_overrides={'initial_header_level': 2})['body']
    return render_template('rst.html', html=html)


@app.route('/feed/<name>')
def feed(name):
    feed = feedparser.parse(FEEDS[name])
    return render_template('feed.html', entries=feed.entries)


if __name__ == '__main__':
    from sassutils.wsgi import SassMiddleware
    app.wsgi_app = SassMiddleware(app.wsgi_app, {
        'afpy': ('sass', 'static/css', '/static/css')})
    app.run(debug=True)
