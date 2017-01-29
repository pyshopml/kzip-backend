from django.conf import settings as django_settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail
from django.template import loader
from abc import ABCMeta, abstractproperty

from .utils import encode_uid


class UserEmailFactoryBase(metaclass=ABCMeta):
    token_generator = default_token_generator

    @abstractproperty
    def subject_template_name(self):
        pass

    @abstractproperty
    def plain_body_template_name(self):
        pass

    @abstractproperty
    def html_body_template_name(self):
        pass

    @abstractproperty
    def action_url(self):
        pass

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
            'url': self.action_url
        }

    @classmethod
    def build(cls, request, user, from_email=None):
        site = get_current_site(request)
        return cls(
            from_email=from_email or getattr(django_settings, 'DEFAULT_FROM_EMAIL'),
            user=user,
            domain=site.domain,
            site_name=site.name,
            protocol='https' if request.is_secure() else 'http',
        )

    def send(self):
        context = self.get_context()
        subject = loader.render_to_string(self.subject_template_name, context)
        subject = ''.join(subject.splitlines())

        plain_body = loader.render_to_string(self.plain_body_template_name, context)
        message = {
            'subject': subject,
            'message': plain_body,
            'from_email': self.from_email,
            'email': [self.user.email],
        }
        if hasattr(self.user, 'email_user'):
            self.user.email_user(**message)
        else:
            send_mail(**message)


class UserActivationEmail(UserEmailFactoryBase):
    @property
    def html_body_template_name(self):
        return None

    subject_template_name = 'users/activation_email_subject.txt'
    plain_body_template_name = 'users/activation_email_body.txt'
    action_url = 'auth/account/activate/?uid={uid}&token={token}'


class UserPasswordResetEmail(UserEmailFactoryBase):
    @property
    def html_body_template_name(self):
        return None

    subject_template_name = 'users/password_reset_email_subject.txt'
    plain_body_template_name = 'users/password_reset_email_body.txt'
    action_url = 'auth/password/reset/confirm/?uid={uid}&token={token}'


class UserConfirmationEmail(UserEmailFactoryBase):
    @property
    def action_url(self):
        return None

    @property
    def html_body_template_name(self):
        return None

    subject_template_name = 'users/confirmation_email_subject.txt'
    plain_body_template_name = 'users/confirmation_email_body.txt'
