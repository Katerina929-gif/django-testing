"""Фикстуры для тестирования проекта YaNews."""

from datetime import datetime, timedelta

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import pytest

from news.models import Comment, News


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Автоматически открывает доступ к базе данных для всех тестов."""
    pass


@pytest.fixture
def news():
    """Создает тестовую новость."""
    return News.objects.create(title='Заголовок', text='Текст новости')


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
    """Возвращает клиент, авторизованный под автором комментария."""
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author, client):
    """Возвращает клиент, авторизованный под чужим пользователем."""
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
def news_list():
    """Создает пачку новостей, превышающую лимит главной страницы."""
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comments_list(news, author):
    """Создает 10 комментариев с хронологическим сдвигом во времени."""
    now = timezone.now()
    comments = []
    for index in range(10):
        comment_obj = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment_obj.created = now + timedelta(days=index)
        comment_obj.save()
        comments.append(comment_obj)
    return comments


@pytest.fixture
def detail_url(news):
    """Возвращает прямую ссылку на страницу новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def url_to_comments(detail_url):
    """Ссылка на блок комментариев страницы новости."""
    return detail_url + '#comments'


@pytest.fixture
def home_url():
    """Ссылка на главную страницу."""
    return reverse('news:home')


@pytest.fixture
def login_url():
    """Ссылка на страницу входа."""
    return reverse('users:login')


@pytest.fixture
def signup_url():
    """Ссылка на страницу регистрации."""
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    """Ссылка на страницу выхода."""
    return reverse('users:logout')


@pytest.fixture
def edit_comment_url(comment):
    """Ссылка на редактирование комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_comment_url(comment):
    """Ссылка на удаление комментария."""
    return reverse('news:delete', args=(comment.id,))
