from django.urls import path, include
from rest_framework.routers import DefaultRouter
from flights.views import CountryViewSet

router = DefaultRouter()
router.register(r"country", CountryViewSet, basename="country")

urlpatterns = [
    path("", include(router.urls)),
]