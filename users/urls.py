from django.urls import path
from .views import (
    UserCreateView,
    MyProfileView,
    AvatarUploadView,
    PublicProfileView,
    DeleteAccountView
)

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('me/', MyProfileView.as_view(), name='my-profile'),
    path('me/avatar/', AvatarUploadView.as_view(), name='avatar-upload'),
    path('<int:user__id>/', PublicProfileView.as_view(), name='public-profile'),
    path('me/delete/', DeleteAccountView.as_view(), name='delete-account'),
]