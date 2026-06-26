"""Общие компоненты, базовые классы и константы для тестов проекта YaNote."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

HOME_URL = reverse('notes:home')
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
LOGIN_URL = reverse('users:login')
SIGNUP_URL = reverse('users:signup')
LOGOUT_URL = reverse('users:logout')


class BaseTestCase(TestCase):
    """Базовый класс тестов.

    подготавливающий пользователей, клиентов и заметку.
    """

    @classmethod
    def setUpTestData(cls):
        """Создание общих объектов для всех тестов-наследников."""
        cls.author = User.objects.create_user(username='Author')
        cls.reader = User.objects.create_user(username='Reader')

        cls.note = Note.objects.create(
            title='Заметка автора',
            text='Текст заметки',
            slug='author-slug',
            author=cls.author
        )

        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
