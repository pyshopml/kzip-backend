from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
            Common users creation
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        password = password or None
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', False)
        extra_fields['is_admin'] = False
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields['is_admin'] = True

        return self._create_user(email, password, **extra_fields)


class ExtUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('Электронная почта', max_length=255, unique=True)
    name = models.CharField('Имя', max_length=80, null=True, blank=True)
    date_joined = models.DateField('Создан', auto_now_add=True, editable=False)
    is_active = models.BooleanField('Активен', default=False)
    is_admin = models.BooleanField('Доступ в админку', default=False)
    is_superuser = models.BooleanField('Суперпользователь', default=False)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_full_name(self):
        full_name = "{} {}".format(self.email, self.name)
        return full_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        """
            admin site required
            :return: user is admin or not
        """
        return self.is_admin

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
