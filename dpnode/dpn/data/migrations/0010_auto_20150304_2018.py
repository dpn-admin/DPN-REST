# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0009_auto_20150225_1648'),
    ]

    operations = [
        migrations.CreateModel(
            name='FixityAlgorithm',
            fields=[
                ('name', models.CharField(primary_key=True, serialize=False, max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='node',
            name='fixity_algorithms',
            field=models.ManyToManyField(blank=True, to='data.FixityAlgorithm', null=True, related_name='+'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fixity',
            name='algorithm',
            field=models.ForeignKey(to='data.FixityAlgorithm'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='replicationtransfer',
            name='fixity_algorithm',
            field=models.ForeignKey(to='data.FixityAlgorithm', related_name='+'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='replicationtransfer',
            name='fixity_nonce',
            field=models.CharField(blank=True, null=True, max_length=128),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='replicationtransfer',
            name='fixity_value',
            field=models.CharField(blank=True, null=True, max_length=128),
            preserve_default=True,
        ),
    ]
