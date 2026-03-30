from rest_framework import permissions


class CanEditCourse(permissions.BasePermission):
    """
    Права для курсов:
    - Модераторы: могут редактировать любые, но не создавать и не удалять
    - Обычные пользователи: могут всё только со своими курсами
    """

    def has_permission(self, request, view):
        # Модераторы не могут создавать
        if view.action == 'create':
            return not request.user.groups.filter(name='Moderators').exists()
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Модераторы не могут удалять
        if view.action == 'destroy':
            return not user.groups.filter(name='Moderators').exists()

        # Модераторы могут редактировать любые курсы
        if view.action in ['update', 'partial_update']:
            if user.groups.filter(name='Moderators').exists():
                return True
            # Обычные пользователи могут редактировать только свои курсы
            return obj.owner == user

        # Просмотр
        return True


class CanEditLesson(permissions.BasePermission):
    """
    Права для уроков:
    - Модераторы: могут редактировать любые, но не создавать и не удалять
    - Обычные пользователи: могут всё только со своими уроками
    """

    def has_permission(self, request, view):
        # Модераторы не могут создавать
        if view.__class__.__name__ == 'LessonCreateAPIView':
            return not request.user.groups.filter(name='Moderators').exists()
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Модераторы не могут удалять
        if view.__class__.__name__ == 'LessonDestroyAPIView':
            return not user.groups.filter(name='Moderators').exists()

        # Модераторы могут редактировать любые уроки
        if view.__class__.__name__ in ['LessonUpdateAPIView']:
            if user.groups.filter(name='Moderators').exists():
                return True
            # Обычные пользователи могут редактировать только свои уроки
            return obj.owner == user

        # Просмотр
        return True