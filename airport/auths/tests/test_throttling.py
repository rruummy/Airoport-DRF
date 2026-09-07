from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.throttling import ScopedRateThrottle

from test_factories import create_user


@patch.object(ScopedRateThrottle, "THROTTLE_RATES", {"auth": "3/min"})
class AuthThrottlingTests(APITestCase):
    """Patches ScopedRateThrottle.THROTTLE_RATES directly (rather than
    override_settings(REST_FRAMEWORK=...)) because DRF's throttle classes
    read api_settings.DEFAULT_THROTTLE_RATES into a class attribute once at
    import time - overriding the Django setting alone doesn't reliably
    change already-imported throttle classes.
    """

    def setUp(self):
        cache.clear()
        self.user = create_user(email="throttled@example.com", password="StrongPass123!")
        self.url = reverse("login")

    def login_attempt(self, ip="127.0.0.1"):
        return self.client.post(
            self.url,
            {"email": "throttled@example.com", "password": "wrong-password"},
            REMOTE_ADDR=ip,
        )

    def test_requests_within_the_limit_are_not_throttled(self):
        for _ in range(3):
            response = self.login_attempt()
            self.assertNotEqual(response.status_code, 429)

    def test_requests_beyond_the_limit_are_throttled(self):
        for _ in range(3):
            self.login_attempt()

        response = self.login_attempt()
        self.assertEqual(response.status_code, 429)

    def test_throttling_is_scoped_per_client_ip(self):
        for _ in range(3):
            self.login_attempt(ip="127.0.0.1")

        throttled = self.login_attempt(ip="127.0.0.1")
        self.assertEqual(throttled.status_code, 429)

        # A different client IP gets its own quota.
        response = self.login_attempt(ip="10.0.0.99")
        self.assertNotEqual(response.status_code, 429)
