from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import Group
from users.models import User, Subscription
from lms.models import Course, Lesson


class LessonAndSubscriptionTests(TestCase):
    """
    Тесты для проверки CRUD уроков и функционала подписки
    """

    def setUp(self):
        """
        Подготовка тестовых данных перед каждым тестом
        """
        # Создаем клиент для API запросов
        self.client = APIClient()

        # Создаем группы
        self.moderator_group, _ = Group.objects.get_or_create(name='Moderators')

        # Создаем пользователей
        self.owner_user = User.objects.create_user(
            email='owner@test.ru',
            username='owner',
            password='testpass123',
            first_name='Владелец',
            last_name='Тестовый'
        )

        self.other_user = User.objects.create_user(
            email='other@test.ru',
            username='other',
            password='testpass123',
            first_name='Другой',
            last_name='Пользователь'
        )

        self.moderator_user = User.objects.create_user(
            email='moderator@test.ru',
            username='moderator',
            password='testpass123',
            first_name='Модератор',
            last_name='Тестовый'
        )
        # Добавляем модератора в группу
        self.moderator_user.groups.add(self.moderator_group)

        # Создаем курс от имени владельца
        self.course = Course.objects.create(
            name='Тестовый курс',
            description='Описание тестового курса',
            owner=self.owner_user
        )

        # Создаем урок от имени владельца
        self.lesson = Lesson.objects.create(
            course=self.course,
            name='Тестовый урок',
            description='Описание тестового урока',
            video_link='https://www.youtube.com/watch?v=test123',
            owner=self.owner_user
        )

    def test_lesson_create_by_owner(self):
        """
        Тест: Владелец может создать урок в своем курсе
        """
        self.client.force_authenticate(user=self.owner_user)

        url = reverse('lms:lesson-create')
        data = {
            'course': self.course.id,
            'name': 'Новый урок от владельца',
            'description': 'Описание нового урока',
            'video_link': 'https://www.youtube.com/watch?v=new123'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.last().owner, self.owner_user)

    def test_lesson_create_by_other_user(self):
        """
        Тест: Другой пользователь не может создать урок в чужом курсе
        """
        self.client.force_authenticate(user=self.other_user)

        url = reverse('lms:lesson-create')
        data = {
            'course': self.course.id,
            'name': 'Урок от чужого пользователя',
            'description': 'Описание урока',
            'video_link': 'https://www.youtube.com/watch?v=other123'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_lesson_create_by_moderator(self):
        """
        Тест: Модератор не может создать урок
        """
        self.client.force_authenticate(user=self.moderator_user)

        url = reverse('lms:lesson-create')
        data = {
            'course': self.course.id,
            'name': 'Урок от модератора',
            'description': 'Описание урока',
            'video_link': 'https://www.youtube.com/watch?v=mod123'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_lesson_list_by_owner(self):
        """
        Тест: Владелец видит только свои уроки
        """
        # Создаем урок от другого пользователя
        other_course = Course.objects.create(
            name='Курс другого',
            description='Описание',
            owner=self.other_user
        )
        Lesson.objects.create(
            course=other_course,
            name='Урок другого',
            description='Описание',
            video_link='https://www.youtube.com/watch?v=other456',
            owner=self.other_user
        )

        self.client.force_authenticate(user=self.owner_user)

        url = reverse('lms:lesson-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Тестовый урок')

    def test_lesson_list_by_moderator(self):
        """
        Тест: Модератор видит все уроки
        """
        # Создаем урок от другого пользователя
        other_course = Course.objects.create(
            name='Курс другого',
            description='Описание',
            owner=self.other_user
        )
        Lesson.objects.create(
            course=other_course,
            name='Урок другого',
            description='Описание',
            video_link='https://www.youtube.com/watch?v=other456',
            owner=self.other_user
        )

        self.client.force_authenticate(user=self.moderator_user)

        url = reverse('lms:lesson-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_lesson_update_by_owner(self):
        """
        Тест: Владелец может обновить свой урок
        """
        self.client.force_authenticate(user=self.owner_user)

        url = reverse('lms:lesson-update', args=[self.lesson.id])
        data = {
            'name': 'Обновленное название урока',
            'description': 'Обновленное описание'
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, 'Обновленное название урока')

    def test_lesson_update_by_other_user(self):
        """
        Тест: Другой пользователь не может обновить чужой урок
        """
        self.client.force_authenticate(user=self.other_user)

        url = reverse('lms:lesson-update', args=[self.lesson.id])
        data = {
            'name': 'Попытка обновить чужой урок'
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lesson_delete_by_owner(self):
        """
        Тест: Владелец может удалить свой урок
        """
        self.client.force_authenticate(user=self.owner_user)

        url = reverse('lms:lesson-delete', args=[self.lesson.id])
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_lesson_delete_by_other_user(self):
        """
        Тест: Другой пользователь не может удалить чужой урок
        """
        self.client.force_authenticate(user=self.other_user)

        url = reverse('lms:lesson-delete', args=[self.lesson.id])
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_video_link_validation_youtube(self):
        """
        Тест: Валидация ссылки - только youtube
        """
        self.client.force_authenticate(user=self.owner_user)

        url = reverse('lms:lesson-create')
        data = {
            'course': self.course.id,
            'name': 'Урок с недопустимой ссылкой',
            'description': 'Описание',
            'video_link': 'https://rutube.ru/video/123'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_link', response.data)

    def test_subscribe_to_course(self):
        """
        Тест: Подписка на курс
        """
        self.client.force_authenticate(user=self.other_user)

        url = reverse('users:subscribe')
        data = {'course_id': self.course.id}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(response.data['is_subscribed'])
        self.assertTrue(Subscription.objects.filter(
            user=self.other_user,
            course=self.course
        ).exists())

    def test_unsubscribe_from_course(self):
        """
        Тест: Отписка от курса
        """
        # Сначала подписываемся
        Subscription.objects.create(
            user=self.other_user,
            course=self.course
        )

        self.client.force_authenticate(user=self.other_user)

        url = reverse('users:subscribe')
        data = {'course_id': self.course.id}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(response.data['is_subscribed'])
        self.assertFalse(Subscription.objects.filter(
            user=self.other_user,
            course=self.course
        ).exists())

    def test_subscribe_without_course_id(self):
        """
        Тест: Подписка без указания course_id
        """
        self.client.force_authenticate(user=self.other_user)

        url = reverse('users:subscribe')
        data = {}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_is_subscribed_field_in_course(self):
        """
        Тест: В курсе есть поле is_subscribed
        """
        # Подписываем пользователя на курс
        Subscription.objects.create(
            user=self.owner_user,
            course=self.course
        )

        self.client.force_authenticate(user=self.owner_user)

        url = reverse('lms:course-detail', args=[self.course.id])
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])

    def test_lesson_create_in_other_course(self):
        """
        Тест: Создание урока в чужом курсе
        """
        other_course = Course.objects.create(
            name='Курс другого',
            description='Описание',
            owner=self.other_user
        )

        self.client.force_authenticate(user=self.owner_user)

        url = reverse('lms:lesson-create')
        data = {
            'course': other_course.id,
            'name': 'Попытка создать урок в чужом курсе',
            'description': 'Описание',
            'video_link': 'https://www.youtube.com/watch?v=test'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)