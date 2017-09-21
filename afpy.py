from pathlib import Path

from flask import Flask, render_template, abort

app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
@app.route('/<template_name>')
def pages(template_name='index'):
    if Path(f'templates/{template_name}.html').exists():
        return render_template(f'{template_name}.html')
    abort(404)


if __name__ == '__main__':
    from sassutils.wsgi import SassMiddleware
    app.wsgi_app = SassMiddleware(app.wsgi_app, {
        'afpy': ('sass', 'static/css', '/static/css')})
    app.run(debug=True)
