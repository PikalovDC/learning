from rest_framework import generics, status
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .permissions import (
    IsModerator,
    IsOwner,
    CanCreateCourse,
    CanCreateLesson,
    CanEditCourse,
    CanEditLesson,
    CanDeleteCourse,
    CanDeleteLesson,
)
from rest_framework import viewsets


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD для курсов через ViewSet"""
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def get_permissions(self):
        """Динамическое назначение прав в зависимости от действия"""
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, CanCreateCourse]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, CanEditCourse]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, CanDeleteCourse]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



class LessonListAPIView(generics.ListAPIView):
    """GET /lessons/ - получение списка всех уроков"""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonCreateAPIView(generics.CreateAPIView):
    """POST /lessons/create/ - создание нового урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, CanCreateLesson]

    def perform_create(self, serializer):
        # Проверка, что курс принадлежит пользователю
        course_id = self.request.data.get('course')
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                if course.owner != self.request.user:
                    raise PermissionDenied('Нельзя создавать уроки в чужих курсах')
            except Course.DoesNotExist:
                raise PermissionDenied('Курс не найден')

            serializer.save(owner=self.request.user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """GET /lessons/{id}/ - получение одного урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Фильтрация: пользователи видят только свои уроки, модераторы - все"""
        user = self.request.user
        if user.groups.filter(name='Moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    """PUT /lessons/{id}/update/ - полное обновление урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, CanEditLesson]

    def get_queryset(self):
        """Фильтрация для безопасности"""
        user = self.request.user
        if user.groups.filter(name='Moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonDestroyAPIView(generics.DestroyAPIView):
    """DELETE /lessons/{id}/delete/ - удаление урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, CanDeleteLesson]

    def get_queryset(self):
        """Фильтрация для безопасности"""
        user = self.request.user
        if user.groups.filter(name='Moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)
