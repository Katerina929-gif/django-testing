"""Тестирование бизнес-логики комментариев и модерации текста."""

from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, detail_url, form_data):
    """Анонимный гость не имеет прав создавать новые комментарии."""
    client.post(detail_url, data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(
    not_author_client, not_author, news, detail_url, form_data, url_to_comments
):
    """Авторизованный пользователь может успешно опубликовать отзыв."""
    response = not_author_client.post(detail_url, data=form_data)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 1

    comment_obj = Comment.objects.get()
    assert comment_obj.text == form_data['text']
    assert comment_obj.news == news
    assert comment_obj.author == not_author


@pytest.mark.django_db
def test_user_cant_use_bad_words(not_author_client, detail_url):
    """Если текст содержит стоп-слова, форма вернет ошибку.

    запись не создастся.
    """
    bad_words_data = {'text': f'Текст, {BAD_WORDS[0]}, текст'}
    response = not_author_client.post(detail_url, data=bad_words_data)

    form = response.context['form']
    assert 'text' in form.errors
    assert WARNING in form.errors['text']
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment, url_to_comments):
    """Автор без проблем удаляет свой собственный комментарий."""
    delete_url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    """Попытка удалить чужой отзыв пресекается статус-кодом 404."""
    delete_url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, comment, form_data, url_to_comments
):
    """Автор может отредактировать содержание своего комментария."""
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)

    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment, form_data
):
    """Чужой пользователь не может изменить текст комментария (ошибка 404)."""
    edit_url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND

    comment.refresh_from_db()
    assert comment.text != form_data['text']
