# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0005_remove_node_me'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bag',
            fields=[
                ('uuid', models.CharField(max_length=64, serialize=False, primary_key=True)),
                ('local_id', models.TextField(max_length=100, null=True, blank=True)),
                ('size', models.BigIntegerField()),
                ('first_version_uuid', models.CharField(max_length=64, null=True, blank=True)),
                ('version', models.PositiveIntegerField(default=1)),
                ('bag_type', models.CharField(choices=[('D', 'Data'), ('R', 'Rights'), ('B', 'Brightening')], default='D', max_length=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('admin_node', models.ForeignKey(related_name='admin_node', to='data.Node', help_text='The current admin_node for this bag.')),
                ('brightening', models.ManyToManyField(to='data.Bag', related_name='brightening_rel_+', null=True, blank=True)),
                ('original_node', models.ForeignKey(related_name='original_node', to='data.Node')),
                ('replicating_nodes', models.ManyToManyField(to='data.Node', related_name='replicating_nodes', help_text='Nodes that have confirmed successful transfers.')),
                ('rights', models.ManyToManyField(to='data.Bag', related_name='rights_rel_+', null=True, blank=True)),
            ],
            options={
                'ordering': ['-updated_at'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Fixity',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('algorithm', models.CharField(choices=[('sha256', 'sha256')], max_length=10)),
                ('digest', models.CharField(max_length=128)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('bag', models.ForeignKey(related_name='fixity', to='data.Bag')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReplicationTransfer',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('replication_id', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('fixity_algorithm', models.CharField(choices=[('sha256', 'sha256')], default='sha256', max_length=6)),
                ('fixity_nonce', models.CharField(max_length=128, null=True)),
                ('fixity_value', models.CharField(max_length=128)),
                ('fixity_accept', models.NullBooleanField()),
                ('bag_valid', models.NullBooleanField()),
                ('status', models.CharField(choices=[('Requested', 'Requested'), ('Rejected', 'Rejected'), ('Received', 'Received'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')], default='Requested', max_length=10)),
                ('protocol', models.CharField(choices=[('H', 'https'), ('R', 'rsync')], default='R', max_length=1)),
                ('link', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('bag', models.ForeignKey(related_name='replication_transfers', to='data.Bag')),
                ('from_node', models.ForeignKey(related_name='transfers_out', to='data.Node')),
                ('to_node', models.ForeignKey(related_name='transfers_in', to='data.Node')),
            ],
            options={
                'ordering': ['-created_at'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RestoreTransfer',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('restore_id', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('status', models.CharField(choices=[('Requested', 'Requested'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected'), ('Prepared', 'Prepared'), ('Finished', 'Finished'), ('Cancelled', 'Cancelled')], default='Requested', max_length=10)),
                ('protocol', models.CharField(choices=[('H', 'https'), ('R', 'rsync')], default='R', max_length=1)),
                ('link', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('bag', models.ForeignKey(to='data.Bag')),
                ('from_node', models.ForeignKey(related_name='restorations_requested', to='data.Node')),
                ('to_node', models.ForeignKey(related_name='restorations_performed', to='data.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='port',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='port',
            name='node',
        ),
        migrations.DeleteModel(
            name='Port',
        ),
        migrations.RemoveField(
            model_name='registryentry',
            name='brightening_objects',
        ),
        migrations.RemoveField(
            model_name='registryentry',
            name='first_node',
        ),
        migrations.RemoveField(
            model_name='registryentry',
            name='replicating_nodes',
        ),
        migrations.RemoveField(
            model_name='registryentry',
            name='rights_objects',
        ),
        migrations.RemoveField(
            model_name='transfer',
            name='node',
        ),
        migrations.RemoveField(
            model_name='transfer',
            name='registry_entry',
        ),
        migrations.DeleteModel(
            name='RegistryEntry',
        ),
        migrations.DeleteModel(
            name='Transfer',
        ),
        migrations.RenameField(
            model_name='node',
            old_name='updated_on',
            new_name='updated_at',
        ),
        migrations.RenameField(
            model_name='storage',
            old_name='type',
            new_name='storage_type',
        ),
        migrations.RemoveField(
            model_name='node',
            name='created_on',
        ),
        migrations.RemoveField(
            model_name='node',
            name='replicate_from',
        ),
        migrations.RemoveField(
            model_name='node',
            name='replicate_to',
        ),
        migrations.RemoveField(
            model_name='node',
            name='restore_from',
        ),
        migrations.RemoveField(
            model_name='node',
            name='restore_to',
        ),
        migrations.AddField(
            model_name='node',
            name='created_at',
            field=models.DateTimeField(default='2015-02-23T00:00:00Z', auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='node',
            name='replicate_from_node',
            field=models.ManyToManyField(to='data.Node', related_name='replicate_from_node_rel_+', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='replicate_to_node',
            field=models.ManyToManyField(to='data.Node', related_name='replicate_to_node_rel_+', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='restore_from_node',
            field=models.ManyToManyField(to='data.Node', related_name='restore_from_node_rel_+', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='restore_to_node',
            field=models.ManyToManyField(to='data.Node', related_name='restore_to_node_rel_+', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='node',
            name='api_root',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='node',
            name='last_pull_date',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='node',
            name='name',
            field=models.CharField(max_length=20, unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='node',
            name='namespace',
            field=models.CharField(max_length=20, unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='node',
            name='protocols',
            field=models.ManyToManyField(to='data.Protocol', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='node',
            name='ssh_pubkey',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='node',
            name='ssh_username',
            field=models.CharField(max_length=20),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='storage',
            name='node',
            field=models.ForeignKey(related_name='storage', to='data.Node'),
            preserve_default=True,
        ),
    ]
