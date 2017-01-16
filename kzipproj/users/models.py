from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models


class UserManager(BaseUserManager):
    def _create_user(self, email, password,
                     is_superuser, is_active, is_admin, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_active=is_active,
                          is_superuser=is_superuser,
                          is_admin=is_admin,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        is_superuser = False
        is_active = False
        is_admin = False
        return self._create_user(email, password, is_superuser, is_active, is_admin,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        is_superuser = True
        is_active = True
        is_admin = True
        return self._create_user(email, password, is_superuser, is_active, is_admin,
                                 **extra_fields)


class ExtUser(AbstractBaseUser, PermissionsMixin):
    # тоже скорее вопрос вкуса, но кодстайл джанго позволяет длинные строки, не надо писать поле на несколько строк
    # специально. В реальности не редкость модели с 10 или 30 полями, представляете сколько вы мотать будете чтобы
    # прочесть только поля такой модели?
    # смотрите код самого джанго - AbstractBaseUser - там так не делают.
    #
    # Я видел что такую схему расположения параметров полей часто испльзуют на просторах интернета,
    # поэтому решил что это удобное офрмление кода( тем более мне оно показалось удобным для чтения)
    # хотел бы дополнительно обсудить на митинге.
    email = models.EmailField(
        'Электронная почта',
        max_length=255,
        unique=True,

    )
    name = models.CharField(
        'Имя',
        max_length=80,
        null=True,
        blank=True
    )
    date_joined = models.DateField(
        'Создан',
        auto_now_add=True,
        editable=False,
    )
    is_active = models.BooleanField(
        'Активен',
        default=False
    )
    is_admin = models.BooleanField(
        'Доступ в админку',
        default=False
    )
    is_superuser = models.BooleanField(
        'Суперпользователь',
        default=False
    )

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_full_name(self):
        full_name = "{} {} {}".format(self.id, self.email, self.name)
        # неиспользуемая переменная. вообще у вас есть места с неиспользуемыми переменными и закомментированным кодом -
        # старайтесь так не делать.
        #
        # хотел возвращать в методе.
        return full_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    # Требуется для админки
    @property
    def is_staff(self):
        return self.is_admin

    def get_short_name(self):
        return self.email

    def __str__(self):
        return "{} {}".format(self.id, self.email)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
