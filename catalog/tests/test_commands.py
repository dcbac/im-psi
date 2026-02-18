from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

class CreateSuperuserCommandTest(TestCase):

    def test_creates_superuser_if_not_exists(self):
        self.assertFalse(User.objects.filter(username="alumnodb").exists())

        call_command("createsu")

        self.assertTrue(User.objects.filter(username="alumnodb").exists())

        user = User.objects.get(username="alumnodb")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_does_not_duplicate_if_exists(self):
        User.objects.create_superuser(
            username="alumnodb",
            password="alumnodb"
        )

        call_command("createsu")

        self.assertEqual(
            User.objects.filter(username="alumnodb").count(),
            1
        )
