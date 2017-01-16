from django.conf import settings as django_settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template import loader

from .utils import encode_uid


class UserEmailFactoryBase(object):
    token_generator = default_token_generator
    subject_template_name = None
    plain_body_template_name = None
    html_body_template_name = None

    def __init__(self, from_email, user, protocol, domain, site_name):
        self.from_email = from_email
        self.user = user
        self.domain = domain
        self.site_name = site_name
        self.protocol = protocol

    def get_context(self):
        return {
            'user': self.user,
            'domain': self.domain,
            'site_name': self.site_name,
            'uid': encode_uid(self.user.pk),
            'token': self.token_generator.make_token(self.user),
            'protocol': self.protocol,
        }

    @classmethod
    def from_request(cls, request, user=None, from_email=None):
        site = get_current_site(request)
        return cls(
            from_email=getattr(django_settings, 'DEFAULT_FROM_EMAIL', from_email),
            user=user,
            domain=site.domain,
            site_name=site.name,
            protocol='https' if request.is_secure() else 'http',
        )

    def send(self, ):
        context = self.get_context()
        subject = loader.render_to_string(self.subject_template_name, context)
        subject = ''.join(subject.splitlines())

        plain_body = loader.render_to_string(self.plain_body_template_name, context)
        message = {
            'subject': subject,
            'message': plain_body,
            'from_email': self.from_email,

        }
        self.user.email_user(**message)


class UserPasswordResetEmail(UserEmailFactoryBase):
    subject_template_name = 'users/password_reset_email_subject.txt'
    plain_body_template_name = 'users/password_reset_email_body.txt'
    PASSWORD_RESET_CONFIRM_URL = 'auth/password/reset/confirm/'

    def get_context(self):
        context = super(UserPasswordResetEmail, self).get_context()
        context['url'] = self.PASSWORD_RESET_CONFIRM_URL.format(**context)
        return context


class UserActivationEmail(UserEmailFactoryBase):
    subject_template_name = 'users/activation_email_subject.txt'
    plain_body_template_name = 'users/activation_email_body.txt'
    ACTIVATE_CONFIRM_URL = 'auth/account/activate/'

    def get_context(self):
        context = super(UserActivationEmail, self).get_context()
        context['url'] = self.ACTIVATE_CONFIRM_URL.format(**context)
        return context


class UserConfirmationEmail(UserEmailFactoryBase):
    subject_template_name = 'users/confirmation_email_subject.txt'
    plain_body_template_name = 'users/confirmation_email_body.txt'
