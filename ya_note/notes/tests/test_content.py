"""Тестирование контента и передачи форм в шаблоны проекта."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    """Тестирование контента и отображения элементов на страницах."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка общих данных для тестов контента."""
        cls.author = User.objects.create_user(username='Author')
        cls.reader = User.objects.create_user(username='Reader')
        cls.note = Note.objects.create(
            title='Заметка автора',
            text='Текст',
            slug='author-slug',
            author=cls.author
        )

    def test_note_in_list_for_author_and_not_for_another_user(self):
        """Заметка передается автору в object_list.

        и не видна другому пользователю.
        """
        url = reverse('notes:list')
        users_results = (
            (self.author, True),
            (self.reader, False),
        )
        for user, should_be_in_list in users_results:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), should_be_in_list)

    def test_pages_contain_form(self):
        """На страницы создания и редактирования заметки.

        передаются формы NoteForm.
        """
        self.client.force_login(self.author)
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
