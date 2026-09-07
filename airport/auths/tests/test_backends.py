from django.contrib.auth import authenticate
from django.test import TestCase

from test_factories import create_user


class EmailBackendTests(TestCase):
    def setUp(self):
        self.user = create_user(email="login@example.com", password="StrongPass123!")

    def test_authenticate_with_correct_email_and_password(self):
        user = authenticate(username="login@example.com", password="StrongPass123!")
        self.assertEqual(user, self.user)

    def test_authenticate_with_wrong_password_fails(self):
        user = authenticate(username="login@example.com", password="wrong-password")
        self.assertIsNone(user)

    def test_authenticate_with_unknown_email_fails(self):
        user = authenticate(username="nobody@example.com", password="whatever")
        self.assertIsNone(user)

    def test_inactive_user_cannot_authenticate(self):
        create_user(email="inactive@example.com", password="StrongPass123!", is_active=False)
        user = authenticate(username="inactive@example.com", password="StrongPass123!")
        self.assertIsNone(user)
