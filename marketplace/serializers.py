from rest_framework import serializers
from .models import (
    Note, NotePurchase, NoteBookmark,
    PastQuestion, Question, Answer,
    QuizAttempt, UserAnswer
)
from courses.serializers import CourseSerializer
from users.serializers import UserSerializer

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'explanation', 'answers']

class PastQuestionSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    uploaded_by = UserSerializer(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PastQuestion
        fields = [
            'id', 'title', 'course', 'exam_type', 'year', 'semester',
            'format', 'file', 'file_url', 'price', 'uploaded_by',
            'created_at', 'updated_at', 'average_rating', 'attempt_count',
            'questions'
        ]
        read_only_fields = ['uploaded_by', 'created_at', 'updated_at', 'attempt_count']

    def get_file_url(self, obj):
        if obj.file and hasattr(obj.file, 'url'):
            request = self.context.get('request')
            return request.build_absolute_uri(obj.file.url)
        return None

class NoteSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    is_purchased = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'course', 'description', 'file', 'file_url',
            'price', 'uploaded_by', 'created_at', 'updated_at',
            'average_rating', 'download_count', 'is_purchased', 'is_bookmarked'
        ]
        read_only_fields = [
            'uploaded_by', 'created_at', 'updated_at',
            'average_rating', 'download_count'
        ]

    def get_file_url(self, obj):
        if obj.file and hasattr(obj.file, 'url'):
            request = self.context.get('request')
            return request.build_absolute_uri(obj.file.url)
        return None

    def get_is_purchased(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.purchases.filter(user=request.user).exists()
        return False

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarks.filter(user=request.user).exists()
        return False

class NotePurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotePurchase
        fields = ['id', 'note', 'user', 'purchased_at', 'price_paid']
        read_only_fields = ['user', 'purchased_at', 'price_paid']

class NoteBookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteBookmark
        fields = ['id', 'note', 'user', 'bookmarked_at']
        read_only_fields = ['user', 'bookmarked_at']

class QuizAttemptSerializer(serializers.ModelSerializer):
    past_question = PastQuestionSerializer(read_only=True)
    score_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'past_question', 'started_at', 'completed_at',
            'score', 'duration_minutes', 'questions_attempted',
            'questions_correct', 'score_percentage'
        ]
        read_only_fields = ['user', 'started_at', 'completed_at', 'score']

    def get_score_percentage(self, obj):
        if obj.score is not None:
            return round(obj.score, 2)
        return None

class UserAnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    selected_answer = AnswerSerializer(read_only=True)
    
    class Meta:
        model = UserAnswer
        fields = [
            'id', 'question', 'selected_answer',
            'is_correct', 'answered_at'
        ]