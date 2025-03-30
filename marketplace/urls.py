from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, PastQuestionViewSet, QuizAttemptViewSet

router = DefaultRouter()
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'past-questions', PastQuestionViewSet, basename='past-question')
router.register(r'quiz-attempts', QuizAttemptViewSet, basename='quiz-attempt')

urlpatterns = [
    path('marketplace/', include(router.urls)),
]