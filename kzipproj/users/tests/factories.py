import factory

from .constants import *
from ..models import ExtUser
from rest_framework.test import APIRequestFactory


class UserFactoryBase(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'sym{}'.format(n + 1))
    email = factory.LazyAttribute(lambda user: '{}@mail.mail'.format(user.name))
    password = factory.PostGenerationMethodCall('set_password', TEST_USERS_PASSWORD)

    @staticmethod
    def get_test_user_password():
        return 'qweasdzxc'

    class Meta:
        model = ExtUser


class AdminUser(UserFactoryBase):
    is_superuser = True
    is_staff = True
    is_active = True


class ActiveUser(UserFactoryBase):
    is_active = True


class PathAPIRequestFactory(APIRequestFactory):
    """
        Build Requests with fixed url
    """
    def __init__(self, enforce_csrf_checks=False, path=None, **defaults):
        super(PathAPIRequestFactory, self).__init__(**defaults)
        self.path = path

    def get(self, path=None, data=None, **extra):
        path = path or self.path
        return super(PathAPIRequestFactory, self).get(path, data, **extra)

    def post(self, path=None, data=None, format=None, content_type=None, **extra):
            path = path or self.path
            return super(PathAPIRequestFactory, self).post(self, path, data=None, format=None, content_type=None, **extra)
