from django.db import models
from rest_framework import serializers
from .models import Tutor, TutorReview, Tutorial, TutorialBooking
from courses.serializers import CourseSerializer
from users.serializers import UserSerializer

class TutorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    subjects = CourseSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Tutor
        fields = [
            'user', 'bio', 'qualifications', 'hourly_rate',
            'subjects', 'is_verified', 'average_rating',
            'created_at'
        ]

    def get_average_rating(self, obj):
        return obj.reviews.aggregate(models.Avg('rating'))['rating__avg']

class TutorRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutor
        fields = ['bio', 'qualifications', 'hourly_rate', 'subjects']

class TutorReviewSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)

    class Meta:
        model = TutorReview
        fields = ['id', 'student', 'rating', 'comment', 'created_at']

class TutorialSerializer(serializers.ModelSerializer):
    tutor = TutorSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    attendees_count = serializers.IntegerField(read_only=True)
    available_slots = serializers.IntegerField(read_only=True)
    is_booked = serializers.SerializerMethodField()

    class Meta:
        model = Tutorial
        fields = [
            'id', 'tutor', 'course', 'title', 'description',
            'start_time', 'end_time', 'max_students', 'price',
            'is_free', 'status', 'attendees_count', 'available_slots',
            'is_booked', 'created_at'
        ]

    def get_is_booked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookings.filter(student=request.user).exists()
        return False

class TutorialCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutorial
        fields = [
            'course', 'title', 'description', 'start_time',
            'end_time', 'max_students', 'price', 'is_free'
        ]

class TutorialBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorialBooking
        fields = ['id', 'tutorial', 'student', 'booked_at', 'attended']
        read_only_fields = ['student', 'booked_at']