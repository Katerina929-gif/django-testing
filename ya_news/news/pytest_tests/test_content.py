"""Тестирование структуры контента, сортировки и форм."""

from typing import List

import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm
from news.models import Comment, News


@pytest.mark.django_db
def test_news_count(client, news_list: List[News]):
    """Количество новостей на главной не превышает установленного лимита."""
    _ = news_list
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_list: List[News]):
    """Новости на главной странице отсортированы от свежих к старым."""
    _ = news_list
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(
    client, detail_url: str, comments_list: List[Comment]
):
    """Комментарии внутри новости отсортированы хронологически."""
    _ = comments_list
    response = client.get(detail_url)
    assert 'news' in response.context
    news_object = response.context['news']
    all_comments = news_object.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, detail_url: str):
    """Аноним не видит форму для отправки комментария."""
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, detail_url: str):
    """Авторизованный пользователь видит форму нужного типа."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
