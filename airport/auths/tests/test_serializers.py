import hashlib
from datetime import date, timedelta

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.utils import timezone

from test_factories import create_user, create_profile
from auths.serializers import RegisterSerializer, LoginSerializer, VerifyEmailSerializer
from emails.models import EmailVerificationCode
from user.models import User


class RegisterSerializerTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def context(self):
        request = self.factory.post("/auth/register/")
        request.user = AnonymousUser()
        return {"request": request}

    def valid_payload(self, **overrides):
        payload = {
            "username": "newpilot",
            "email": "newpilot@example.com",
            "password": "SuperSecret123!",
            "first_name": "Anna",
            "last_name": "Nova",
            "passport_number": "AB123456",
            "birth_date": "1995-05-20",
            "bio": "",
        }
        payload.update(overrides)
        return payload

    def test_valid_registration_creates_inactive_user_with_profile(self):
        serializer = RegisterSerializer(data=self.valid_payload(), context=self.context())
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        self.assertFalse(user.is_active)
        self.assertTrue(user.check_password("SuperSecret123!"))
        self.assertEqual(user.profile.first_name, "Anna")
        self.assertEqual(user.profile.last_name, "Nova")
        # The raw passport number must never be stored as-is.
        self.assertNotEqual(user.profile.passport_number, "AB123456")

    def test_duplicate_email_is_rejected(self):
        create_user(email="newpilot@example.com")
        serializer = RegisterSerializer(data=self.valid_payload(), context=self.context())
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_first_name_with_digits_is_rejected(self):
        serializer = RegisterSerializer(
            data=self.valid_payload(first_name="Anna1"), context=self.context()
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("first_name", serializer.errors)

    def test_identical_first_and_last_name_is_rejected(self):
        serializer = RegisterSerializer(
            data=self.valid_payload(first_name="Anna", last_name="Anna"),
            context=self.context(),
        )
        self.assertFalse(serializer.is_valid())

    def test_future_birth_date_is_rejected(self):
        future = (date.today() + timedelta(days=1)).isoformat()
        serializer = RegisterSerializer(
            data=self.valid_payload(birth_date=future), context=self.context()
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("birth_date", serializer.errors)

    def test_invalid_passport_format_is_rejected(self):
        serializer = RegisterSerializer(
            data=self.valid_payload(passport_number="!!!"), context=self.context()
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("passport_number", serializer.errors)

    def test_duplicate_passport_number_is_rejected(self):
        existing_user = create_user(email="owner@example.com")
        create_profile(existing_user, raw_passport="AB123456")

        serializer = RegisterSerializer(
            data=self.valid_payload(email="other@example.com"),
            context=self.context(),
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("passport_number", serializer.errors)


class LoginSerializerTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = create_user(email="login2@example.com", password="StrongPass123!")

    def context(self):
        request = self.factory.post("/auth/login/")
        return {"request": request}

    def test_valid_login_returns_tokens(self):
        serializer = LoginSerializer(
            data={"email": "login2@example.com", "password": "StrongPass123!"},
            context=self.context(),
        )
        serializer.is_valid(raise_exception=True)
        self.assertIn("access", serializer.validated_data)
        self.assertIn("refresh", serializer.validated_data)

    def test_wrong_password_is_rejected(self):
        serializer = LoginSerializer(
            data={"email": "login2@example.com", "password": "wrong"},
            context=self.context(),
        )
        self.assertFalse(serializer.is_valid())

    def test_unverified_user_is_rejected(self):
        create_user(email="unverified2@example.com", password="StrongPass123!", is_active=False)
        serializer = LoginSerializer(
            data={"email": "unverified2@example.com", "password": "StrongPass123!"},
            context=self.context(),
        )
        self.assertFalse(serializer.is_valid())


class VerifyEmailSerializerTests(TestCase):
    def setUp(self):
        self.user = create_user(email="toverify@example.com", is_active=False)

    def make_code(self, code="123456", expires_in=timedelta(minutes=10)):
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        return EmailVerificationCode.objects.create(
            user=self.user,
            code_hash=code_hash,
            expires_at=timezone.now() + expires_in,
        )

    def test_correct_code_verifies_successfully(self):
        self.make_code("123456")
        serializer = VerifyEmailSerializer(
            data={"email": self.user.email, "code": "123456"}
        )
        serializer.is_valid(raise_exception=True)
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_wrong_code_is_rejected(self):
        self.make_code("123456")
        serializer = VerifyEmailSerializer(
            data={"email": self.user.email, "code": "000000"}
        )
        self.assertFalse(serializer.is_valid())

    def test_expired_code_is_rejected(self):
        self.make_code("123456", expires_in=timedelta(minutes=-1))
        serializer = VerifyEmailSerializer(
            data={"email": self.user.email, "code": "123456"}
        )
        self.assertFalse(serializer.is_valid())

    def test_already_active_user_is_rejected(self):
        self.user.is_active = True
        self.user.save(update_fields=["is_active"])
        self.make_code("123456")
        serializer = VerifyEmailSerializer(
            data={"email": self.user.email, "code": "123456"}
        )
        self.assertFalse(serializer.is_valid())
