from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.template import loader
from django.test import TestCase
from django.core import mail
from .factories import UserFactoryBase, PathAPIRequestFactory
from ..utils.emails import UserEmailFactoryBase, UserActivationEmail, UserPasswordResetEmail, UserConfirmationEmail
from ..utils import utils


class UserEmailBaseTestCase(TestCase):
    def setUp(self):
        self.request_factory = PathAPIRequestFactory(path='/')
        self.user = UserFactoryBase.create()
        self.email_factory = UserEmailFactoryBase
        self.request = self.request_factory.get()

    def test_fail_build_email(self):
        with self.assertRaises(TypeError) as exc:
            self.email_factory.build(self.request, self.user)
            # todo exception message assertion


class ActivationAndCommonEmailTestCase(TestCase):
    def setUp(self):
        self.request_factory = PathAPIRequestFactory(path='/')
        self.user = UserFactoryBase.create()
        self.email_factory = UserActivationEmail
        self.request = self.request_factory.get()

    def test_ok_build_instance(self):
        email = self.email_factory.build(self.request, self.user)

        self.assertIsInstance(email, UserActivationEmail)
        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(email.user.email, self.user.email)
        self.assertEqual(email.protocol, self.request.scheme)
        self.assertEqual(str(email.site_name), 'testserver')
        self.assertEqual(str(email.domain), 'testserver')

    def test_ok_get_context(self):
        email = self.email_factory.build(self.request, self.user)
        pregenerated_token = default_token_generator.make_token(self.user)
        uid = utils.encode_uid(self.user.pk)
        token = default_token_generator.make_token(self.user)
        url = 'auth/account/activate/?uid={}&token={}'.format(uid, token)
        expected_context = {
            'user': self.user,
            'protocol': self.request.scheme,
            'domain': 'testserver',
            'site_name': 'testserver',
            'uid': uid,
            'token': pregenerated_token,
            'url': url
        }
        self.assertDictEqual(email.get_context(), expected_context)

    def test_ok_email_sending(self):
        email = self.email_factory.build(self.request, self.user)
        email.send()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)

    def test_ok_url_format(self):
        email = self.email_factory.build(self.request, self.user)
        uid = utils.encode_uid(self.user.pk)
        token = default_token_generator.make_token(self.user)
        expected_action_url = 'auth/account/activate/?uid={}&token={}'.format(uid, token)
        action_url = email.get_context().get('url')
        self.assertEqual(action_url, expected_action_url)

    def test_ok_url_in_sent_mail(self):
        email = self.email_factory.build(self.request, self.user)
        email.send()
        uid = utils.encode_uid(self.user.pk)
        token = default_token_generator.make_token(self.user)
        expected_action_url = 'auth/account/activate/?uid={}&token={}'.format(uid, token)
        self.assertIn(expected_action_url, mail.outbox[0].body)


class PasswordResetEmailTestCase(TestCase):
    def setUp(self):
        self.request_factory = PathAPIRequestFactory(path='/')
        self.user = UserFactoryBase.create()
        self.email_factory = UserPasswordResetEmail
        self.request = self.request_factory.get()

    def test_ok_url_format(self):
        email = self.email_factory.build(self.request, self.user)
        uid = utils.encode_uid(self.user.pk)
        token = default_token_generator.make_token(self.user)
        expected_action_url = 'auth/password/reset/confirm/?uid={}&token={}'.format(uid, token)
        action_url = email.get_context().get('url')
        self.assertEqual(action_url, expected_action_url)

    def test_ok_url_in_sent_mail(self):
        email = self.email_factory.build(self.request, self.user)
        email.send()
        uid = utils.encode_uid(self.user.pk)
        token = default_token_generator.make_token(self.user)
        expected_action_url = 'auth/password/reset/confirm/?uid={}&token={}'.format(uid, token)
        self.assertIn(expected_action_url, mail.outbox[0].body)


class ConfirmationEmailTestCase(TestCase):
    def setUp(self):
        self.request_factory = PathAPIRequestFactory(path='/')
        self.user = UserFactoryBase.create()
        self.email_factory = UserConfirmationEmail
        self.request = self.request_factory.get()

    def test_ok_content_in_sent_mail(self):
        email = self.email_factory.build(self.request, self.user)
        email.send()
        subject_template = 'users/confirmation_email_subject.txt'
        plain_body_template = 'users/confirmation_email_body.txt'
        site_name = email.get_context().get('site_name')
        subject = loader.render_to_string(subject_template, {'site_name': site_name})
        body = loader.render_to_string(plain_body_template)
        self.assertIn(body, mail.outbox[0].body)
        self.assertIn(subject, mail.outbox[0].subject)
