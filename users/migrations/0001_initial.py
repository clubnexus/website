# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserExt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.IntegerField()),
                ('email_verified', models.BooleanField(default=False)),
                ('email_token', models.CharField(max_length=64)),
                ('banned', models.BooleanField(default=False)),
                ('ban_history', models.CharField(max_length=20480)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
