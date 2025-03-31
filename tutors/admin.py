from django.contrib import admin
from .models import Tutor, TutorReview, Tutorial, TutorialBooking

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'hourly_rate')
    list_filter = ('is_verified',)
    search_fields = ('user__first_name', 'user__last_name', 'user__email')

@admin.register(TutorReview)
class TutorReviewAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'student', 'rating', 'created_at')
    list_filter = ('rating',)

@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_display = ('title', 'tutor', 'course', 'start_time', 'end_time', 'is_free', 'status')
    list_filter = ('status', 'is_free', 'course')
    search_fields = ('title', 'tutor__user__first_name', 'tutor__user__last_name')

@admin.register(TutorialBooking)
class TutorialBookingAdmin(admin.ModelAdmin):
    list_display = ('tutorial', 'student', 'booked_at', 'attended')
    list_filter = ('attended',)