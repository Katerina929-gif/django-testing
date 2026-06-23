"""Тестирование бизнес-логики создания, изменения и удаления заметок."""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteLogic(TestCase):
    """Тестирование базовой бизнес-логики создания заметок."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка общих данных для тестов создания заметок."""
        cls.author = User.objects.create_user(username='Author')
        cls.reader = User.objects.create_user(username='Reader')
        cls.form_data = {
            'title': 'Заголовок заметки',
            'text': 'Текст заметки',
            'slug': 'unique-slug'
        }

    def test_user_can_create_note_but_anonymous_cant(self):
        """Залогиненный пользователь может создать заметку.

        а анонимный — нет.
        """
        url = reverse('notes:add')

        self.client.post(url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 0)

        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.author, self.author)

    def test_cant_create_two_notes_with_same_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        url = reverse('notes:add')
        self.client.force_login(self.author)

        self.client.post(url, data=self.form_data)

        response = self.client.post(url, data=self.form_data)

        form = response.context['form']

        self.assertIn('slug', form.errors)

        expected_error = self.form_data['slug'] + WARNING
        self.assertIn(expected_error, form.errors['slug'])

        self.assertEqual(Note.objects.count(), 1)

    def test_automatic_slug_generation(self):
        """Если при создании заметки не заполнен slug.

        то он формируется автоматически.
        """
        url = reverse('notes:add')
        self.client.force_login(self.author)

        data_without_slug = {'title': 'Новая заметка', 'text': 'Текст'}
        self.client.post(url, data=data_without_slug)

        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        expected_slug = slugify(data_without_slug['title'])
        self.assertEqual(note.slug, expected_slug)


class TestNoteEditDeleteLogic(TestCase):
    """Тестирование логики редактирования и удаления заметок."""

    @classmethod
    def setUpTestData(cls):
        """Подготовка общих данных для тестов изменения и удаления."""
        cls.author = User.objects.create_user(username='Author')
        cls.reader = User.objects.create_user(username='Reader')
        cls.note = Note.objects.create(
            title='Оригинальный заголовок',
            text='Оригинальный текст',
            slug='note-slug',
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.new_form_data = {
            'title': 'Обновленный заголовок',
            'text': 'Обновленный текст',
            'slug': 'updated-slug'
        }

    def test_author_can_edit_and_delete_own_note(self):
        """Пользователь может редактировать и удалять свои заметки."""
        self.client.force_login(self.author)

        response = self.client.post(self.edit_url, data=self.new_form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.new_form_data['title'])

        current_delete_url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(current_delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_edit_and_delete_note_of_another_user(self):
        """Пользователь не может редактировать или удалять чужие заметки."""
        self.client.force_login(self.reader)

        response = self.client.post(self.edit_url, data=self.new_form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, self.new_form_data['title'])

        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
