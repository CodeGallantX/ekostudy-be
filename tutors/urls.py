from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TutorViewSet, TutorialViewSet

router = DefaultRouter()
router.register(r'tutors', TutorViewSet, basename='tutor')
router.register(r'tutorials', TutorialViewSet, basename='tutorial')

urlpatterns = [
    path('', include(router.urls)),
]