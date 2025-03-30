from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet,
    CourseViewSet,
    CourseUnitViewSet,
    CourseMaterialViewSet,
    PastQuestionViewSet
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'courses', CourseViewSet, basename='course')

# Nested routers for course-related resources
courses_router = DefaultRouter()
courses_router.register(r'units', CourseUnitViewSet, basename='course-unit')
courses_router.register(r'materials', CourseMaterialViewSet, basename='course-material')
courses_router.register(r'past-questions', PastQuestionViewSet, basename='past-question')

urlpatterns = [
    path('', include(router.urls)),
    path('courses/<int:course_id>/', include(courses_router.urls)),
]