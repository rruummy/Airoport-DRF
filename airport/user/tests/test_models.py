from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from test_factories import create_user, create_profile


class UserModelTests(TestCase):
    def test_is_admin_role_true_for_admin_role(self):
        user = create_user(email="a@example.com", role="admin")
        self.assertTrue(user.is_admin_role)

    def test_is_admin_role_true_for_superuser(self):
        user = create_user(email="b@example.com", role="user", is_superuser=True)
        self.assertTrue(user.is_admin_role)

    def test_is_admin_role_false_for_plain_user(self):
        user = create_user(email="c@example.com", role="user")
        self.assertFalse(user.is_admin_role)

    def test_str_returns_username(self):
        user = create_user(email="d@example.com", username="d_user")
        self.assertEqual(str(user), "d_user")


class UserProfileModelTests(TestCase):
    def test_age_when_birthday_already_passed_this_year(self):
        today = date.today()
        birth_date = date(today.year - 30, today.month, today.day)
        user = create_user(email="age1@example.com")
        profile = create_profile(user, birth_date=birth_date)

        self.assertEqual(profile.age, 30)

    def test_age_when_birthday_has_not_happened_yet_this_year(self):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        birth_date = date(today.year - 30, tomorrow.month, tomorrow.day)
        user = create_user(email="age2@example.com")
        profile = create_profile(user, birth_date=birth_date)

        self.assertEqual(profile.age, 29)

    def test_negative_balance_is_invalid(self):
        user = create_user(email="balance@example.com")
        profile = create_profile(user)
        profile.balance = Decimal("-1.00")

        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_passport_number_must_be_unique(self):
        user1 = create_user(email="p1@example.com")
        user2 = create_user(email="p2@example.com")
        create_profile(user1, raw_passport="AB123456")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                create_profile(user2, raw_passport="AB123456")
