"""Фикстуры для тестирования проекта YaNews."""

from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def news(db):
    """Создает тестовую новость."""
    _ = db
    return News.objects.create(title='Заголовок', text='Текст новости')


@pytest.fixture
def news_pk_for_args(news):
    """Возвращает ID новости для передачи аргументом в reverse()."""
    return (news.pk,)


@pytest.fixture
def author(django_user_model):
    """Пользователь-автор комментария."""
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def not_author(django_user_model):
    """Сторонний зарегистрированный пользователь."""
    return django_user_model.objects.create(username='Чужой пользователь')


@pytest.fixture
def author_client(author, client):
    """Клиент, авторизованный под автором комментария."""
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author, client):
    """Клиент, авторизованный под сторонним пользователем."""
    client.force_login(not_author)
    return client


@pytest.fixture
def comment(author, news):
    """Создает тестовый комментарий к новости."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def comment_id_for_args(comment):
    """Возвращает ID комментария для передачи в reverse()."""
    return (comment.id,)


@pytest.fixture
def news_list(db):
    """Создает пачку новостей, превышающую лимит главной страницы."""
    _ = db
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comments_list(news, author):
    """Создает 10 комментариев с хронологическим сдвигом во времени."""
    now = timezone.now()
    comments = []
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments.append(comment)
    return comments


@pytest.fixture
def detail_url(news):
    """Возвращает прямую ссылку на страницу новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def form_data():
    """Валидные данные формы комментария."""
    return {'text': 'Новый текст комментария'}


@pytest.fixture
def url_to_comments(detail_url):
    """Ссылка на блок комментариев страницы новости."""
    return detail_url + '#comments'
