from django.shortcuts import render
from rest_framework import generics, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from users.models import Payment, User
from users.serializers import PaymentSerializer, UserSerializer
from .filters import PaymentFilter
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny


class UserCreateAPIView(generics.CreateAPIView):
    """Регистрация - доступно всем"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserListAPIView(generics.ListAPIView):
    """Список пользователей - только авторизованные"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Просмотр, обновление, удаление пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if request.user.id != self.get_object().id:
            return Response({'error': 'Можно редактировать только свой профиль'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.id != self.get_object().id:
            return Response({'error': 'Можно удалить только свой профиль'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter

    ordering_fields = ['payment_date', 'amount', 'id']
    ordering = ['-payment_date']
