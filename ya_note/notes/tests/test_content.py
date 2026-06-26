"""Тестирование структуры контента и передачи форм в шаблоны проекта."""

from notes.forms import NoteForm
from notes.tests.common import BaseTestCase, ADD_URL, LIST_URL


class TestContent(BaseTestCase):
    """Тестирование контента и отображения элементов на страницах."""

    def test_note_in_list_for_author(self):
        """Заметка передается автору в object_list и сохраняет свои поля."""
        self.client.force_login(self.author)
        response = self.client.get(LIST_URL)

        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']

        self.assertEqual(object_list.count(), 1)
        received_note = object_list.get()
        self.assertEqual(received_note, self.note)
        self.assertEqual(received_note.title, self.note.title)
        self.assertEqual(received_note.slug, self.note.slug)

    def test_note_not_in_list_for_another_user(self):
        """Заметка автора не видна другому зарегистрированному пользователю."""
        self.client.force_login(self.reader)
        response = self.client.get(LIST_URL)

        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_pages_contain_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        self.client.force_login(self.author)

        urls = (ADD_URL, self.edit_url)

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
