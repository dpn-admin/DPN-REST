# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transfer',
            name='status',
            field=models.CharField(default='P', choices=[('P', 'Pending'), ('A', 'Accept'), ('R', 'Reject'), ('C', 'Confirmed')], max_length=1),
        ),
    ]
