from django.contrib import admin
from .models import (
    Note, NotePurchase, NoteBookmark,
    PastQuestion, Question, Answer,
    QuizAttempt, UserAnswer
)

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

class QuestionInline(admin.TabularInline):
    model = Question
    inlines = [AnswerInline]
    extra = 1

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'price', 'uploaded_by', 'download_count')
    list_filter = ('course', 'uploaded_by')
    search_fields = ('title', 'description')

@admin.register(PastQuestion)
class PastQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'exam_type', 'year', 'semester', 'format', 'price')
    list_filter = ('course', 'exam_type', 'year', 'semester', 'format')
    search_fields = ('title',)
    inlines = [QuestionInline]

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'past_question', 'score', 'started_at', 'completed_at')
    list_filter = ('past_question', 'user')
    readonly_fields = ('score',)

admin.site.register(NotePurchase)
admin.site.register(NoteBookmark)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(UserAnswer)