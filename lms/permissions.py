from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверка, является ли пользователь модератором"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Moderators').exists()


class IsOwner(permissions.BasePermission):
    """Проверка, является ли пользователь владельцем объекта"""

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class CanCreateCourse(permissions.BasePermission):
    """Только обычные пользователи (не модераторы) могут создавать курсы"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if view.action == 'create':
            return not request.user.groups.filter(name='Moderators').exists()
        return True


class CanCreateLesson(permissions.BasePermission):
    """Только обычные пользователи (не модераторы) могут создавать уроки"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Модераторы не могут создавать
        return not request.user.groups.filter(name='Moderators').exists()


class CanEditCourse(permissions.BasePermission):
    """Модераторы могут редактировать любые курсы, владельцы - свои"""

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Модератор может редактировать
        if request.user.groups.filter(name='Moderators').exists():
            return view.action in ['update', 'partial_update']

        # Владелец может редактировать
        return obj.owner == request.user


class CanEditLesson(permissions.BasePermission):
    """Модераторы могут редактировать любые уроки, владельцы - свои"""

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Модератор может редактировать
        if request.user.groups.filter(name='Moderators').exists():
            return True

        # Владелец может редактировать
        return obj.owner == request.user


class CanDeleteCourse(permissions.BasePermission):
    """Только владельцы могут удалять свои курсы. Модераторы не могут удалять"""

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Модераторы не могут удалять
        if request.user.groups.filter(name='Moderators').exists():
            return False

        # Владелец может удалять
        return obj.owner == request.user


class CanDeleteLesson(permissions.BasePermission):
    """Только владельцы могут удалять свои уроки. Модераторы не могут удалять"""

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Модераторы не могут удалять
        if request.user.groups.filter(name='Moderators').exists():
            return False

        # Владелец может удалять
        return obj.owner == request.user