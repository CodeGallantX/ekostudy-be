from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from .models import Tutor, TutorReview, Tutorial, TutorialBooking
from .serializers import (
    TutorSerializer, TutorRegisterSerializer, TutorReviewSerializer,
    TutorialSerializer, TutorialCreateSerializer, TutorialBookingSerializer
)
from .permissions import IsTutor

class TutorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tutor.objects.filter(is_verified=True)
    serializer_class = TutorSerializer

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request):
        if hasattr(request.user, 'tutor_profile'):
            return Response(
                {'detail': 'You are already registered as a tutor'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TutorRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tutor = serializer.save(user=request.user)
        return Response(
            TutorSerializer(tutor, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        tutor = self.get_object()
        reviews = tutor.reviews.all()
        serializer = TutorReviewSerializer(reviews, many=True)
        return Response(serializer.data)

class TutorialViewSet(viewsets.ModelViewSet):
    serializer_class = TutorialSerializer

    def get_queryset(self):
        queryset = Tutorial.objects.all()
        if self.action == 'upcoming':
            queryset = queryset.filter(
                status='UPCOMING',
                start_time__gt=timezone.now()
            )
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return TutorialCreateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTutor()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(tutor=self.request.user.tutor_profile)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def book(self, request, pk=None):
        tutorial = self.get_object()

        if tutorial.bookings.filter(student=request.user).exists():
            return Response(
                {'detail': 'You have already booked this tutorial'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if tutorial.available_slots <= 0:
            return Response(
                {'detail': 'No available slots for this tutorial'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking = TutorialBooking.objects.create(
            tutorial=tutorial,
            student=request.user
        )
        serializer = TutorialBookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)