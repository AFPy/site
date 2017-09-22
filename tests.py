import pytest

from afpy import app


def test_no_arguments():
    response = app.test_client().get('/')
    assert response.status_code == 200


@pytest.mark.parametrize('name', ['index', 'communaute'])
def test_with_arguments(name):
    response = app.test_client().get(f'/{name}')
    assert response.status_code == 200


def test_404():
    response = app.test_client().get('/unknown')
    assert response.status_code == 404
