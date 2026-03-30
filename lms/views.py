from rest_framework import generics
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import CanEditCourse, CanEditLesson


from rest_framework import viewsets


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD для курсов через ViewSet"""
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, CanEditCourse]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



class LessonListAPIView(generics.ListAPIView):
    """GET /lessons/ - получение списка всех уроков"""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, CanEditLesson]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonCreateAPIView(generics.CreateAPIView):
    """POST /lessons/create/ - создание нового урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, CanEditLesson]

    def perform_create(self, serializer):
        # Проверка, что курс принадлежит пользователю
        course_id = self.request.data.get('course')
        if course_id:
            course = Course.objects.get(id=course_id)
            if course.owner != self.request.user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('Нельзя создавать уроки в чужих курсах')

        serializer.save(owner=self.request.user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """GET /lessons/{id}/ - получение одного урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, CanEditLesson]


class LessonUpdateAPIView(generics.UpdateAPIView):
    """PUT /lessons/{id}/update/ - полное обновление урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, CanEditLesson]


class LessonDestroyAPIView(generics.DestroyAPIView):
    """DELETE /lessons/{id}/delete/ - удаление урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, CanEditLesson]
