# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0004_node_last_pull_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='node',
            name='me',
        ),
    ]
