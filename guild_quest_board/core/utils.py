def get_username(data):
    """Возвращает username пользователя."""
    return data['username']


def get_email(data):
    """Возвращает email пользователя."""
    return data['email']


def get_password(data):
    """Возвращает password пользователя."""
    return data['password']


def get_quest(self):
    """Возвращает квест."""
    return self.context['quest']


def get_user(self):
    """Возвращает текущего пользователя."""
    return self.context['request'].user


def patch_methods():
    """Возвращает список с методом patch."""
    return ['patch']


def get_methods():
    """Возвращает список с методом get."""
    return ['get']


def post_methods():
    """Возвращает список с методом post."""
    return ['post']
