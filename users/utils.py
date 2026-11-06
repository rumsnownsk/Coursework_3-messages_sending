import os
import uuid
from django.forms import ValidationError

from transliterate import translit


def get_user_avatar_path(instance, filename):
    """Путь для аватаров пользователей: users/avatars/username_uuid.ext"""
    name, ext = os.path.splitext(filename)
    # Берем username для имени файла (он точно есть)
    base_name = translit(instance.username, 'ru', reversed=True).lower()
    base_name = re.sub(r'[^a-z0-9\-]+', '-', base_name).strip('-')
    unique_id = uuid.uuid4().hex[:6]
    return f'users/avatars/{base_name}_{unique_id}{ext}'