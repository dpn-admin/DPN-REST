# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_auto_20150223_2008'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fixity',
            options={'ordering': ['created_at']},
        ),
        migrations.AlterField(
            model_name='bag',
            name='admin_node',
            field=models.ForeignKey(related_name='administered_bags', help_text='The current admin_node for this bag.', to='data.Node'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bag',
            name='replicating_nodes',
            field=models.ManyToManyField(related_name='replicated_bags', help_text='Nodes that have confirmed successful transfers.', to='data.Node'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fixity',
            name='bag',
            field=models.ForeignKey(related_name='fixities', to='data.Bag'),
            preserve_default=True,
        ),
    ]
