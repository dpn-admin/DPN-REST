# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0012_auto_20150501_1557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bag',
            name='updated_at',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='node',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='replicationtransfer',
            name='updated_at',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='restoretransfer',
            name='updated_at',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
    ]
