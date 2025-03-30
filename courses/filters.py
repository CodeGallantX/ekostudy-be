import django_filters
from .models import Course

class CourseFilter(django_filters.FilterSet):
    level = django_filters.CharFilter(field_name='level')
    semester = django_filters.CharFilter(field_name='semester')
    department = django_filters.CharFilter(field_name='department__code')
    course_type = django_filters.CharFilter(field_name='course_type')
    lecturer = django_filters.CharFilter(
        field_name='lecturers__id',
        lookup_expr='exact'
    )
    search = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains'
    )

    class Meta:
        model = Course
        fields = ['level', 'semester', 'department', 'course_type', 'lecturer', 'search']