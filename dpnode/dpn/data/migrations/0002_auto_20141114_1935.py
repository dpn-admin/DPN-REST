# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='registryentry',
            options={'ordering': ['last_modified_date'], 'verbose_name_plural': 'registry entries'},
        ),
        migrations.AddField(
            model_name='transfer',
            name='fixity_type',
            field=models.CharField(choices=[('sha256', 'sha256')], max_length=6, default='sha256'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='node',
            name='created_on',
            field=models.DateTimeField(help_text='Auto updated field of the record creation datetime.', auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='node',
            name='namespace',
            field=models.CharField(help_text='namespace identifier used for references to the node.', unique=True, max_length=20),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='transfer',
            name='status',
            field=models.CharField(choices=[('P', 'Pending'), ('A', 'Accept'), ('R', 'Reject'), ('C', 'Confirm')], max_length=1, default='P'),
            preserve_default=True,
        ),
    ]
