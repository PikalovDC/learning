from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Lesson"""

    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'course', 'course_name', 'name', 'description', 'preview',
                  'video_link', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Course"""

    # Добавляем поле с количеством уроков в курсе
    lessons_count = serializers.SerializerMethodField()

    lessons = LessonSerializer(many=True, read_only=True, source='lessons')

    class Meta:
        model = Course
        fields = ['id', 'name', 'preview', 'description', 'lessons_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_lessons_count(self, obj):
        return obj.lessons.count()
