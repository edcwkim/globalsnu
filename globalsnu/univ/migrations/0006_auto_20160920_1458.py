# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-20 05:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('univ', '0005_auto_20160914_0101'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='country',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='school',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='school',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
