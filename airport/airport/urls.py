from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
    )

from user.views import root_redirect_view

urlpatterns = [
    path("", root_redirect_view, name="root-redirect"),

    path("admin/", admin.site.urls),

    path("auth/", include("auths.urls")),
    path("auth/", include("rest_framework.urls")),

    path("user/", include("user.urls")),
    path("payment/", include("payment.urls")),
    path("", include("flights.urls")),
    path("", include("tickets.urls")),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]