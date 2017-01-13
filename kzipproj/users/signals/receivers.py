from django.dispatch import receiver

from .senders import confim_email
from ..utils.emails import UserConfirmationEmail


@receiver(confim_email)
def send_success_mail(sender, **kwargs):
    user = kwargs['user']
    request = kwargs['request']
    email_factory = UserConfirmationEmail.from_request(request, user)
    email = email_factory.create()
    email.send()


