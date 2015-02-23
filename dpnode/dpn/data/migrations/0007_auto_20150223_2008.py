# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0006_auto_20150223_2007'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='node',
            name='replicate_from_node',
        ),
        migrations.RemoveField(
            model_name='node',
            name='replicate_to_node',
        ),
        migrations.RemoveField(
            model_name='node',
            name='restore_from_node',
        ),
        migrations.RemoveField(
            model_name='node',
            name='restore_to_node',
        ),
        migrations.AddField(
            model_name='node',
            name='replicate_from',
            field=models.ManyToManyField(to='data.Node', null=True, blank=True, related_name='replicate_from_rel_+'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='replicate_to',
            field=models.ManyToManyField(to='data.Node', null=True, blank=True, related_name='replicate_to_rel_+'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='restore_from',
            field=models.ManyToManyField(to='data.Node', null=True, blank=True, related_name='restore_from_rel_+'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='restore_to',
            field=models.ManyToManyField(to='data.Node', null=True, blank=True, related_name='restore_to_rel_+'),
            preserve_default=True,
        ),
    ]
