from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.test import TestCase, RequestFactory
from django.core import mail
from .factories import UserFactoryBase, PathAPIRequestFactory
from ..utils.emails import UserEmailFactoryBase
from ..utils import utils


class UserEmailBaseTestCase(TestCase):
    def setUp(self):
        self.request_factory = PathAPIRequestFactory(path='/')
        self.user = UserFactoryBase.create()
        self.email_factory = UserEmailFactoryBase
        self.request = self.request_factory.get()

    def test_fail_build_email(self):
        with self.assertRaises(TypeError):
            self.email_factory.build(self.request, self.user)


class UserActivationEmail(TestCase):
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

        # def test_fail_send_build_email(self):
    #     email = self.email_factory.build(self.request, self.user)
    #     email.send()
    #     self.assertEqual(len(mail.outbox), 1)
    #     self.assertEqual(len(mail.outbox[0].to), 1)
    #     self.assertIn(self.user.email, mail.outbox[0].to)

    # self.assertIsInstance(email, UserEmailFactoryBase)
    # self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
    # self.assertEqual(email.user.email, self.user.email)
    # self.assertEqual(email.protocol, self.request.scheme)
    # self.assertEqual(str(email.site_name), 'testserver')
    # self.assertEqual(str(email.domain), 'testserver')

# class ActivationEmailTest(TestCase):
#     def setUp(self):
#         self.request_factory = RequestFactory()
#         self.user = UserFactoryBase.create()
#
#
#     def test_ok_url_format(self):
#         request = self.request_factory.get('/')
#         email = emails.UserActivationEmail.from_request(self.req, self.user)
#
#         uid = utils.encode_uid(email.user.pk)
#         token = default_token_generator.make_token(email.user)
#
#         url = email.get_context().get('url')
#         self.assertEqual(
#             url, 'account/activate/?uid={}&token={}'.format(uid, token)
#         )
#

# class UserPasswordResetEmailTest(TestCase):
#     def setUp(self):
#         self.rf = RequestFactory()
#         self.req = self.rf.get('/')
#         self.user = factories.ActiveUser.create()
#
#     def test_ok_url_format(self):
#         email = emails.UserPasswordResetEmail(self.req, self.user)
#
#         uid = utils.encode_uid(email.user.pk)
#         token = default_token_generator.make_token(email.user)
#
#         url = email.get_context().get('url')
#         self.assertEqual(
#             url,
#             'account/password/reset/confirm/?uid=%s&token=%s' % (uid, token)
#         )
