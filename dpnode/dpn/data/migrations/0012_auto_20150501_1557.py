# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0011_auto_20150317_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replicationtransfer',
            name='status',
            field=models.CharField(default='Requested', choices=[('Requested', 'Requested'), ('Rejected', 'Rejected'), ('Received', 'Received'), ('Confirmed', 'Confirmed'), ('Stored', 'Stored'), ('Cancelled', 'Cancelled')], max_length=10),
            preserve_default=True,
        ),
    ]
