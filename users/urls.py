from django.urls import path
from .views import (PaymentListAPIView, UserCreateAPIView, UserProfileAPIView, UserUpdateAPIView, UserDeleteAPIView,
SubscriptionAPIView, CreatePaymentView, PaymentStatusView)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'users'

urlpatterns = [
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('profile/', UserProfileAPIView.as_view(), name='profile'),
    path('profile/update/', UserUpdateAPIView.as_view(), name='profile-update'),
    path('profile/delete/', UserDeleteAPIView.as_view(), name='profile-delete'),
    path('subscribe/', SubscriptionAPIView.as_view(), name='subscribe'),
    path('pay/', CreatePaymentView.as_view(), name='create-payment'),
    path('payments/<int:payment_id>/status/', PaymentStatusView.as_view(), name='payment-status'),
]
