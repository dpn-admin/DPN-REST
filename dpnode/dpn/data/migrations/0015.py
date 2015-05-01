# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0014_auto_20150501_1833'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bag',
            old_name='original_node',
            new_name='ingest_node',
        ),
    ]
