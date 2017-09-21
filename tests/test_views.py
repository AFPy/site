from functools import partial

import pytest
from flask import url_for

import afpy


@pytest.fixture(autouse=True)
def app():
    return afpy.app


class TestPagesView:
    get_test_url = partial(url_for, 'pages')

    def test_no_arguments(self, client):
        response = client.get(self.get_test_url())

        assert response.status_code == 200

    @pytest.mark.parametrize(
        'template_name',
        [
            'a-propos',
            'feed',
            'rst',
        ]
    )
    def test_with_arguments(self, client, template_name):
        response = client.get(self.get_test_url(template_name=template_name))

        assert response.status_code == 200

    def test_404(self, client):
        response = client.get(self.get_test_url(template_name="bad_template_name_my_friend"))

        assert response.status_code == 404
