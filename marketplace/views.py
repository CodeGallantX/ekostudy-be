from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count
from django.http import FileResponse
from .models import (
    Note, NotePurchase, NoteBookmark,
    PastQuestion, QuizAttempt, UserAnswer
)
from .serializers import (
    NoteSerializer, NotePurchaseSerializer, NoteBookmarkSerializer,
    PastQuestionSerializer, QuizAttemptSerializer, UserAnswerSerializer
)
from courses.models import Course
import random

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def purchase(self, request, pk=None):
        note = self.get_object()
        user = request.user
        
        if note.purchases.filter(user=user).exists():
            return Response(
                {'detail': 'You have already purchased this note'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        purchase = NotePurchase.objects.create(
            note=note,
            user=user,
            price_paid=note.price
        )
        
        note.download_count += 1
        note.save()
        
        serializer = NotePurchaseSerializer(purchase)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def bookmark(self, request, pk=None):
        note = self.get_object()
        user = request.user
        
        if request.method == 'POST':
            bookmark, created = NoteBookmark.objects.get_or_create(
                note=note,
                user=user
            )
            if created:
                serializer = NoteBookmarkSerializer(bookmark)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                {'detail': 'Note already bookmarked'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        elif request.method == 'DELETE':
            bookmark = get_object_or_404(NoteBookmark, note=note, user=user)
            bookmark.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def download(self, request, pk=None):
        note = self.get_object()
        if not note.purchases.filter(user=request.user).exists():
            return Response(
                {'detail': 'You need to purchase this note first'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        response = FileResponse(note.file.open(), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{note.file.name}"'
        return response

class PastQuestionViewSet(viewsets.ModelViewSet):
    queryset = PastQuestion.objects.all()
    serializer_class = PastQuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def download(self, request, pk=None):
        past_question = self.get_object()
        if past_question.format != 'PDF':
            return Response(
                {'detail': 'This past question is not available as a PDF'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response = FileResponse(past_question.file.open(), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{past_question.file.name}"'
        return response

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start_quiz(self, request, pk=None):
        past_question = self.get_object()
        if past_question.format != 'INT':
            return Response(
                {'detail': 'This past question is not interactive'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        num_questions = request.data.get('num_questions', 10)
        duration = request.data.get('duration_minutes', 30)
        
        questions = past_question.questions.all()
        if num_questions < len(questions):
            questions = random.sample(list(questions), num_questions)
        
        attempt = QuizAttempt.objects.create(
            user=request.user,
            past_question=past_question,
            duration_minutes=duration
        )
        
        past_question.attempt_count += 1
        past_question.save()
        
        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class QuizAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit_answer(self, request, pk=None):
        attempt = self.get_object()
        if attempt.completed_at:
            return Response(
                {'detail': 'This quiz attempt is already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        question_id = request.data.get('question_id')
        answer_id = request.data.get('answer_id')
        
        question = get_object_or_404(attempt.past_question.questions, pk=question_id)
        answer = get_object_or_404(question.answers, pk=answer_id)
        
        user_answer, created = UserAnswer.objects.get_or_create(
            attempt=attempt,
            question=question,
            defaults={
                'selected_answer': answer,
                'is_correct': answer.is_correct
            }
        )
        
        if not created:
            user_answer.selected_answer = answer
            user_answer.is_correct = answer.is_correct
            user_answer.save()
        
        attempt.questions_attempted = attempt.user_answers.count()
        attempt.questions_correct = attempt.user_answers.filter(is_correct=True).count()
        attempt.save()
        
        return Response(
            {'is_correct': answer.is_correct, 'explanation': question.explanation},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        attempt = self.get_object()
        if attempt.completed_at:
            return Response(
                {'detail': 'This quiz attempt is already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attempt.completed_at = timezone.now()
        attempt.score = attempt.calculate_score()
        attempt.save()
        
        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data, status=status.HTTP_200_OK)