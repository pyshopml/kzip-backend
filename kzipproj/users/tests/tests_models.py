from django.core import mail
from django.test import TestCase

from ..models import ExtUser
from .factories import UserFactoryBase
from .constants import *


class ExtUserTestCase(TestCase):
    """
        ExtUser model testcase.
        implement tests for methods:
            get_full_name
            get_short_name
            email_user
            __str__
        implement pending:
            has_perm
            has_module_perms
    """

    def setUp(self):
        self.user_factory = UserFactoryBase

    def test_ok_user_get_full_name_method(self):
        user = self.user_factory.create()
        self.assertEqual(user.get_full_name(), '{} {}'.format(user.email, user.name))

    def test_ok_user_get_short_name_method(self):
        user = self.user_factory.create()
        self.assertEqual(user.get_short_name(), user.email)

    def test_ok_user_str_(self):
        user = self.user_factory.create()
        self.assertEqual(str(user), user.email)

    def test_ok_send_user_mail(self):
        user = self.user_factory.create()
        subject = 'test134'
        message = 'test_body134'
        from_email = 'test@ukr.net'
        user.email_user(subject, message, from_email=from_email)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertEqual(mail.outbox[0].body, message)
        self.assertEqual(mail.outbox[0].from_email, from_email)
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertIn(user.email, mail.outbox[0].to)


class UserManagerTestCase(TestCase):
    """
        ExtUser model Manager testcase.
        implement tests for methods:
            _create_user
            create_user
            create_superuser
    """
    def setUp(self):
        self.user_factory = UserFactoryBase

    def test_ok__create_user(self):
        base_user = self.user_factory.build()
        self.assertFalse(base_user.pk)
        user_data = {
            'email': base_user.email,
            'name': base_user.name,
            'password': TEST_USERS_PASSWORD,
        }
        ExtUser.objects._create_user(**user_data)
        user = ExtUser.objects.get(email=base_user.email)

        self.assertIsInstance(user, ExtUser)
        self.assertTrue(user.pk)
        self.assertEqual(user.email, base_user.email)
        self.assertEqual(user.name, base_user.name)

        self.assertFalse(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.check_password(TEST_USERS_PASSWORD))

    def test_fail__create_user_without_email(self):
        base_user = self.user_factory.build()
        user_data = {
            'name': base_user.name,
            'password': TEST_USERS_PASSWORD,
        }
        self.assertRaises(TypeError,
                          ExtUser.objects._create_user,
                          **user_data)

    def test_fail__create_user_with_empty_email(self):
        base_user = self.user_factory.build()
        user_data = {
            'email': '',
            'name': base_user.name,
            'password': TEST_USERS_PASSWORD,
        }
        self.assertRaises(ValueError,
                          ExtUser.objects._create_user,
                          **user_data)

    def test_ok__create_user_without_name(self):
        base_user = self.user_factory.build()
        self.assertFalse(base_user.pk)
        user_data = {
            'email': base_user.email,
            'password': TEST_USERS_PASSWORD,
        }
        ExtUser.objects._create_user(**user_data)
        user = ExtUser.objects.get(email=base_user.email)
        self.assertIsNone(user.name)

    def test_fail__create_user_without_password(self):
        base_user = self.user_factory.build()
        self.assertFalse(base_user.pk)
        user_data = {
            'email': base_user.email,
            'name': base_user.name,
        }
        self.assertRaises(TypeError,
                          ExtUser.objects._create_user,
                          **user_data)

    def test_false__create_user_with_empty_password(self):
        base_user = self.user_factory.build()
        self.assertFalse(base_user.pk)
        user_data = {
            'email': base_user.email,
            'name': base_user.name,
            'password': '',
        }

        user = ExtUser.objects._create_user(**user_data)

        self.assertFalse(user.has_usable_password())

    def test_ok_create_user(self):
        base_user = self.user_factory.build()
        self.assertFalse(base_user.pk)
        user_data = {
            'email': base_user.email,
            'name': base_user.name,
            'password': TEST_USERS_PASSWORD,
        }

        ExtUser.objects.create_user(**user_data)

        user = ExtUser.objects.get(email=base_user.email)
        self.assertTrue(user.pk)
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_false_create_user_with_true_is_admin(self):
        base_user = self.user_factory.build()
        self.assertFalse(base_user.pk)
        user_data = {
            'email': base_user.email,
            'name': base_user.name,
            'password': TEST_USERS_PASSWORD,
            'is_admin': True
        }

        ExtUser.objects.create_user(**user_data)

        user = ExtUser.objects.get(email=base_user.email)
        self.assertTrue(user.pk)
        self.assertFalse(user.is_staff)

    def test_ok_create_superuser(self):
        base_user = self.user_factory.build()
        self.assertFalse(base_user.pk)
        user_data = {
            'email': base_user.email,
            'name': base_user.name,
            'password': TEST_USERS_PASSWORD,
        }

        ExtUser.objects.create_superuser(**user_data)

        user = ExtUser.objects.get(email=base_user.email)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_ok_create_superuser_with_false_is_admin(self):
        base_user = self.user_factory.build()
        self.assertFalse(base_user.pk)
        user_data = {
            'email': base_user.email,
            'name': base_user.name,
            'password': TEST_USERS_PASSWORD,
            'is_admin': False
        }

        ExtUser.objects.create_superuser(**user_data)
        user = ExtUser.objects.get(email=base_user.email)
        self.assertTrue(user.is_staff)
