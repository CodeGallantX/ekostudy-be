from django.db import models
from django.contrib.auth import get_user_model
from courses.models import Course
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Note(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notes')
    description = models.TextField()
    file = models.FileField(upload_to='marketplace/notes/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    average_rating = models.FloatField(default=0)
    download_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} - {self.course.code}"

class NotePurchase(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='purchases')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_notes')
    purchased_at = models.DateTimeField(auto_now_add=True)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('note', 'user')

class NoteBookmark(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='bookmarks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarked_notes')
    bookmarked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('note', 'user')

class PastQuestion(models.Model):
    EXAM_TYPES = [
        ('MID', 'Midterm Exam'),
        ('FIN', 'Final Exam'),
        ('QUZ', 'Quiz'),
        ('ASG', 'Assignment'),
    ]

    FORMAT_CHOICES = [
        ('PDF', 'PDF Document'),
        ('INT', 'Interactive Quiz'),
    ]

    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='marketplace_past_questions')
    exam_type = models.CharField(max_length=3, choices=EXAM_TYPES)
    year = models.PositiveIntegerField()
    semester = models.CharField(max_length=1, choices=Course.SEMESTER_CHOICES)
    format = models.CharField(max_length=3, choices=FORMAT_CHOICES)
    file = models.FileField(upload_to='marketplace/past_questions/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_past_questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    average_rating = models.FloatField(default=0)
    attempt_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.course.code} - {self.get_exam_type_display()} ({self.year})"

class Question(models.Model):
    past_question = models.ForeignKey(PastQuestion, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    past_question = models.ForeignKey(PastQuestion, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField()
    questions_attempted = models.PositiveIntegerField(default=0)
    questions_correct = models.PositiveIntegerField(default=0)

    def calculate_score(self):
        if self.questions_attempted > 0:
            return (self.questions_correct / self.questions_attempted) * 100
        return 0

class UserAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)