# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0016_auto_20150504_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='replicate_from',
            field=models.ManyToManyField(to='data.Node', related_name='reverse_replicate_from', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='node',
            name='replicate_to',
            field=models.ManyToManyField(to='data.Node', related_name='reverse_replicate_to', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='node',
            name='restore_from',
            field=models.ManyToManyField(to='data.Node', related_name='reverse_restore_from', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='node',
            name='restore_to',
            field=models.ManyToManyField(to='data.Node', related_name='reverse_restore_to', null=True, blank=True),
            preserve_default=True,
        ),
    ]
