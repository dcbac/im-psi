import uuid
import datetime

from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from catalog.models import Author, BookInstance, Book, Genre, Language
from unittest.mock import patch

class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        number_of_authors = 13

        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f"Dominique {author_id}",
                last_name=f"Surname {author_id}",
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/catalog/authors/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("authors"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("authors"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/author_list.html")

    def test_pagination_is_ten(self):
        response = self.client.get(reverse("authors"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertEqual(len(response.context["author_list"]), 4)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse("authors") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertEqual(len(response.context["author_list"]), 4)


User = get_user_model()


class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(
            username="testuser1", password="1X<ISRUkw+tuK"
        )
        test_user2 = User.objects.create_user(
            username="testuser2", password="2HJ1vRV0Z&3iD"
        )

        test_user1.save()
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(
            first_name="Dominique", last_name="Rousseau"
        )
        test_genre = Genre.objects.create(name="Fantasy")
        test_language = Language.objects.create(name="English")
        test_book = Book.objects.create(
            title="Book Title",
            summary="My book summary",
            isbn="ABCDEFG",
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(
            genre_objects_for_book
        )  # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy % 5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = "m"
            BookInstance.objects.create(
                book=test_book,
                imprint="Unlikely Imprint, 2016",
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("my-borrowed"))
        self.assertRedirects(response, "/accounts/login/?next=/catalog/mybooks/")

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("my-borrowed"))

        # Check our user is logged in
        self.assertEqual(str(response.context["user"]), "testuser1")
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(
            response, "catalog/bookinstance_list_borrowed_user.html"
        )

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("my-borrowed"))

        # Check our user is logged in
        self.assertEqual(str(response.context["user"]), "testuser1")
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue("bookinstance_list" in response.context)
        self.assertEqual(len(response.context["bookinstance_list"]), 0)

        # Now change all books to be on loan
        books = BookInstance.objects.all()[:10]

        for book in books:
            book.status = "o"
            book.save()

        # Check that now we have borrowed books in the list
        response = self.client.get(reverse("my-borrowed"))
        # Check our user is logged in
        self.assertEqual(str(response.context["user"]), "testuser1")
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        self.assertTrue("bookinstance_list" in response.context)

        # Confirm all books belong to testuser1 and are on loan
        for book_item in response.context["bookinstance_list"]:
            self.assertEqual(response.context["user"], book_item.borrower)
            self.assertEqual(book_item.status, "o")

    def test_pages_ordered_by_due_date(self):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status = "o"
            book.save()

        login = self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("my-borrowed"))

        # Check our user is logged in
        self.assertEqual(str(response.context["user"]), "testuser1")
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Confirm that of the items, only 4 are displayed due to pagination.
        self.assertEqual(len(response.context["bookinstance_list"]), 4)

        last_date = 0
        for book in response.context["bookinstance_list"]:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back


class RenewBookInstancesViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(
            username="testuser1", password="1X<ISRUkw+tuK"
        )
        test_user2 = User.objects.create_user(
            username="testuser2", password="2HJ1vRV0Z&3iD"
        )

        test_user1.save()
        test_user2.save()

        # Give test_user2 permission to renew books.
        permission = Permission.objects.get(name="Set book as returned")
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(
            first_name="Dominique", last_name="Rousseau"
        )
        test_genre = Genre.objects.create(name="Fantasy")
        test_language = Language.objects.create(name="English")
        test_book = Book.objects.create(
            title="Book Title",
            summary="My book summary",
            isbn="ABCDEFG",
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(
            genre_objects_for_book
        )  # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create a BookInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint="Unlikely Imprint, 2016",
            due_back=return_date,
            borrower=test_user1,
            status="o",
        )

        # Create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint="Unlikely Imprint, 2016",
            due_back=return_date,
            borrower=test_user2,
            status="o",
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance1.pk})
        )
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance1.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance2.pk})
        )

        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance1.pk})
        )

        # Check that it lets us login. We're a librarian, so we can view any users book
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        # unlikely UID to match our bookinstance!
        test_uid = uuid.uuid4()
        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": test_uid})
        )
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance1.pk})
        )
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, "catalog/book_renew_librarian.html")

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance1.pk})
        )
        self.assertEqual(response.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(
            response.context["form"].initial["due_back"], date_3_weeks_in_future
        )

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(
            reverse(
                "renew-book-librarian",
                kwargs={
                    "pk": self.test_bookinstance1.pk,
                },
            ),
            {"due_back": valid_date_in_future},
        )
        self.assertRedirects(response, reverse("all-borrowed"))

    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        response = self.client.post(
            reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance1.pk}),
            {"due_back": date_in_past},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "due_back", "Invalid date - renewal in past"
        )

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        response = self.client.post(
            reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance1.pk}),
            {"due_back": invalid_date_in_future},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "due_back",
            "Invalid date - renewal more than 4 weeks ahead",
        )


