from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from user.views import RegisterView, root_redirect_view

urlpatterns = [
    path("", root_redirect_view, name="root-redirect"),
    path('admin/', admin.site.urls),

    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/register/", RegisterView.as_view(), name="register" ),
    path("auth/token-refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('auth/', include('rest_framework.urls')),

    path("user/", include("user.urls")),
    path("", include("flights.urls")),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
