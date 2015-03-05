# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TTEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_type', models.CharField(max_length=60)),
                ('event_date', models.DateTimeField()),
                ('event_account', models.IntegerField()),
                ('event_desc_pub', models.CharField(max_length=500)),
                ('event_desc_priv', models.CharField(max_length=500)),
                ('event_ip_pub', models.CharField(max_length=40)),
                ('event_ip_priv', models.CharField(max_length=40)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
