from django.test import TestCase
from rest_framework.reverse import reverse

from ..models import ExtUser
from .. import consts


class LoginViewTestCase(TestCase):
    def test_ok_login_successful(self):
        email, password = 'sym1@gmail.com', 'qweasdzxc'
        user = ExtUser.objects.create_user(email=email, password=password, is_active=True)
        response = self.client.post(path=reverse('login'),
                                    data={
                                        'email': email,
                                        'password': password
                                    })
        self.assertEquals(response.status_code, 200)

        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_fail_login_inactive_user(self):
        email, password = 'sym2@gmail.com', 'qweasdzxc'
        user = ExtUser.objects.create_user(email=email, password=password, is_active=False)
        print(user.is_active)
        response = self.client.post(path=reverse('login'),
                                    data={
                                        'email': email,
                                        'password': password
                                    })
        self.assertEquals(response.status_code, 401)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.data['message'], consts.INACTIVE_ACCOUNT)

    def test_fail_incorrect_credentials(self):
        response = self.client.post(path=reverse('login'),
                                    data={'email': 'email', 'password': 'password'})

        self.assertEquals(response.status_code, 400)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.data['message'], consts.INVALID_CREDENTIALS)

        response = self.client.post(path=reverse('login'),
                                    data={'password': 'password'})

        self.assertEquals(response.status_code, 400)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.data['message'], consts.INVALID_CREDENTIALS)