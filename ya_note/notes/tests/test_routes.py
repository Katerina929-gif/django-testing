"""Тестирование маршрутизации и доступности страниц проекта."""

from http import HTTPStatus

from notes.tests.common import (
    ADD_URL,
    BaseTestCase,
    HOME_URL,
    LIST_URL,
    LOGIN_URL,
    LOGOUT_URL,
    SIGNUP_URL,
    SUCCESS_URL,
)


class TestRoutes(BaseTestCase):
    """Тестирование маршрутизации и доступности страниц проекта."""

    def test_pages_availability_for_anonymous_user(self):
        """Главная страница, вход, регистрация и выход доступны анонимам."""
        urls = (HOME_URL, LOGIN_URL, SIGNUP_URL, LOGOUT_URL)
        for url in urls:
            with self.subTest(url=url):
                if url == LOGOUT_URL:
                    response = self.client.post(url)
                else:
                    response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Авторизованному пользователю доступны страницы.

        списков и создания.
        """
        self.client.force_login(self.reader)
        urls = (LIST_URL, ADD_URL, SUCCESS_URL)
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """Страницы заметки, удаления и редактирования.

        доступны только автору.
        """
        urls = (self.detail_url, self.edit_url, self.delete_url)
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, expected_status in users_statuses:
            self.client.force_login(user)
            for url in urls:
                with self.subTest(user=user.username, url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous_user(self):
        """Анонимный пользователь перенаправляется на страницу логина."""
        urls = (
            LIST_URL,
            ADD_URL,
            SUCCESS_URL,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                expected_url = f'{LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
