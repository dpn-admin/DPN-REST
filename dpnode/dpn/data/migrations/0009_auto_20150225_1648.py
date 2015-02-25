# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0008_auto_20150225_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replicationtransfer',
            name='fixity_value',
            field=models.CharField(null=True, max_length=128),
            preserve_default=True,
        ),
    ]
