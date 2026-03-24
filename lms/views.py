from rest_framework import generics
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


from rest_framework import viewsets


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD для курсов через ViewSet"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer



class LessonListAPIView(generics.ListAPIView):
    """GET /lessons/ - получение списка всех уроков"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonCreateAPIView(generics.CreateAPIView):
    """POST /lessons/create/ - создание нового урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """GET /lessons/{id}/ - получение одного урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonUpdateAPIView(generics.UpdateAPIView):
    """PUT /lessons/{id}/update/ - полное обновление урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonDestroyAPIView(generics.DestroyAPIView):
    """DELETE /lessons/{id}/delete/ - удаление урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer