# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-07 12:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_', '0002_auto_20160711_1628'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='changed_nickname',
            field=models.BooleanField(default=False, verbose_name='has changed nickname'),
        ),
    ]