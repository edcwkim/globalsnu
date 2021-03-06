# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-07 18:50
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0006_auto_20161015_1449'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='page',
            options={},
        ),
        migrations.RemoveField(
            model_name='essay',
            name='page_title_for_url',
        ),
        migrations.AddField(
            model_name='essay',
            name='creator_email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='creator email'),
        ),
        migrations.AddField(
            model_name='pagerevision',
            name='editor_email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='editor email'),
        ),
        migrations.AlterField(
            model_name='essay',
            name='archived',
            field=models.BooleanField(default=False, verbose_name='archived'),
        ),
        migrations.AlterField(
            model_name='essay',
            name='content',
            field=models.TextField(max_length=1000000, verbose_name='content'),
        ),
        migrations.AlterField(
            model_name='essay',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created time'),
        ),
        migrations.AlterField(
            model_name='essay',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_essays', to=settings.AUTH_USER_MODEL, verbose_name='creator'),
        ),
        migrations.AlterField(
            model_name='essay',
            name='creator_name',
            field=models.CharField(blank=True, max_length=30, verbose_name='creator name'),
        ),
        migrations.AlterField(
            model_name='essay',
            name='edited',
            field=models.DateTimeField(auto_now=True, verbose_name='edited time'),
        ),
        migrations.AlterField(
            model_name='essay',
            name='likers',
            field=models.ManyToManyField(related_name='liked_essays', to=settings.AUTH_USER_MODEL, verbose_name='users who liked'),
        ),
        migrations.AlterField(
            model_name='essay',
            name='page',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='essays', to='wiki.Page', verbose_name='page'),
        ),
        migrations.AlterField(
            model_name='essay',
            name='title',
            field=models.CharField(max_length=100, verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='external',
            name='page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='externals', to='wiki.Page', verbose_name='page'),
        ),
        migrations.AlterField(
            model_name='external',
            name='preview',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='external',
            name='source',
            field=models.CharField(choices=[('WP', 'Wikipedia'), ('NW', 'Namu Wiki')], max_length=2, verbose_name='source'),
        ),
        migrations.AlterField(
            model_name='external',
            name='url',
            field=models.URLField(verbose_name='URL'),
        ),
        migrations.AlterField(
            model_name='page',
            name='archived',
            field=models.BooleanField(default=False, verbose_name='archived'),
        ),
        migrations.AlterField(
            model_name='page',
            name='current_revision',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wiki.PageRevision', verbose_name='current revision'),
        ),
        migrations.AlterField(
            model_name='page',
            name='title_for_url',
            field=models.CharField(max_length=150, verbose_name='title for URL'),
        ),
        migrations.AlterField(
            model_name='page',
            name='wiki',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='pages', to='wiki.Wiki', verbose_name='wiki'),
        ),
        migrations.AlterField(
            model_name='pagerevision',
            name='content',
            field=models.TextField(blank=True, max_length=65535, verbose_name='content'),
        ),
        migrations.AlterField(
            model_name='pagerevision',
            name='edit_summary',
            field=models.CharField(max_length=255, verbose_name='edit summary'),
        ),
        migrations.AlterField(
            model_name='pagerevision',
            name='edited',
            field=models.DateTimeField(auto_now_add=True, verbose_name='edited time'),
        ),
        migrations.AlterField(
            model_name='pagerevision',
            name='editor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='edited_revisions', to=settings.AUTH_USER_MODEL, verbose_name='editor'),
        ),
        migrations.AlterField(
            model_name='pagerevision',
            name='editor_name',
            field=models.CharField(blank=True, max_length=30, verbose_name='editor name'),
        ),
        migrations.AlterField(
            model_name='pagerevision',
            name='page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revisions', to='wiki.Page', verbose_name='page'),
        ),
        migrations.AlterField(
            model_name='pagerevision',
            name='previous_revision',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='next_revision', to='wiki.PageRevision', verbose_name='previous revision'),
        ),
        migrations.AlterField(
            model_name='pagerevision',
            name='revision_number',
            field=models.PositiveSmallIntegerField(editable=False, verbose_name='revision_number'),
        ),
        migrations.AlterField(
            model_name='pagerevision',
            name='title',
            field=models.CharField(max_length=100, validators=[django.core.validators.RegexValidator(re.compile('^[^_/]+\\Z', 32), "The title cannot contain '_' or '/'.")], verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='wiki',
            name='lang',
            field=models.CharField(choices=[('ko', 'Korean'), ('en', 'English')], max_length=5, unique=True, verbose_name='language code'),
        ),
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('wiki', 'subid'), ('wiki', 'title_for_url')]),
        ),
        migrations.AlterIndexTogether(
            name='page',
            index_together=set([('wiki', 'subid'), ('wiki', 'title_for_url')]),
        ),
    ]
