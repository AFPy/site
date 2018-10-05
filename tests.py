import pytest

from afpy import app


def test_home():
    response = app.test_client().get('/')
    assert response.status_code == 200


@pytest.mark.parametrize('name', ['', 'communaute'])
def test_html(name):
    response = app.test_client().get(f'/{name}')
    assert response.status_code == 200


@pytest.mark.parametrize('name', ['charte', 'a-propos'])
def test_rest(name):
    response = app.test_client().get(f'/docs/{name}')
    assert response.status_code == 200


def test_planet():
    response = app.test_client().get(f'/planet/')
    assert response.status_code == 200


def test_404():
    response = app.test_client().get('/unknown')
    assert response.status_code == 404
    response = app.test_client().get('/docs/unknown')
    assert response.status_code == 404
    response = app.test_client().get('/feed/unknown')
    assert response.status_code == 404


def test_read_posts():
    response = app.test_client().get('/posts/actualites')
    assert response.status_code == 200
    response = app.test_client().get('/posts/emplois')
    assert response.status_code == 200
