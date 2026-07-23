from django.urls import path
from user.views import RegisterView, UserProfileGetView, UserProfileUpdateView

urlpatterns = [
    path("profile/", UserProfileGetView.as_view(), name="profile"),
    path("profile/update", UserProfileUpdateView.as_view(), name="profile"),
]