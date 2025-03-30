from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Department, Course, CourseOutline,
    CourseMaterial, CourseUnit, PastQuestion
)
from .serializers import (
    DepartmentSerializer,
    CourseSerializer,
    CourseCreateUpdateSerializer,
    CourseOutlineSerializer,
    CourseMaterialSerializer,
    CourseUnitSerializer,
    PastQuestionSerializer
)
from .permissions import IsCourseLecturer, IsAdminOrReadOnly
from .filters import CourseFilter

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['college', 'code']

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend]
    filterset_class = CourseFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CourseCreateUpdateSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['get', 'put'])
    def outline(self, request, pk=None):
        course = self.get_object()
        
        if request.method == 'GET':
            outline = get_object_or_404(CourseOutline, course=course)
            serializer = CourseOutlineSerializer(outline)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            if not (request.user.is_staff or request.user in course.lecturers.all()):
                return Response(
                    {'detail': 'Only admins and course lecturers can update the outline'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            outline, created = CourseOutline.objects.get_or_create(course=course)
            serializer = CourseOutlineSerializer(outline, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def materials(self, request, pk=None):
        course = self.get_object()
        materials = course.materials.filter(is_approved=True)
        serializer = CourseMaterialSerializer(
            materials, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'])
    def past_questions(self, request, pk=None):
        course = self.get_object()
        
        if request.method == 'GET':
            questions = course.past_questions.filter(is_approved=True)
            serializer = PastQuestionSerializer(
                questions, 
                many=True,
                context={'request': request}
            )
            return Response(serializer.data)
        
        elif request.method == 'POST':
            if not request.user.is_authenticated:
                return Response(
                    {'detail': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            serializer = PastQuestionSerializer(
                data=request.data,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save(
                    course=course,
                    uploaded_by=request.user,
                    is_approved=request.user.is_staff
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseUnitViewSet(viewsets.ModelViewSet):
    serializer_class = CourseUnitSerializer
    permission_classes = [IsAuthenticated, IsCourseLecturer]

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return CourseUnit.objects.filter(course_id=course_id)

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

class CourseMaterialViewSet(viewsets.ModelViewSet):
    serializer_class = CourseMaterialSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return CourseMaterial.objects.all()
        return CourseMaterial.objects.filter(is_approved=True)

    def perform_create(self, serializer):
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        serializer.save(
            course=course,
            uploaded_by=self.request.user,
            is_approved=self.request.user.is_staff
        )

class PastQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = PastQuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return PastQuestion.objects.all()
        return PastQuestion.objects.filter(is_approved=True)

    def perform_create(self, serializer):
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        serializer.save(
            course=course,
            uploaded_by=self.request.user,
            is_approved=self.request.user.is_staff
        )