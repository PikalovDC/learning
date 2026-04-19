import stripe
from rest_framework import generics, status, views
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from users.models import Payment, User, Subscription
from users.serializers import (UserProfileSerializer, UserUpdateSerializer, PaymentSerializer, UserSerializer)
from .filters import PaymentFilter
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from lms.models import Course
from .services import create_stripe_payment_session
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Проверка статуса платежа по ID",
        responses={
            200: openapi.Response(
                description="Статус платежа",
                examples={
                    "application/json": {
                        "payment_id": 1,
                        "status": "paid",
                        "amount": 5000,
                        "course": "Название курса"
                    }
                }
            ),
            401: "Не авторизован",
            404: "Платеж не найден",
        }
    )

    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)

        if not payment.stripe_session_id:
            return Response({'status': 'pending', 'message': 'Сессия не создана'})

        session = stripe.checkout.Session.retrieve(payment.stripe_session_id)

        # Обновляем статус в БД
        payment.status = session.payment_status
        payment.save()

        return Response({
            'payment_id': payment.id,
            'status': session.payment_status,
            'amount': payment.amount,
            'course': payment.paid_course.name if payment.paid_course else None
        })


class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Создание платежа для курса через Stripe",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['course_id'],
            properties={
                'course_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID курса'),
                'amount': openapi.Schema(type=openapi.TYPE_INTEGER, description='Сумма в рублях (по умолчанию 5000)'),
            },
        ),
        responses={
            201: openapi.Response(
                description="Платеж создан",
                examples={
                    "application/json": {
                        "payment_id": 1,
                        "payment_url": "https://checkout.stripe.com/...",
                        "amount": 5000,
                        "course": "Название курса"
                    }
                }
            ),
            400: "Не указан course_id",
            401: "Не авторизован",
            404: "Курс не найден",
        }
    )

    def post(self, request):
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)

        # Сумма оплаты (можно брать из запроса или фиксированную)
        amount = request.data.get('amount', 5000)

        # Получаем ссылку на оплату от Stripe
        session_id, payment_url, product_id, price_id = create_stripe_payment_session(course.name, amount)

        # Создаем платеж в БД
        payment = Payment.objects.create(
            user=request.user,
            paid_course=course,
            amount=amount,
            payment_method='transfer',
            payment_url=payment_url,
            stripe_session_id=session_id,
            stripe_product_id=product_id,
            stripe_price_id=price_id,
            status='pending'
        )



        return Response({
            'payment_id': payment.id,
            'payment_url': payment_url,
            'amount': amount,
            'course': course.name
        })


class UserCreateAPIView(generics.CreateAPIView):
    """Регистрация - доступно всем"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserProfileAPIView(generics.RetrieveAPIView):
    """Просмотр профиля - только свои данные"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserUpdateAPIView(generics.UpdateAPIView):
    """Обновление профиля - только свои данные"""
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class UserDeleteAPIView(generics.DestroyAPIView):
    """Удаление профиля - только свои данные"""
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response({'message': 'Пользователь удален'}, status=status.HTTP_204_NO_CONTENT)


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date', 'amount', 'id']
    ordering = ['-payment_date']

    def get_queryset(self):
        """Пользователи видят только свои платежи"""
        return Payment.objects.filter(user=self.request.user)


class SubscriptionAPIView(views.APIView):
    """
    Эндпоинт для управления подпиской на курс:
    - Если подписка есть - удаляем
    - Если подписки нет - создаем
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Управление подпиской на курс (добавить/удалить)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['course_id'],
            properties={
                'course_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID курса'),
            },
        ),
        responses={
            200: openapi.Response(
                description="Подписка удалена",
                examples={"application/json": {"message": "Подписка удалена", "is_subscribed": False}}
            ),
            201: openapi.Response(
                description="Подписка добавлена",
                examples={"application/json": {"message": "Подписка добавлена", "is_subscribed": True}}
            ),
            400: "Не указан course_id",
            401: "Не авторизован",
            404: "Курс не найден",
        }
    )

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {"error": "Необходимо указать course_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)

        # Проверяем, есть ли подписка
        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            # Если подписка есть - удаляем
            subscription.delete()
            return Response(
                {"message": "Подписка удалена", "is_subscribed": False},
                status=status.HTTP_200_OK
            )
        else:
            # Если подписки нет - создаем
            Subscription.objects.create(user=user, course=course)
            return Response(
                {"message": "Подписка добавлена", "is_subscribed": True},
                status=status.HTTP_201_CREATED
            )
