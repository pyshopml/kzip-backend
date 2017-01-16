from django.db import models
from django.conf import settings


class Publication(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь')
    title = models.CharField('Название', max_length=255)
    text = models.TextField('Отзыв')
    create_date = models.DateTimeField('Создан', auto_now_add=True)

    def __str__(self):
        object_name = "{}-{}-{}".format(self.create_date, self.user.email, self.title)
        return object_name

    class Meta:
        ordering = ["-create_date"]
        get_latest_by = "create_date"
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
