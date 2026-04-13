from django.shortcuts import render
from rest_framework import generics, status, views
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from users.models import Payment, User, Subscription
from users.serializers import (UserProfileSerializer, UserUpdateSerializer, PaymentSerializer, UserSerializer,
SubscriptionSerializer)
from .filters import PaymentFilter
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from lms.models import Course


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