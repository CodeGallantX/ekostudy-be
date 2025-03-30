from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from django.utils.timezone import now

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    college = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name}"

class Course(models.Model):
    SEMESTER_CHOICES = [
        ('1', 'First Semester'),
        ('2', 'Second Semester'),
        # ('3', 'Summer Semester'),
    ]
    
    LEVEL_CHOICES = [
        ('100', '100 Level'),
        ('200', '200 Level'),
        ('300', '300 Level'),
        ('400', '400 Level'),
        ('500', '500 Level'),
        ('600', '600 Level'),
    ]
    
    COURSE_TYPE_CHOICES = [
        ('COMPULSORY', 'Compulsory'),
        ('ELECTIVE', 'Elective'),
        ('GENERAL', 'General Studies'),
        ('REQUIRED', 'Required'),
    ]

    title = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='courses',
        default=1
    )
    level = models.CharField(max_length=3, choices=LEVEL_CHOICES, default='100')
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, default='1')
    credit_units = models.PositiveIntegerField(default=2)
    course_type = models.CharField(max_length=10, choices=COURSE_TYPE_CHOICES, default='Compulsory')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='is_prerequisite_for'
    )
    lecturers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='courses_taught',
        blank=True
    )

    class Meta:
        ordering = ['level', 'code']
        unique_together = ['code', 'department']

    def __str__(self):
        return f"{self.code}: {self.title}"

    @property
    def full_code(self):
        return f"{self.code}"

class CourseOutline(models.Model):
    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        related_name='outline'
    )
    synopsis = models.TextField(help_text="Brief course description")
    objectives = models.TextField(help_text="Course learning objectives")
    topics = models.JSONField(
        default=list,
        help_text="List of topics and subtopics in JSON format"
    )
    references = models.TextField(help_text="Recommended textbooks and references")
    grading_system = models.JSONField(
        default=dict,
        help_text="Grading breakdown in JSON format"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Outline for {self.course.title}"

class CourseMaterial(models.Model):
    MATERIAL_TYPES = [
        ('NOTE', 'Lecture Note'),
        ('SLIDE', 'Slide Presentation'),
        ('TEXT', 'Textbook'),
        ('VIDEO', 'Video Material'),
        ('OTHER', 'Other'),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='materials'
    )
    title = models.CharField(max_length=200, blank=True)
    material_type = models.CharField(max_length=5, choices=MATERIAL_TYPES)
    file = models.FileField(upload_to='course_materials/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.get_material_type_display()} for {self.course.code}"

class CourseUnit(models.Model):
    UNIT_TYPES = [
        ('LEC', 'Lecture'),
        ('TUT', 'Tutorial'),
        ('LAB', 'Laboratory'),
        ('ASG', 'Assignment'),
        ('PRJ', 'Project'),
        ('EXM', 'Exam'),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='units'
    )
    title = models.CharField(max_length=200, blank=True)
    unit_type = models.CharField(max_length=3, choices=UNIT_TYPES)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    order = models.PositiveIntegerField()
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    attachment = models.FileField(upload_to='unit_attachments/', blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.code} - {self.get_unit_type_display()}: {self.title}"

class PastQuestion(models.Model):
    EXAM_TYPES = [
        ('MID', 'Midterm Exam'),
        ('FIN', 'Final Exam'),
        ('QUZ', 'Quiz'),
        ('ASG', 'Assignment'),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='past_questions'
    )
    title = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=3, choices=EXAM_TYPES)
    year = models.PositiveIntegerField()
    file = models.FileField(upload_to='past_questions/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-year', 'exam_type']

    def __str__(self):
        return f"{self.course.code} - {self.get_exam_type_display()} ({self.year})"