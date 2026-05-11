# Learning - Платформа для онлайн-обучения

## Запуск через Docker

1. Скопируйте `.env.sample` в `.env` и заполните переменные
2. Выполните команду: `docker compose up --build`
3. Создайте суперпользователя: `docker compose exec web python manage.py createsuperuser`

## Локальный запуск (без Docker)

1. Установите зависимости: `pip install -r requirements.txt`
2. Создайте базу данных PostgreSQL и настройте `.env`
3. Выполните миграции: `python manage.py migrate`
4. Запустите Redis: `redis-server`
5. Запустите Celery (в отдельном терминале): `celery -A celery_app worker --loglevel=info -P eventlet`
6. Запустите Celery-beat (в отдельном терминале): `celery -A celery_app beat --loglevel=info`
7. Запустите Django сервер: `python manage.py runserver`

## Переменные окружения

Создайте файл `.env` по примеру `.env.sample`

## Документация API

После запуска:
- Swagger: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`
- Админка: `http://localhost:8000/admin/`

## Тесты

```bash
python manage.py test