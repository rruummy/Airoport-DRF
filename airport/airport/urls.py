from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from user.views import root_redirect_view
from auths.views import VerifyEmailView, ResendVerificationView, RegisterView, GoogleLoginView, GoogleAuthUrlView, GoogleCallbackView

urlpatterns = [
    path("", root_redirect_view, name="root-redirect"),
    path('admin/', admin.site.urls),

    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/login-with-google/get-url", GoogleAuthUrlView.as_view(), name="google_login_url"),
    path("auth/login-with-google/get-token", GoogleCallbackView.as_view(), name="google_get_token"),
    path("auth/login-with-google/", GoogleLoginView.as_view(), name="google_login"),
    path("auth/register/", RegisterView.as_view(), name="register" ),
    path("auth/token-refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("auth/resend-verification/", ResendVerificationView.as_view()),
    path('auth/', include('rest_framework.urls')),

    path("user/", include("user.urls")),
    path("", include("payment.urls")),
    path("", include("flights.urls")),
    path("", include("tickets.urls")),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
