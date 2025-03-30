from rest_framework import serializers
from .models import (
    Department, Course, CourseOutline, 
    CourseMaterial, CourseUnit, PastQuestion
)
from users.base_serializers import UserSerializer  # Changed import

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'code', 'name', 'college', 'description']

class CourseSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    lecturers = UserSerializer(many=True, read_only=True)
    full_code = serializers.CharField(read_only=True)
    is_lecturer = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'full_code', 'title', 'code', 'description',
            'department', 'level', 'semester', 'credit_units',
            'course_type', 'is_active', 'created_at', 'lecturers',
            'is_lecturer'
        ]
        read_only_fields = ['created_at']

    def get_is_lecturer(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return request.user in obj.lecturers.all()
        return False

class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'title', 'code', 'description', 'department',
            'level', 'semester', 'credit_units', 'course_type',
            'lecturers'
        ]

class CourseOutlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseOutline
        fields = [
            'synopsis', 'objectives', 'topics',
            'references', 'grading_system'
        ]

class CourseMaterialSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = CourseMaterial
        fields = [
            'id', 'title', 'material_type', 'file', 'file_url',
            'description', 'uploaded_by', 'uploaded_at', 'is_approved'
        ]
        read_only_fields = ['uploaded_by', 'uploaded_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            return request.build_absolute_uri(obj.file.url)
        return None

class CourseUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseUnit
        fields = [
            'id', 'title', 'unit_type', 'description', 'duration_minutes',
            'order', 'content', 'video_url', 'attachment', 'is_published',
            'created_at'
        ]
        read_only_fields = ['created_at']

class PastQuestionSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = PastQuestion
        fields = [
            'id', 'title', 'exam_type', 'year', 'file', 'file_url',
            'description', 'uploaded_by', 'uploaded_at', 'is_approved'
        ]
        read_only_fields = ['uploaded_by', 'uploaded_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            return request.build_absolute_uri(obj.file.url)
        return None