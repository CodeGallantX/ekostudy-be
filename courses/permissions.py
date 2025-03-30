from rest_framework.permissions import BasePermission

class IsAdminOrReadOnly(BasePermission):
    """Allow admin users to edit, others to read"""
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_staff

class IsCourseLecturer(BasePermission):
    """Check if the user is a lecturer for the course"""
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
            
        course_id = view.kwargs.get('course_id') or view.kwargs.get('pk')
        if not course_id:
            return False
        
        course = view.get_queryset().first().course if hasattr(view, 'get_queryset') and view.get_queryset().exists() else None
        if course:
            return request.user in course.lecturers.all()
        
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
            
        if hasattr(obj, 'course'):
            return request.user in obj.course.lecturers.all()
        return False