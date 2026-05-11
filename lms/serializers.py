from rest_framework import serializers
from lms.models import Course, Lesson
from .validators import validate_youtube_url
from users.models import Subscription


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Lesson"""

    course_name = serializers.CharField(source='course.name', read_only=True)
    video_link = serializers.URLField(
        required=False,
        allow_blank=True,
        allow_null=True,
        validators=[validate_youtube_url]
    )

    class Meta:
        model = Lesson
        fields = ['id', 'course', 'course_name', 'name', 'description', 'preview',
                  'video_link', 'owner', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'owner']


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Course"""

    # Добавляем поле с количеством уроков в курсе
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'preview', 'description', 'lessons', 'lessons_count',
                  'owner', 'created_at', 'updated_at', 'is_subscribed',]
        read_only_fields = ['created_at', 'updated_at', 'owner']

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на курс"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False
