from django.core import mail
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .. import consts
from .factories import ActiveUser, PathAPIRequestFactory


class ActivationViewTestCase(APITestCase):
    def setUp(self):
        self.reset_path = reverse('users:password_reset')
        self.active_user = ActiveUser
        self.request_factory = PathAPIRequestFactory(path='/')
        self.TEST_USERS_PASSWORD = self.active_user.get_test_user_password()

    def test_ok_sending_password_reset_email_method_get(self):
        user = self.active_user.create()
        response = self.client.get(self.reset_path, data={'email': user.email})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['detail'], consts.RESET_EMAIL_SENT)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertIn(user.email, mail.outbox[0].to)

    def test_fail_sending_mail_with_non_existent_email_method_get(self):
        response = self.client.get(self.reset_path, data={'email': 'fail_mail@mail.com'})
        self.assertEqual(response.status_code, 400)
        self.assertIn(consts.EMAIL_NOT_FOUND, response.data['email'])
        self.assertEqual(len(mail.outbox), 0)

    def test_ok_allowany_can_reset_password(self):
        user = self.active_user.create()
        self.assertNotIn('_auth_user_id', self.client.session)
        response = self.client.get(self.reset_path, data={'email': user.email})
        self.assertEqual(response.status_code, 200)

    def test_ok_sending_password_reset_email_method_post(self):
        user = self.active_user.create()
        response = self.client.post(self.reset_path, data={'email': user.email})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['detail'], consts.RESET_EMAIL_SENT)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertIn(user.email, mail.outbox[0].to)
