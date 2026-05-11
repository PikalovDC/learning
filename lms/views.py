from rest_framework import generics, status
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .permissions import (
    CanCreateCourse,
    CanCreateLesson,
    CanEditCourse,
    CanEditLesson,
    CanDeleteCourse,
    CanDeleteLesson,
)
from rest_framework import viewsets
from .paginators import CoursePaginator, LessonPaginator
from users.tasks import send_course_update_email
from rest_framework.response import Response


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD для курсов через ViewSet"""
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CoursePaginator

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def get_serializer_context(self):
        """Передаем request в контекст для доступа к пользователю"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

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

    def update(self, request, *args, **kwargs):
        """Обновление курса с отправкой уведомлений подписчикам"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Сохраняем старое название для сравнения
        old_name = instance.name
        old_description = instance.description

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Формируем описание изменений
        changes = []
        if old_name != instance.name:
            changes.append(f"Название изменено с '{old_name}' на '{instance.name}'")
        if old_description != instance.description:
            changes.append("Описание курса обновлено")

        # Если есть изменения, отправляем уведомления подписчикам
        if changes:
            changes_description = "\n".join(changes)
            # Асинхронный вызов задачи
            send_course_update_email.delay(
                course_id=instance.id,
                course_name=instance.name,
                changes_description=changes_description
            )

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление курса"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class LessonListAPIView(generics.ListAPIView):
    """GET /lessons/ - получение списка всех уроков"""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LessonPaginator

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
