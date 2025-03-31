from rest_framework.permissions import BasePermission

class IsTutor(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'tutor_profile')