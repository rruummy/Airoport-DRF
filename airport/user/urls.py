from django.urls import path
from user.views import UserProfileGetView, UserProfileUpdateView, ChangePasswordView

urlpatterns = [
    path("profile/", UserProfileGetView.as_view(), name="profile-get"),
    path("profile/update/", UserProfileUpdateView.as_view(), name="profile-update"),
    path("profile/change-password/", ChangePasswordView.as_view(), name="change-password"),
]