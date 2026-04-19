from django.urls import path
from rest_framework.routers import DefaultRouter
from lms.views import (
    CourseViewSet,
    LessonListAPIView,
    LessonCreateAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView
)


app_name = 'lms'
# Роутер для курсов (ViewSet)
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

# URL-паттерны для уроков (Generic классы)
urlpatterns = [
    # Уроки
    path('lessons/', LessonListAPIView.as_view(), name='lesson-list'),
    path('lessons/create/', LessonCreateAPIView.as_view(), name='lesson-create'),
    path('lessons/<int:pk>/', LessonRetrieveAPIView.as_view(), name='lesson-detail'),
    path('lessons/<int:pk>/update/', LessonUpdateAPIView.as_view(), name='lesson-update'),
    path('lessons/<int:pk>/delete/', LessonDestroyAPIView.as_view(), name='lesson-delete'),
]

# Добавляем URL от роутера
urlpatterns += router.urls
