"""Тестирование доступности маршрутов и редиректов."""

from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_lazyfixture import lazy_fixture as lf
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', lf('news_pk_for_args')),
        ('users:login', None),
        ('users:signup', None),
        ('users:logout', None),
    ),
)
def test_pages_availability_for_anonymous_user(client, name, args):
    """Главная, новость, вход, выход и регистрация доступны анонимам."""
    url = reverse(name, args=args)
    if name == 'users:logout':
        response = client.post(url)
    else:
        response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
    parametrized_client, name, comment, expected_status
):
    """Автор имеет доступ к изменению/удалению своего комментария.

    чужой — нет.
    """
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lf('comment_id_for_args')),
        ('news:delete', lf('comment_id_for_args')),
    ),
)
def test_redirects_for_anonymous_user(client, name, args):
    """При попытке править или удалить отзыв.

    аноним отправляется на авторизацию.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
