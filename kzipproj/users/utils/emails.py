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
    def subject_template(self):
        pass

    @abstractproperty
    def plain_body_template(self):
        pass

    @abstractproperty
    def html_body_template(self):
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

    def render_mail(self):
        context = self.get_context()
        subject = loader.render_to_string(self.subject_template, context)
        subject = ''.join(subject.splitlines())

        plain_body = loader.render_to_string(self.plain_body_template, context)
        message = {
            'subject': subject,
            'message': plain_body,
            'from_email': self.from_email,
        }
        if self.html_body_template:
            message['html_message'] = loader.render_to_string(self.html_body_template, context)
        return message

    def send(self):
        message = self.render_mail()
        if hasattr(self.user, 'email_user'):
            self.user.email_user(**message)
        else:
            message['email'] = [self.user.email]
            send_mail(**message)


class UserEmailUrlMixin(object):

    def get_context(self):
        context = super(UserEmailUrlMixin, self).get_context()
        context['url'] = self.action_url.format(**context)
        return context


class UserActivationEmail(UserEmailUrlMixin, UserEmailFactoryBase):
    @property
    def html_body_template(self):
        return None

    subject_template = 'users/activation_email_subject.txt'
    plain_body_template = 'users/activation_email_body.txt'
    action_url = 'auth/account/activate/?uid={uid}&token={token}'


class UserPasswordResetEmail(UserEmailUrlMixin, UserEmailFactoryBase):
    @property
    def html_body_template(self):
        return None

    subject_template = 'users/password_reset_email_subject.txt'
    plain_body_template = 'users/password_reset_email_body.txt'
    action_url = 'auth/password/reset/confirm/?uid={uid}&token={token}'


class UserConfirmationEmail(UserEmailFactoryBase):
    @property
    def action_url(self):
        return None

    @property
    def html_body_template(self):
        return None

    subject_template = 'users/confirmation_email_subject.txt'
    plain_body_template = 'users/confirmation_email_body.txt'
