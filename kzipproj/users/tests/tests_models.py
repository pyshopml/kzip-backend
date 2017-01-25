from django.core import mail
from django.test import TestCase
from ..models import ExtUser


class ExtUserTestCase(TestCase):
    def setUp(self):
        self.email1, self.name1, self.password1 = 'user1@gmail.com', 'first', 'Q123456789'
        self.user = ExtUser(email=self.email1, name=self.name1, password=self.password1)

    def test_ok_user_get_full_name_method(self):
        self.assertEqual(self.user.get_full_name(), 'user1@gmail.com first')

    def test_ok_user_get_short_name_method(self):
        self.assertEqual(self.user.get_short_name(), self.email1)

    def test_ok_create_user(self):
        ExtUser.objects.create_user(email='user2@gmail.com', name='second', password='qweasdzxc')
        user = ExtUser.objects.get(email='user2@gmail.com')
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password(raw_password='qweasdzxc'))

    def test_ok_create_superuser(self):
        ExtUser.objects.create_superuser(email='user3@gmail.com', name='third', password='qweasdzxc')
        user = ExtUser.objects.get(email='user3@gmail.com')
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password(raw_password='qweasdzxc'))

    def test_ok_send_user_mail(self):
        ExtUser.objects.create(email='user4@gmail.com', name='fourth', password='qweasdzxc')
        user = ExtUser.objects.get(email='user4@gmail.com')
        user.email_user(subject='test134', message='test_body134', from_email='test@ukr.net')
        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(mail.outbox[0].subject, 'test134')
        self.assertEqual(mail.outbox[0].body, 'test_body134')
        self.assertEqual(mail.outbox[0].from_email, 'test@ukr.net')

