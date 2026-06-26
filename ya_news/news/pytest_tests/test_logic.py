"""Тестирование бизнес-логики комментариев и модерации текста."""

from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

COMMENT_FORM_DATA = {'text': 'Новый текст комментария'}


def test_anonymous_user_cant_create_comment(client, detail_url):
    """Анонимный гость не имеет прав создавать новые комментарии."""
    comments_count_before = Comment.objects.count()

    client.post(detail_url, data=COMMENT_FORM_DATA)

    comments_count_after = Comment.objects.count()
    assert comments_count_before == comments_count_after


def test_user_can_create_comment(
    not_author_client, not_author, detail_url, url_to_comments
):
    """Авторизованный пользователь может успешно опубликовать отзыв."""
    comments_count_before = Comment.objects.count()

    response = not_author_client.post(detail_url, data=COMMENT_FORM_DATA)
    assertRedirects(response, url_to_comments)

    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before + 1

    comment_obj = Comment.objects.get()
    assert comment_obj.text == COMMENT_FORM_DATA['text']
    assert comment_obj.author == not_author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(not_author_client, detail_url, bad_word):
    """Форма возвращает ошибку.

    если комментарий содержит любое из стоп-слов.
    """
    comments_count_before = Comment.objects.count()

    bad_words_data = {
        'text': f'Какое-то предложение, {bad_word}, продолжение текста.'
    }
    response = not_author_client.post(detail_url, data=bad_words_data)

    assert 'form' in response.context
    form = response.context['form']

    assert 'text' in form.errors
    assert WARNING in form.errors['text']

    comments_count_after = Comment.objects.count()
    assert comments_count_before == comments_count_after


def test_author_can_delete_comment(
    author_client, delete_comment_url, comment, url_to_comments
):
    """Автор без проблем удаляет свой собственный комментарий."""
    response = author_client.delete(delete_comment_url)
    assertRedirects(response, url_to_comments)

    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_user_cant_delete_comment_of_another_user(
    not_author_client, delete_comment_url, comment
):
    """Попытка удалить чужой отзыв пресекается ошибкой 404."""
    original_text = comment.text
    original_author = comment.author
    original_news = comment.news

    response = not_author_client.delete(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND

    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == original_text
    assert updated_comment.author == original_author
    assert updated_comment.news == original_news


def test_author_can_edit_comment(
    author_client, edit_comment_url, comment, url_to_comments
):
    """Автор может отредактировать содержание своего комментария."""
    original_author = comment.author
    original_news = comment.news

    response = author_client.post(edit_comment_url, data=COMMENT_FORM_DATA)
    assertRedirects(response, url_to_comments)

    updated_comment = Comment.objects.get(pk=comment.pk)

    assert updated_comment.text == COMMENT_FORM_DATA['text']
    assert updated_comment.author == original_author
    assert updated_comment.news == original_news


def test_user_cant_edit_comment_of_another_user(
    not_author_client, edit_comment_url, comment
):
    """Чужой пользователь не может изменить текст комментария (ошибка 404)."""
    original_text = comment.text
    original_author = comment.author
    original_news = comment.news

    response = not_author_client.post(edit_comment_url, data=COMMENT_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND

    updated_comment = Comment.objects.get(pk=comment.pk)

    assert updated_comment.text == original_text
    assert updated_comment.author == original_author
    assert updated_comment.news == original_news
