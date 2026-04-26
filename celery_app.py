import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('learning')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# --- НАСТРОЙКА ПЕРИОДИЧЕСКИХ ЗАДАЧ (СОГЛАСНО ДОКУМЕНТАЦИИ) ---
app.conf.beat_schedule = {
    'deactivate-inactive-users': { # Уникальное имя задачи
        'task': 'users.tasks.deactivate_inactive_users', # Путь к задаче
        'schedule': crontab(hour=0, minute=0), # Выполнять в 00:00 каждый день
        # 'args': (16, 16),  # Можно передать аргументы, если нужно
        # 'kwargs': {},      # Можно передать именованные аргументы
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
