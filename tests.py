import pytest

from afpy import application


def test_home():
    response = application.test_client().get("/")
    assert response.status_code == 200


@pytest.mark.parametrize("name", ["", "communaute"])
def test_html(name):
    response = application.test_client().get(f"/{name}")
    assert response.status_code == 200


@pytest.mark.parametrize("name", ["charte", "a-propos"])
def test_rest(name):
    response = application.test_client().get(f"/docs/{name}")
    assert response.status_code == 200


def test_planet():
    response = application.test_client().get("/planet/")
    assert response.status_code == 200


def test_404():
    response = application.test_client().get("/unknown")
    assert response.status_code == 404
    response = application.test_client().get("/docs/unknown")
    assert response.status_code == 404
    response = application.test_client().get("/feed/unknown")
    assert response.status_code == 404


def test_read_posts():
    response = application.test_client().get("/actualites/page/1")
    assert response.status_code == 200
    response = application.test_client().get("/emplois/page/1")
    assert response.status_code == 200
