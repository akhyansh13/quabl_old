# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SimplerApp', '0007_auto_20141024_2055'),
    ]

    operations = [
        migrations.AddField(
            model_name='reqbyuser',
            name='frequency',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
