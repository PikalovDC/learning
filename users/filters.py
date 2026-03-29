import django_filters
from .models import Payment

class PaymentFilter(django_filters.FilterSet):
    paid_course = django_filters.NumberFilter(field_name='paid_course_id')
    paid_lesson = django_filters.NumberFilter(field_name='paid_lesson_id')
    lesson_name = django_filters.CharFilter(field_name='paid_lesson__name', lookup_expr='icontains')

    class Meta:
        model = Payment
        fields = {
            'payment_method': ['exact'],
            'paid_course': ['exact'],
            'paid_lesson': ['exact'],
        }