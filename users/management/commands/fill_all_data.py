from django.core.management.base import BaseCommand
from users.models import User, Payment
from lms.models import Course, Lesson
from datetime import datetime
from django.utils.timezone import make_aware


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **options):
        # Создаем курсы
        course1, _ = Course.objects.get_or_create(
            id=1,
            defaults={'name': 'Python для начинающих', 'description': 'Базовый курс Python'}
        )
        course2, _ = Course.objects.get_or_create(
            id=2,
            defaults={'name': 'Django Framework', 'description': 'Изучаем Django'}
        )

        # Создаем уроки
        Lesson.objects.get_or_create(
            id=1,
            defaults={'course': course1, 'name': 'Введение в Python', 'description': 'Установка и настройка'}
        )
        Lesson.objects.get_or_create(
            id=2,
            defaults={'course': course2, 'name': 'Введение в Django', 'description': 'Создание первого проекта'}
        )

        # Создаем пользователей
        user1, _ = User.objects.get_or_create(
            id=1,
            defaults={'email': 'user1@example.com', 'username': 'user1'}
        )
        user1.set_password('123456')
        user1.save()

        user2, _ = User.objects.get_or_create(
            id=2,
            defaults={'email': 'user2@example.com', 'username': 'user2'}
        )
        user2.set_password('123456')
        user2.save()

        # Создаем платежи
        Payment.objects.get_or_create(
            id=1,
            defaults={
                'user': user1,
                'payment_date': make_aware(datetime(2024, 1, 15, 10, 30)),
                'paid_course': course1,
                'paid_lesson': None,
                'amount': 5000.00,
                'payment_method': 'transfer'
            }
        )

        Payment.objects.get_or_create(
            id=2,
            defaults={
                'user': user1,
                'payment_date': make_aware(datetime(2024, 2, 20, 14, 45)),
                'paid_course': None,
                'paid_lesson': Lesson.objects.get(id=1),
                'amount': 1500.00,
                'payment_method': 'cash'
            }
        )

        Payment.objects.get_or_create(
            id=3,
            defaults={
                'user': user2,
                'payment_date': make_aware(datetime(2024, 3, 10, 9, 15)),
                'paid_course': course2,
                'paid_lesson': None,
                'amount': 7500.00,
                'payment_method': 'transfer'
            }
        )

        self.stdout.write(self.style.SUCCESS('Все данные успешно созданы!'))
