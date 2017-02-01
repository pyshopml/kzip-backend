from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from ..models import ExtUser

from .factories import UserFactoryBase, PathAPIRequestFactory, ActiveUser
from .. import consts
from ..utils.emails import UserActivationEmail
from ..views import ActivationView
from ..utils import utils


class ActivationViewTestCase(TestCase):
    """
    Testing ActivationView
    tests through method get test common cases of ActivationView
    """

    def setUp(self):
        self.request_factory = PathAPIRequestFactory(path='/')
        self.user_factory = UserFactoryBase
        self.active_user_factory = ActiveUser
        self.TEST_USERS_PASSWORD = UserFactoryBase.get_test_user_password()
        self.activation_email_factory = UserActivationEmail
        self.activation_view = ActivationView.as_view()

    def test_ok_activate_user_via_url_method_get(self):
        """
        Test full logic from request (use activate url from activate_mail_factory),
        through urlconf, to response.
        Check successful user activation(property is_active)
        """
        user = UserFactoryBase.create()
        created_user_id = user.pk
        self.assertFalse(user.is_active)

        creation_request = self.request_factory.post(data={'email': user.email,
                                                           'password': self.TEST_USERS_PASSWORD,
                                                           })
        email = self.activation_email_factory.build(creation_request, user)
        url = email.get_context().get('url')
        response = self.client.get('/{}'.format(url))
        self.assertEquals(response.status_code, 202)
        self.assertEqual(response.data['detail'], consts.ACTIVATION_SUCCESS)

        activated_user = ExtUser.objects.get(email=user.email)
        self.assertEqual(created_user_id, activated_user.pk)
        self.assertTrue(activated_user.is_active)

    def test_fail_activate_already_active_user_method_get(self):
        """
        Try activate already active user by means of django.test.client
        request(use activate url from activate_mail_factory)
        """
        user = ActiveUser.create()
        self.assertTrue(user.is_active)
        creation_request = self.request_factory.post(data={'email': user.email,
                                                           'password': self.TEST_USERS_PASSWORD,
                                                           })
        email = self.activation_email_factory.build(creation_request, user)
        url = email.get_context().get('url')
        response = self.client.get('/{}'.format(url))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], consts.STALE_TOKEN)

    def test_fail_activate_user_with_bad_uid(self):
        """
        Test ActivationView directly with not correct user UID
        check status code, error message.
        check poperty is_active=false
        """
        user = UserFactoryBase.create()
        self.assertFalse(user.is_active)
        badUID = utils.encode_uid(user.pk + 1)
        token = default_token_generator.make_token(user)
        request = self.request_factory.get(data={'uid': badUID,
                                                 'token': token,
                                                 })
        response = self.activation_view(request)
        not_activated_user = ExtUser.objects.get(email=user.email)
        self.assertFalse(not_activated_user.is_active)
        self.assertEqual(response.status_code, 400)
        self.assertIn(consts.INVALID_UID, response.data['uid'])

    def test_fail_activate_user_with_fail_token(self):
        """
        Test ActivationView directly with fail token
        check status code, error message.
        check poperty is_active=false

        """
        user = UserFactoryBase.create()
        self.assertFalse(user.is_active)
        UID = utils.encode_uid(user.pk)
        fail_token = default_token_generator.make_token(user) + str(1)
        request = self.request_factory.get(data={'uid': UID,
                                                 'token': fail_token,
                                                 })
        response = self.activation_view(request)
        not_activated_user = ExtUser.objects.get(email=user.email)
        self.assertFalse(not_activated_user.is_active)
        self.assertEqual(response.status_code, 400)
        self.assertIn(consts.INVALID_TOKEN, response.data['non_field_errors'])

    def test_fail_activate_already_active_user_method_post(self):
        """
        Test full logic from request (use activate url from activate_mail_factory),
        through urlconf, to response.
        Check successful user activation(property is_active)
        """
        created_user = UserFactoryBase.create()
        self.assertFalse(created_user.is_active)
        UID = utils.encode_uid(created_user.pk)
        token = default_token_generator.make_token(created_user)
        url = 'auth/account/activate/?uid={uid}&token={token}'
        response = self.client.post('/{}'.format(url), data={'uid': UID,
                                                             'token': token})
        self.assertEquals(response.status_code, 202)
        self.assertEqual(response.data['detail'], consts.ACTIVATION_SUCCESS)

        activated_user = ExtUser.objects.get(email=created_user.email)
        self.assertEqual(created_user.id, activated_user.pk)
        self.assertTrue(activated_user.is_active)
