from django.contrib import admin
from .models import Course, Department, CourseMaterial, CourseOutline, CourseUnit, PastQuestion

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'level', 'semester', 'credit_units', 'course_type')
    search_fields = ('title', 'code', 'department', 'level', 'semester', 'credit_units', 'course_type', 'prerequisites')
    # raw_id_fields = ('code',)

@admin.register(CourseUnit)
class CourseUnitAdmin(admin.ModelAdmin):
    list_display = ('unit_type', 'duration_minutes', 'is_published', 'content')
    list_filter = ('unit_type', 'duration_minutes',)
    search_fields = ('attachment', 'content', 'description')

@admin.register(CourseOutline)
class CourseOutlineAdmin(admin.ModelAdmin):
    list_display = ('course', 'synopsis',)
    list_filter = ('references',)
    search_fields = ('objectives', 'topics')


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('material_type', 'file')
    list_filter = ('material_type', 'file', 'description',)
    search_fields = ('material_type', 'description')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'college')
    list_filter = ('name', 'college',)
    search_fields = ('name', 'college', 'code')


@admin.register(PastQuestion)
class PastQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'exam_type', 'year', 'file')
    list_filter = ('exam_type', 'year')
    search_fields = ('title', 'exam_type', 'year', 'file', 'description')