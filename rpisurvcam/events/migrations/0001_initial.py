# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-15 14:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Success'), (1, 'Failure'), (2, 'System Error'), (3, 'Info')], default=(0, 'Success'))),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('url', models.URLField(null=True)),
                ('url_text', models.CharField(max_length=50, null=True)),
            ],
            options={
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='EventClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('visible', models.BooleanField(default=True)),
            ],
            options={
                'managed': True,
                'verbose_name_plural': 'Event classes',
            },
        ),
        migrations.AddField(
            model_name='event',
            name='event_class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='events.EventClass'),
        ),
        migrations.AddField(
            model_name='event',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to=settings.AUTH_USER_MODEL),
        ),
    ]
