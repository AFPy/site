import pytest

from afpy import app


def test_home():
    response = app.test_client().get('/')
    assert response.status_code == 200


@pytest.mark.parametrize('name', ['index', 'communaute'])
def test_html(name):
    response = app.test_client().get(f'/{name}')
    assert response.status_code == 200


@pytest.mark.parametrize('name', ['charte', 'a-propos'])
def test_rest(name):
    response = app.test_client().get(f'/docs/{name}')
    assert response.status_code == 200


@pytest.mark.parametrize('name', ['planet', 'meetup_lyon'])
def test_feed(name):
    response = app.test_client().get(f'/feed/{name}')
    assert response.status_code == 200


def test_404():
    response = app.test_client().get('/unknown')
    assert response.status_code == 404
    response = app.test_client().get('/docs/unknown')
    assert response.status_code == 404
    response = app.test_client().get('/feed/unknown')
    assert response.status_code == 404
