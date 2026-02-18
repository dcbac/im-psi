from django.test import TestCase
from django.urls import reverse

from catalog.models import Author, Genre, Book, Language, BookInstance

class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        author = Author.objects.create(first_name="Big", last_name="Bob")
        cls.author_id = author.id

    def test_first_name_label(self):
        author = Author.objects.get(id=self.author_id)
        field_label = author._meta.get_field("first_name").verbose_name
        self.assertEqual(field_label, "first name")

    def test_date_of_death_label(self):
        author = Author.objects.get(id=self.author_id)
        field_label = author._meta.get_field("date_of_death").verbose_name
        self.assertEqual(field_label, "died")

    def test_first_name_max_length(self):
        author = Author.objects.get(id=self.author_id)
        max_length = author._meta.get_field("first_name").max_length
        self.assertEqual(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=self.author_id)
        expected_object_name = f"{author.last_name}, {author.first_name}"
        self.assertEqual(str(author), expected_object_name)

    def test_get_absolute_url(self):
        author = Author.objects.get(id=self.author_id)
        self.assertEqual(author.get_absolute_url(), f"/catalog/author/{self.author_id}")

class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(first_name='John', last_name='Doe')
        language = Language.objects.create(name='English')
        cls.book = Book.objects.create(
            title='Test Book',
            author=author,
            summary='A test book summary',
            isbn='1234567890123',
            language=language
        )

    def test_get_absolute_url(self):
        expected_url = reverse('book-detail', args=[str(self.book.id)])
        self.assertEqual(self.book.get_absolute_url(), expected_url)


class BookInstanceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(first_name='Jane', last_name='Smith')
        language = Language.objects.create(name='Spanish')
        book = Book.objects.create(
            title='Another Test Book',
            author=author,
            summary='Another test summary',
            isbn='9876543210987',
            language=language
        )
        cls.book_instance = BookInstance.objects.create(
            book=book,
            imprint='Test Imprint 2024',
            status='a'
        )

    def test_str_representation(self):
        expected_string = f"{self.book_instance.id} ({self.book_instance.book.title})"
        self.assertEqual(str(self.book_instance), expected_string)
        self.assertIn(str(self.book_instance.id), str(self.book_instance))
        self.assertIn(self.book_instance.book.title, str(self.book_instance))

    def test_display_id(self):
        expected_id_string = str(self.book_instance.id)
        self.assertEqual(self.book_instance.display_id(), expected_id_string)
        self.assertIsInstance(self.book_instance.display_id(), str)
