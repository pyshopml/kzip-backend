# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-14 13:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kzip', '0002_auto_20170108_0327'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='publication',
            options={'get_latest_by': 'create_date', 'ordering': ['-create_date'], 'verbose_name': 'Отзыв', 'verbose_name_plural': 'Отзывы'},
        ),
    ]
