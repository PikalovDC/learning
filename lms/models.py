from django.db import models
from django.conf import settings


class Course(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='название'
    )
    preview = models.ImageField(
        upload_to='courses/',
        blank=True,
        null=True,
        verbose_name='превью'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='описание'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='дата последнего изменения'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← вместо 'users.User'
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='courses',
        verbose_name='Владелец'
    )

    class Meta:
        verbose_name = 'курс'
        verbose_name_plural = 'курсы'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Lesson(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name='курс',
        related_name='lessons'
    )

    name = models.CharField(
        max_length=200,
        verbose_name='название'
    )
    preview = models.ImageField(
        upload_to='courses/',
        blank=True,
        null=True,
        verbose_name='превью'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='описание'
    )

    video_link = models.URLField(
        blank=True,
        null=True,
        verbose_name='ссылка на видео'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='дата обновления'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← вместо 'users.User'
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='lessons',
        verbose_name='Владелец'
    )


    class Meta:
        verbose_name = 'урок'
        verbose_name_plural = 'уроки'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} (курс: {self.course.name})"
