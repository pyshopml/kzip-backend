# файл с объявлением сигналов принято называть signals.py
# для примера можно посмотреть, как в самом джанго объявлен какой-либо сигнал, например, pre_save.
from django.dispatch import Signal

# # New user changed password.
# password_changed = Signal(providing_args=["user", "request"])

# Confirm mail
confirm_email = Signal(providing_args=['user', 'request'])
# внимательнее относитесь к орфографии: если не видно, поменяйте цвет спелл-чекера в настройках IDE.
#
# исправил