class AuthorCreateViewTest(TestCase):
    """Test case for the AuthorCreate view (Created as Challenge)."""

    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(
            username="testuser1", password="some_password1"
        )
        test_user2 = User.objects.create_user(
            username="testuser2", password="some_password2"
        )

        permAddAuthor = Permission.objects.get(name="Can add author")
        test_user1.user_permissions.add(permAddAuthor)
        test_user1.save()

        test_user2.save()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("author-create"))
        self.assertRedirects(response, "/accounts/login/?next=/catalog/author/create/")

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username="testuser2", password="some_password2")
        self.assertTrue(login)

        valid_first_name = "Some"
        valid_last_name = "One"
        valid_date_of_birth = datetime.date.today() + datetime.timedelta(weeks=-100)
        valid_date_of_death = datetime.date.today() + datetime.timedelta(weeks=100)
        response = self.client.post(
            reverse(
                "author-create",
            ),
            {
                "first_name": valid_first_name,
                "last_name": valid_last_name,
                "date_of_birth": valid_date_of_birth,
                "date_of_death": valid_date_of_death,
            },
        )

        self.assertTrue(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username="testuser1", password="some_password1")
        self.assertTrue(login)

        valid_first_name = "Some"
        valid_last_name = "One"
        valid_date_of_birth = datetime.date.today() + datetime.timedelta(weeks=-100)
        valid_date_of_death = datetime.date.today() + datetime.timedelta(weeks=100)
        response = self.client.post(
            reverse(
                "author-create",
            ),
            {
                "first_name": valid_first_name,
                "last_name": valid_last_name,
                "date_of_birth": valid_date_of_birth,
                "date_of_death": valid_date_of_death,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/catalog/author/"))

    def test_uses_correct_template(self):
        login = self.client.login(username="testuser1", password="some_password1")
        self.assertTrue(login)

        response = self.client.get(
            reverse(
                "author-create",
            ),
        )

        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/author_form.html")

    def test_form_date_of_death_initially_set_to_expected_date(self):
        login = self.client.login(username="testuser1", password="some_password1")
        self.assertTrue(login)

        response = self.client.get(reverse("author-create"))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["form"].initial["date_of_death"],
            "11/11/2023",
        )

    def test_redirects_to_detail_view_on_success(self):
        login = self.client.login(username="testuser1", password="some_password1")
        self.assertTrue(login)

        valid_first_name = "Some"
        valid_last_name = "One"
        valid_date_of_birth = datetime.date.today() + datetime.timedelta(weeks=-100)
        valid_date_of_death = datetime.date.today() + datetime.timedelta(weeks=100)
        response = self.client.post(
            reverse(
                "author-create",
            ),
            {
                "first_name": valid_first_name,
                "last_name": valid_last_name,
                "date_of_birth": valid_date_of_birth,
                "date_of_death": valid_date_of_death,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/catalog/author/"))

class AuthorDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        permission = Permission.objects.get(codename='delete_author')
        self.user.user_permissions.add(permission)
        self.user.save()

        self.author = Author.objects.create(
            first_name='John',
            last_name='Doe'
        )

    def test_author_delete_success(self):
        self.client.login(username='testuser', password='12345')

        response = self.client.post(
            reverse('author-delete', args=[self.author.pk])
        )

        self.assertRedirects(response, reverse('authors'))
        self.assertFalse(Author.objects.filter(pk=self.author.pk).exists())

class BookDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        permission = Permission.objects.get(codename='delete_book')
        self.user.user_permissions.add(permission)
        self.user.save()

        self.author = Author.objects.create(first_name='Jane', last_name='Doe')

        self.book = Book.objects.create(
            title='Test Book',
            author=self.author,
            summary='Test summary',
            isbn='1234567890123'
        )

    def test_book_delete_success(self):
        self.client.login(username='testuser', password='12345')

        response = self.client.post(
            reverse('book-delete', args=[self.book.pk])
        )

        # Comprueba redirección correcta
        self.assertRedirects(response, reverse('books'))

        # Comprueba que el libro fue eliminado
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())

class AuthorDeleteExceptionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        permission = Permission.objects.get(codename='delete_author')
        self.user.user_permissions.add(permission)
        self.user.save()

        self.author = Author.objects.create(
            first_name='John',
            last_name='Doe'
        )

    @patch("catalog.models.Author.delete")
    def test_author_delete_exception_redirects_back(self, mock_delete):
        # Forzamos excepción
        mock_delete.side_effect = Exception("Delete failed")

        self.client.login(username='testuser', password='12345')

        response = self.client.post(
            reverse('author-delete', args=[self.author.pk])
        )

        self.assertRedirects(
            response,
            reverse('author-delete', args=[self.author.pk])
        )

        self.assertTrue(Author.objects.filter(pk=self.author.pk).exists())

class BookDeleteExceptionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        permission = Permission.objects.get(codename='delete_book')
        self.user.user_permissions.add(permission)
        self.user.save()

        self.author = Author.objects.create(first_name='Jane', last_name='Doe')

        self.book = Book.objects.create(
            title='Test Book',
            author=self.author,
            summary='Test summary',
            isbn='1234567890123'
        )

    @patch("catalog.models.Book.delete")
    def test_book_delete_exception_redirects_back(self, mock_delete):
        # Forzamos excepción
        mock_delete.side_effect = Exception("Delete failed")

        self.client.login(username='testuser', password='12345')

        response = self.client.post(
            reverse('book-delete', args=[self.book.pk])
        )

        self.assertRedirects(
            response,
            reverse('book-delete', args=[self.book.pk])
        )

        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())
