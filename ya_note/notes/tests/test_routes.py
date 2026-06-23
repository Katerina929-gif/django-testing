"""Тестирование маршрутизации и доступности страниц проекта."""

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тестирование маршрутизации и доступности страниц проекта."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка общих данных для тестирования маршрутов."""
        cls.author = User.objects.create_user(username='AuthorUser')
        cls.reader = User.objects.create_user(username='ReaderUser')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author
        )

    def test_pages_availability_for_anonymous_user(self):
        """Главная страница, страницы входа, регистрации и выхода.

        доступны анонимам.
        """
        urls = (
            'notes:home',
            'users:login',
            'users:signup',
            'users:logout',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                if name == 'users:logout':
                    response = self.client.post(url)
                else:
                    response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Авторизованному пользователю доступны страницы списков.

        и создания.
        """
        urls = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        self.client.force_login(self.reader)
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """Страницы заметки, удаления и редактирования.

        доступны только автору.
        """
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, expected_status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user.username, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous_user(self):
        """Анонимный пользователь перенаправляется на страницу логина.

        со всех закрытых страниц.
        """
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                expected_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
