from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()

class Tutor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='tutor_profile'
    )
    bio = models.TextField()
    qualifications = models.TextField()
    hourly_rate = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        null=True,
        blank=True
    )
    subjects = models.ManyToManyField('courses.Course', related_name='tutors')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - Tutor"

class TutorReview(models.Model):
    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tutor_reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tutor', 'student')

class Tutorial(models.Model):
    STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name='tutorials'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='tutorials'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_students = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        null=True,
        blank=True
    )
    is_free = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='UPCOMING'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def attendees_count(self):
        return self.bookings.count()

    @property
    def available_slots(self):
        return self.max_students - self.attendees_count

    def __str__(self):
        return f"{self.title} by {self.tutor.user.get_full_name()}"

class TutorialBooking(models.Model):
    tutorial = models.ForeignKey(
        Tutorial,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tutorial_bookings'
    )
    booked_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ('tutorial', 'student')