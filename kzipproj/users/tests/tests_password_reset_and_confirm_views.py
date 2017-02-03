from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from ..models import ExtUser
from ..utils import utils
from .. import consts
from .factories import ActiveUser, PathAPIRequestFactory


class ResetViewTestCase(APITestCase):
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


class PasswordResetConfirmViewTestCase(APITestCase):
    def setUp(self):
        self.reset_path = reverse('users:password_reset_confirm')
        self.active_user = ActiveUser
        self.reset_confirm_url = '/auth/password/reset/confirm/?uid={uid}&token={token}'
        self.TEST_USERS_PASSWORD = self.active_user.get_test_user_password()

    def test_ok_get_data_for_change_password(self):
        user = ActiveUser.create()
        UID = utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        pasword_reset_url = self.reset_confirm_url.format(uid=UID, token=token)
        response = self.client.get(pasword_reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['uid'], UID)
        self.assertEqual(response.data['token'], token)

    def test_fail_get_data_for_change_password_with_wrong_uid(self):
        user = ActiveUser.create()
        UID = utils.encode_uid(user.pk + 1)
        token = default_token_generator.make_token(user)
        pasword_reset_url = self.reset_confirm_url.format(uid=UID, token=token)
        response = self.client.get(pasword_reset_url)
        self.assertEqual(response.status_code, 400)
        self.assertIn(consts.INVALID_UID, response.data['uid'])

    def test_fail_get_data_for_change_password_with_wrong_token(self):
        user = ActiveUser.create()
        UID = utils.encode_uid(user.pk)
        wrong_token = default_token_generator.make_token(user) + str(1)
        pasword_reset_url = self.reset_confirm_url.format(uid=UID, token=wrong_token)
        response = self.client.get(pasword_reset_url)
        self.assertEqual(response.status_code, 400)
        self.assertIn(consts.INVALID_TOKEN, response.data['non_field_errors'])

    def test_ok_change_password(self):
        user = ActiveUser.create()
        old_password = ActiveUser.get_test_user_password()
        self.assertTrue(user.check_password(old_password))
        UID = utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        new_password = 'Q123456789'
        pasword_reset_url = self.reset_confirm_url.format(uid=UID, token=token)
        response = self.client.post(pasword_reset_url, data={'uid': UID,
                                                             'token': token,
                                                             'new_password': new_password})
        self.assertEqual(response.status_code, 200)
        user = ExtUser.objects.get(email=user.email)
        self.assertFalse(user.check_password(old_password))
        self.assertTrue(user.check_password(new_password))

    def test_fail_change_password_wirh_wrong_token(self):
        user = ActiveUser.create()
        old_password = ActiveUser.get_test_user_password()
        self.assertTrue(user.check_password(old_password))
        UID = utils.encode_uid(user.pk)
        wrong_token = default_token_generator.make_token(user) + str(1)
        new_password = 'Q123456789'
        pasword_reset_url = self.reset_confirm_url.format(uid=UID, token=wrong_token)
        response = self.client.post(pasword_reset_url, data={'uid': UID,
                                                             'token': wrong_token,
                                                             'new_password': new_password})
        self.assertEqual(response.status_code, 400)
        user = ExtUser.objects.get(email=user.email)
        self.assertTrue(user.check_password(old_password))
        self.assertFalse(user.check_password(new_password))

    def test_fail_change_password_wirh_wrong_UID(self):
        user = ActiveUser.create()
        old_password = ActiveUser.get_test_user_password()
        self.assertTrue(user.check_password(old_password))
        bad_UID = utils.encode_uid(user.pk + 1)
        token = default_token_generator.make_token(user)
        new_password = 'Q123456789'
        pasword_reset_url = self.reset_confirm_url.format(uid=bad_UID, token=token)
        response = self.client.post(pasword_reset_url, data={'uid': bad_UID,
                                                             'token': token,
                                                             'new_password': new_password})
        self.assertEqual(response.status_code, 400)
        user = ExtUser.objects.get(email=user.email)
        self.assertTrue(user.check_password(old_password))
        self.assertFalse(user.check_password(new_password))

    def test_ok_send_mail_after_change_password(self):
        user = ActiveUser.create()
        old_password = ActiveUser.get_test_user_password()
        self.assertTrue(user.check_password(old_password))
        UID = utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        new_password = 'Q123456789'
        pasword_reset_url = self.reset_confirm_url.format(uid=UID, token=token)
        response = self.client.post(pasword_reset_url, data={'uid': UID,
                                                             'token': token,
                                                             'new_password': new_password})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertIn(user.email, mail.outbox[0].to)

    def test_fail_send_mail_after_change_password(self):
        user = ActiveUser.create()
        old_password = ActiveUser.get_test_user_password()
        self.assertTrue(user.check_password(old_password))
        bad_UID = utils.encode_uid(user.pk + 1)
        token = default_token_generator.make_token(user)
        new_password = 'Q123456789'
        pasword_reset_url = self.reset_confirm_url.format(uid=bad_UID, token=token)
        response = self.client.post(pasword_reset_url, data={'uid': bad_UID,
                                                             'token': token,
                                                             'new_password': new_password})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)

