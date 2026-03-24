from rest_framework import serializers
from .models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Course"""

    # Добавляем поле с количеством уроков в курсе
    lessons_count = serializers.IntegerField(source='lessons.count', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'preview', 'description', 'lessons_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Lesson"""

    # Для удобства отображаем название курса
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'course', 'course_name', 'name', 'description', 'preview',
                  'video_link', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']