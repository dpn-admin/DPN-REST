# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bag',
            name='ingest_node',
            field=models.ForeignKey(to='data.Node', related_name='ingest_node'),
            preserve_default=True,
        ),
    ]
