# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_ttevent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ttevent',
            name='event_desc_priv',
            field=models.TextField(max_length=500),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ttevent',
            name='event_desc_pub',
            field=models.TextField(max_length=500),
            preserve_default=True,
        ),
    ]
