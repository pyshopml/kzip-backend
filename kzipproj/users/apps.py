from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = "Пользователи"

    def ready(self):
        from .signals.receivers import send_success_mail