from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory

from test_factories import create_user
from user.permissions import (
    IsAdminRole,
    IsVerifiedUser,
    IsCompletedProfile,
    IsNotCompletedProfile,
    IsAdminOrReadOnly,
)


class PermissionTestCase(TestCase):
    """Base class wiring up a RequestFactory for building fake requests."""

    def setUp(self):
        self.factory = RequestFactory()

    def request(self, user, method="get"):
        req = getattr(self.factory, method)("/")
        req.user = user
        return req


class IsAdminRoleTests(PermissionTestCase):
    def test_admin_role_is_allowed(self):
        user = create_user(email="admin@example.com", role="admin")
        self.assertTrue(IsAdminRole().has_permission(self.request(user), None))

    def test_superuser_without_admin_role_is_allowed(self):
        user = create_user(email="root@example.com", role="user", is_superuser=True)
        self.assertTrue(IsAdminRole().has_permission(self.request(user), None))

    def test_regular_user_is_denied(self):
        user = create_user(email="plain@example.com", role="user")
        self.assertFalse(IsAdminRole().has_permission(self.request(user), None))

    def test_anonymous_user_is_denied(self):
        self.assertFalse(
            IsAdminRole().has_permission(self.request(AnonymousUser()), None)
        )


class IsVerifiedUserTests(PermissionTestCase):
    def test_active_regular_user_is_allowed(self):
        user = create_user(email="verified@example.com", role="user", is_active=True)
        self.assertTrue(IsVerifiedUser().has_permission(self.request(user), None))

    def test_inactive_user_is_denied(self):
        user = create_user(email="unverified@example.com", role="user", is_active=False)
        self.assertFalse(IsVerifiedUser().has_permission(self.request(user), None))

    def test_admin_role_is_denied(self):
        # IsVerifiedUser is scoped to the "user" role only.
        user = create_user(email="admin2@example.com", role="admin")
        self.assertFalse(IsVerifiedUser().has_permission(self.request(user), None))

    def test_anonymous_user_is_denied(self):
        self.assertFalse(
            IsVerifiedUser().has_permission(self.request(AnonymousUser()), None)
        )


class ProfileCompletionPermissionTests(PermissionTestCase):
    def test_is_completed_profile_true(self):
        user = create_user(email="done@example.com")
        user.is_profile_completed = True
        user.save(update_fields=["is_profile_completed"])
        self.assertTrue(IsCompletedProfile().has_permission(self.request(user), None))
        self.assertFalse(IsNotCompletedProfile().has_permission(self.request(user), None))

    def test_is_not_completed_profile_true(self):
        user = create_user(email="notdone@example.com")
        self.assertFalse(IsCompletedProfile().has_permission(self.request(user), None))
        self.assertTrue(IsNotCompletedProfile().has_permission(self.request(user), None))


class IsAdminOrReadOnlyTests(PermissionTestCase):
    def test_safe_method_allowed_for_verified_user(self):
        user = create_user(email="reader@example.com", role="user", is_active=True)
        self.assertTrue(
            IsAdminOrReadOnly().has_permission(self.request(user, "get"), None)
        )

    def test_safe_method_denied_for_unverified_user(self):
        user = create_user(email="reader2@example.com", role="user", is_active=False)
        self.assertFalse(
            IsAdminOrReadOnly().has_permission(self.request(user, "get"), None)
        )

    def test_write_method_requires_admin_role(self):
        admin = create_user(email="admin3@example.com", role="admin")
        regular = create_user(email="regular3@example.com", role="user")

        self.assertTrue(
            IsAdminOrReadOnly().has_permission(self.request(admin, "post"), None)
        )
        self.assertFalse(
            IsAdminOrReadOnly().has_permission(self.request(regular, "post"), None)
        )
