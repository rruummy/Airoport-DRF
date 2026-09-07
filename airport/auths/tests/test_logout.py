from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from test_factories import create_user


class LogoutViewTests(APITestCase):
    def setUp(self):
        self.user = create_user(email="logout@example.com", password="StrongPass123!")
        self.url = reverse("logout")

    def get_tokens(self):
        refresh = RefreshToken.for_user(self.user)
        return str(refresh), str(refresh.access_token)

    def test_logout_blacklists_the_refresh_token(self):
        refresh_str, access_str = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_str}")

        response = self.client.post(self.url, {"refresh": refresh_str})
        self.assertEqual(response.status_code, 205)

        # The same refresh token can no longer be used to get a new access token.
        refresh_response = self.client.post(
            reverse("token_refresh"), {"refresh": refresh_str}
        )
        self.assertEqual(refresh_response.status_code, 401)

    def test_logout_without_refresh_token_returns_400(self):
        _, access_str = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_str}")

        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)

    def test_logout_with_garbage_refresh_token_returns_400(self):
        _, access_str = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_str}")

        response = self.client.post(self.url, {"refresh": "not-a-real-token"})
        self.assertEqual(response.status_code, 400)

    def test_logout_requires_authentication(self):
        refresh_str, _ = self.get_tokens()

        response = self.client.post(self.url, {"refresh": refresh_str})
        self.assertEqual(response.status_code, 401)

    def test_double_logout_with_same_token_is_rejected(self):
        refresh_str, access_str = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_str}")

        first = self.client.post(self.url, {"refresh": refresh_str})
        second = self.client.post(self.url, {"refresh": refresh_str})

        self.assertEqual(first.status_code, 205)
        self.assertEqual(second.status_code, 400)
