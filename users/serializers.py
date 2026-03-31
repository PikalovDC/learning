from rest_framework import serializers
from .models import Payment, User


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра профиля (ограниченные поля)"""

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'phone_number', 'city', 'avatar', 'date_joined']
        read_only_fields = ['id', 'email', 'date_joined']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'city', 'avatar']


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    password = serializers.CharField(write_only=True, required=False)
    password2 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'password2',
                  'first_name', 'last_name', 'phone_number', 'city',
                  'avatar', 'date_joined']
        read_only_fields = ['id', 'date_joined']

    def validate(self, data):
        # Проверка пароля только при создании
        if 'password' in data and 'password2' in data:
            if data['password'] != data['password2']:
                raise serializers.ValidationError({'password': 'Пароли не совпадают'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2', None)
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        # При обновлении игнорируем поля пароля
        validated_data.pop('password', None)
        validated_data.pop('password2', None)
        return super().update(instance, validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    course_name = serializers.CharField(source='paid_course.name', read_only=True, allow_null=True)
    lesson_name = serializers.CharField(source='paid_lesson.name', read_only=True, allow_null=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'user_email',
            'payment_date',
            'paid_course',
            'course_name',
            'paid_lesson',
            'lesson_name',
            'amount',
            'payment_method'
        ]
        read_only_fields = ['payment_date']
