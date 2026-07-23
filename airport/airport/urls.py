from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from flights.views import FlightViewSet, AirportViewSet, AirlineViewSet, AirplaneSerializerViewSet, CountryViewSet
from tickets.views import TicketViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'tickets', TicketViewSet)
router.register(r'flights', FlightViewSet)
router.register(r'airlines', AirlineViewSet)
router.register(r'airplanes', AirplaneSerializerViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'airports', AirportViewSet)

urlpatterns = [
    path("api/users/", include("user.urls")),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('admin/', admin.site.urls),
    path('api/auth/', include('rest_framework.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
