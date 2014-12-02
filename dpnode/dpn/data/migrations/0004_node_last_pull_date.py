# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0003_auto_20141117_2011'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='last_pull_date',
            field=models.DateTimeField(help_text='Date of most recent updated registry entry', null=True, blank=True),
            preserve_default=True,
        ),
    ]
