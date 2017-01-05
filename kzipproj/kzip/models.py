from django.db import models
from django.conf import settings


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        # default=ExtUser.objects.get(login='anonymous'),
    )
    title = models.CharField(
        'Название',
        max_length=255,
    )
    comment = models.TextField(
        'Отзыв',
    )
    create_date = models.DateTimeField(
        'Создан',
        auto_now_add=True
    )

    def __str__(self):
        object_name = "{}-{}-{}".format(self.create_date, self.user.email, self.title)
        return object_name

    def get_user(self):
        user = "{}".format(self.user.email)
        return user

    class Meta:
        ordering = ["-create_date", "user"]
        get_latest_by = "create_date"
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
