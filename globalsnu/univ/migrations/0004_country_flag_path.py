# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-25 15:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('univ', '0003_auto_20160802_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='flag_path',
            field=models.FilePathField(blank=True, path='/srv/static/img/flags'),
        ),
    ]
