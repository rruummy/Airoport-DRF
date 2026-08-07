from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from auths.views import (
    RegisterView, LoginView,
    GoogleAuthUrlView, GoogleCallbackView, GoogleLoginView,
    VerifyEmailView, ResendVerificationView,
    ForgotPasswordView, ResetPasswordView,
    )

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),

    path("login/", LoginView.as_view(), name="login"),
    path("token-refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("login-with-google/get-url/", GoogleAuthUrlView.as_view(), name="google_login_url"),
    path("login-with-google/get-token/", GoogleCallbackView.as_view(), name="google_get_token"),
    path("login-with-google/", GoogleLoginView.as_view(), name="google_login"),

    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("resend-verification/", ResendVerificationView.as_view(), name="resend_verification"),

    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
]