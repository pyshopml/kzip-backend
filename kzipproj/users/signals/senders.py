from django.dispatch import Signal

# # New user changed password.
# password_changed = Signal(providing_args=["user", "request"])

# Confirm mail
confim_email = Signal(providing_args=['user', 'request'])
