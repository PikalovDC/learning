import re
from rest_framework.exceptions import ValidationError


def validate_youtube_url(value):
    """
    Валидатор проверяет, что ссылка ведет на youtube.com
    """
    if not value:
        return value

    # Регулярное выражение для проверки youtube ссылок
    youtube_pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/'

    if not re.search(youtube_pattern, value):
        raise ValidationError(
            'Разрешены только ссылки на YouTube (youtube.com или youtu.be)'
        )

    return value
