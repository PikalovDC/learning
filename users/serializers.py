from rest_framework import serializers
from .models import Payment

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