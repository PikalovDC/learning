from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = 'Создает группу модераторов и назначает права'

    def handle(self, *args, **options):
        # Создаем группу модераторов
        moderator_group, created = Group.objects.get_or_create(name='Moderators')

        if created:
            self.stdout.write(self.style.SUCCESS('Группа Moderators создана'))
        else:
            self.stdout.write(self.style.WARNING('Группа Moderators уже существует'))

        # Получаем content types для моделей
        course_content_type = ContentType.objects.get_for_model(Course)
        lesson_content_type = ContentType.objects.get_for_model(Lesson)

        # Права для курсов (только просмотр и изменение, без создания и удаления)
        course_permissions = [
            Permission.objects.get(codename='view_course', content_type=course_content_type),
            Permission.objects.get(codename='change_course', content_type=course_content_type),
        ]

        # Права для уроков (только просмотр и изменение, без создания и удаления)
        lesson_permissions = [
            Permission.objects.get(codename='view_lesson', content_type=lesson_content_type),
            Permission.objects.get(codename='change_lesson', content_type=lesson_content_type),
        ]

        # Добавляем права группе
        all_permissions = course_permissions + lesson_permissions
        moderator_group.permissions.set(all_permissions)

        self.stdout.write(self.style.SUCCESS(f'Группе назначено {len(all_permissions)} прав'))
        self.stdout.write(self.style.SUCCESS('Права: просмотр и изменение курсов и уроков'))