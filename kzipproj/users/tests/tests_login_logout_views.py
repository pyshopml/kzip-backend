from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from .factories import ActiveUser, UserFactoryBase
from .. import consts


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.login_path = reverse('users:login')
        self.active_user_factory = ActiveUser
        self.user_factory = UserFactoryBase
        self.TEST_USERS_PASSWORD = UserFactoryBase.get_test_user_password()

    def test_ok_login_successful(self):
        user = self.active_user_factory.create()
        response = self.client.post(path=self.login_path,
                                    data={
                                        'email': user.email,
                                        'password': self.TEST_USERS_PASSWORD,
                                    })
        self.assertEquals(response.status_code, 200)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_fail_login_inactive_user(self):
        user = self.user_factory.create()
        response = self.client.post(path=self.login_path,
                                    data={
                                        'email': user.email,
                                        'password': self.TEST_USERS_PASSWORD,
                                    })
        self.assertEquals(response.status_code, 401)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.data['message'], consts.INACTIVE_ACCOUNT)

    def test_fail_incorrect_credentials(self):
        user = self.active_user_factory.create()
        response = self.client.post(path=self.login_path,
                                    data={'email': user.email, 'password': 'password'})

        self.assertEquals(response.status_code, 400)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.data['message'], consts.INVALID_CREDENTIALS)

        response = self.client.post(path=self.login_path,
                                    data={'password': 'password'})

        self.assertEquals(response.status_code, 400)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.data['message'], consts.INVALID_CREDENTIALS)


class LogoutViewTestCase(TestCase):
    def setUp(self):
        self.login_path = reverse('users:logout')
        self.active_user_factory = ActiveUser
        self.TEST_USERS_PASSWORD = ActiveUser.get_test_user_password()

    def test_ok_user_logout_get(self):
        user = self.active_user_factory.create()
        is_login = self.client.login(email=user.email,
                                     password=self.TEST_USERS_PASSWORD)
        self.assertTrue(is_login)
        self.assertIsNotNone(self.client.session.session_key)
        response = self.client.get(self.login_path)
        self.assertEquals(response.status_code, 200)
        self.assertIsNone(self.client.session.session_key)

    def test_ok_user_logout_post(self):
        user = self.active_user_factory.create()
        is_login = self.client.login(email=user.email,
                                     password=self.TEST_USERS_PASSWORD)
        self.assertTrue(is_login)
        self.assertIsNotNone(self.client.session.session_key)
        response = self.client.post(self.login_path)
        self.assertEquals(response.status_code, 200)
        self.assertIsNone(self.client.session.session_key)
