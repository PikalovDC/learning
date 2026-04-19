from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def send_course_update_email(course_id, course_name, changes_description):
    """
    Асинхронная рассылка писем подписчикам курса об обновлении
    """
    from .models import Subscription

    # Получаем всех подписчиков курса
    subscriptions = Subscription.objects.filter(course_id=course_id).select_related('user')

    if not subscriptions.exists():
        return f"No subscribers for course {course_name}"

    recipients = [sub.user.email for sub in subscriptions]

    subject = f"Обновление курса: {course_name}"
    message = f"""
    Здравствуйте!

    Курс "{course_name}" был обновлен.

    Изменения: {changes_description}

    С уважением,
    Команда Learning Platform
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        return f"Email sent to {len(recipients)} subscribers of course {course_name}"
    except Exception as e:
        return f"Error sending emails: {str(e)}"


@shared_task
def deactivate_inactive_users():
    """
    Блокирует пользователей, которые не заходили более месяца
    """
    # Вычисляем дату месяц назад
    month_ago = timezone.now() - timedelta(days=30)

    # Находим активных пользователей, которые не заходили более месяца
    inactive_users = User.objects.filter(
        is_active=True,
        last_login__lt=month_ago
    )

    count = inactive_users.count()

    if count > 0:
        # Блокируем пользователей
        updated_count = inactive_users.update(is_active=False)
        return f"Заблокировано {updated_count} неактивных пользователей"

    return "Нет неактивных пользователей для блокировки"
