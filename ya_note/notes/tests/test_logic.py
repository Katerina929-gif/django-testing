"""Тестирование бизнес-логики создания, изменения и удаления заметок."""

from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.common import ADD_URL, BaseTestCase, SUCCESS_URL


class TestNoteLogic(BaseTestCase):
    """Тестирование логики создания заметок и валидации слагов."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестирования создания заметок."""
        super().setUpTestData()
        cls.form_data = {
            'title': 'Заголовок заметки',
            'text': 'Текст заметки',
            'slug': 'unique-slug'
        }

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count_before = Note.objects.count()

        self.client.post(ADD_URL, data=self.form_data)

        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count_after)

    def test_authorized_user_can_create_note(self):
        """Авторизованный пользователь может успешно создать заметку."""
        self.client.force_login(self.author)
        notes_count_before = Note.objects.count()

        response = self.client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)

        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)

        note = Note.objects.last()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_cant_create_two_notes_with_same_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.client.force_login(self.author)
        notes_count_before = Note.objects.count()

        self.form_data['slug'] = self.note.slug
        response = self.client.post(ADD_URL, data=self.form_data)

        self.assertIn('form', response.context)
        form = response.context['form']

        self.assertIn('slug', form.errors)

        expected_error = self.form_data['slug'] + WARNING
        self.assertIn(expected_error, form.errors['slug'])

        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count_after)

    def test_automatic_slug_generation(self):
        """Автоматическое формирование.

        slug из поля title при его отсутствии.
        """
        self.client.force_login(self.author)
        notes_count_before = Note.objects.count()

        data_without_slug = {'title': 'Новая заметка', 'text': 'Текст'}
        self.client.post(ADD_URL, data_without_slug)

        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)

        note = Note.objects.last()
        expected_slug = slugify(data_without_slug['title'])
        self.assertEqual(note.slug, expected_slug)


class TestNoteEditDeleteLogic(BaseTestCase):
    """Тестирование логики изменения и удаления заметок автором и чужаком."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестов изменения и удаления."""
        super().setUpTestData()
        cls.new_form_data = {
            'title': 'Обновленный заголовок',
            'text': 'Обновленный текст',
            'slug': 'updated-slug'
        }

    def test_author_can_edit_own_note(self):
        """Автор может успешно отредактировать все поля своей заметки."""
        self.client.force_login(self.author)

        response = self.client.post(self.edit_url, data=self.new_form_data)
        self.assertRedirects(response, SUCCESS_URL)

        updated_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(updated_note.title, self.new_form_data['title'])
        self.assertEqual(updated_note.text, self.new_form_data['text'])
        self.assertEqual(updated_note.slug, self.new_form_data['slug'])
        self.assertEqual(updated_note.author, self.note.author)

    def test_author_can_delete_own_note(self):
        """Автор может успешно удалить свою заметку."""
        self.client.force_login(self.author)

        response = self.client.post(self.delete_url)
        self.assertRedirects(response, SUCCESS_URL)

        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может отредактировать чужую заметку (404)."""
        self.client.force_login(self.reader)

        response = self.client.post(self.edit_url, data=self.new_form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        not_updated_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(not_updated_note.title, self.note.title)
        self.assertEqual(not_updated_note.text, self.note.text)
        self.assertEqual(not_updated_note.slug, self.note.slug)
        self.assertEqual(not_updated_note.author, self.note.author)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить чужую заметку (404)."""
        self.client.force_login(self.reader)

        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
