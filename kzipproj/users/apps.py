from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = "Пользователи"

    def ready(self):
        # у ready() есть особенность, он в тестах выполняется 1 раз, при запуске сервера - 2.
        # учтите на будущее (если будете убирать сейчас сигналы, это не важно):
        # https://docs.djangoproject.com/en/1.10/topics/signals/#preventing-duplicate-signals
        from .signals.receivers import send_success_mail