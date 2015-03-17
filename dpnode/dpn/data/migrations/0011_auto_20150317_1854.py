# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0010_auto_20150304_2018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bag',
            name='brightening',
        ),
        migrations.AddField(
            model_name='bag',
            name='interpretive',
            field=models.ManyToManyField(null=True, blank=True, to='data.Bag', related_name='interpretive_rel_+'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bag',
            name='bag_type',
            field=models.CharField(max_length=1, default='D', choices=[('D', 'Data'), ('R', 'Rights'), ('I', 'Interpretive')]),
            preserve_default=True,
        ),
    ]
