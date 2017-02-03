from django.test import TestCase
from ..models import ExtUser
from rest_framework.reverse import reverse
from django.core import mail
from .factories import UserFactoryBase


class UserCreateViewTestCase(TestCase):
    """
        Test UserCreate view
        create user
        create user with existing
        check send activation mail after user creation
    """

    def setUp(self):
        self.register_path = reverse('users:register')
        self.user_factory = UserFactoryBase
        self.TEST_USERS_PASSWORD = UserFactoryBase.get_test_user_password()

    def test_ok_allowany_can_create_user(self):
        user = self.user_factory.build()
        self.assertNotIn('_auth_user_id', self.client.session)
        response = self.client.post(path=self.register_path,
                                    data={
                                        'email': user.email,
                                        'name': user.name,
                                        'password': self.TEST_USERS_PASSWORD
                                    })
        self.assertEqual(response.status_code, 201)
        created_user = ExtUser.objects.get(email=user.email)
        self.assertTrue(created_user.pk)

    def test_fail_create_user_with_existing_email(self):
        user = self.user_factory.create()
        response = self.client.post(path=self.register_path,
                                    data={
                                        'email': user.email,
                                        'name': user.name,
                                        'password': self.TEST_USERS_PASSWORD
                                    })
        self.assertEqual(response.status_code, 400)

    def test_ok_send_activation_email(self):
        user = self.user_factory.build()
        response = self.client.post(path=self.register_path,
                                    data={
                                        'email': user.email,
                                        'name': user.name,
                                        'password': self.TEST_USERS_PASSWORD
                                    })
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertIn(user.email, mail.outbox[0].to)
