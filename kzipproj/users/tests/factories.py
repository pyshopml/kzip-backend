import factory

from .constants import *
from ..models import ExtUser


class UserFactoryBase(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'sym{}'.format(n + 1))
    email = factory.LazyAttribute(lambda user: '{}@mail.mail'.format(user.name))
    password = factory.PostGenerationMethodCall('set_password', TEST_USERS_PASSWORD)

    class Meta:
        model = ExtUser


class AdminUser(UserFactoryBase):
    is_superuser = True
    is_staff = True
    is_active = True


class ActiveUser(UserFactoryBase):
    is_active = True
