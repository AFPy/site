import docutils.core
import docutils.writers.html5_polyglot
from flask import Flask, render_template

app = Flask(__name__)


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


if __name__ == '__main__':
    from sassutils.wsgi import SassMiddleware
    app.wsgi_app = SassMiddleware(app.wsgi_app, {
        'afpy': ('sass', 'static/css', '/static/css')})
    app.run(debug=True)
