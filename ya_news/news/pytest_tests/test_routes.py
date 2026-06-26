"""Тестирование доступности маршрутов и редиректов."""

from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_fixture, is_logout',
    (
        (lf('home_url'), False),
        (lf('detail_url'), False),
        (lf('login_url'), False),
        (lf('signup_url'), False),
        (lf('logout_url'), True),
    ),
)
def test_pages_availability_for_anonymous_user(client, url_fixture, is_logout):
    """Базовые страницы доступны анонимным пользователям."""
    if is_logout:
        response = client.post(url_fixture)
    else:
        response = client.get(url_fixture)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'url_fixture',
    (lf('edit_comment_url'), lf('delete_comment_url')),
)
def test_pages_availability_for_different_users(
    parametrized_client, url_fixture, expected_status
):
    """Автор имеет доступ к изменению/удалению комментария, чужой — нет."""
    response = parametrized_client.get(url_fixture)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture',
    (lf('edit_comment_url'), lf('delete_comment_url')),
)
def test_redirects_for_anonymous_user(client, login_url, url_fixture):
    """При попытке править или удалить отзыв.

    аноним отправляется на авторизацию.
    """
    expected_url = f'{login_url}?next={url_fixture}'
    response = client.get(url_fixture)
    assertRedirects(response, expected_url)
