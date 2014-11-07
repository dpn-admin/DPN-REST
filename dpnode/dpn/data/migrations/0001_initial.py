# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=20, help_text='Human readable name of the node.')),
                ('namespace', models.CharField(unique=True, max_length=20, help_text='namespace value used to identify the node in important references.')),
                ('api_root', models.URLField(blank=True, null=True, help_text='Root url for node api endpoints')),
                ('ssh_username', models.CharField(max_length=20, help_text='Username this node will use for ssh connections to local servers.')),
                ('ssh_pubkey', models.TextField(blank=True, null=True, help_text='SSL public key this node ssh user will use to connect.')),
                ('replicate_from', models.BooleanField(help_text='Select to enable querying to this node for content to replicate.', default=False)),
                ('replicate_to', models.BooleanField(help_text='Select to include this node as a choice to replicate to.', default=False)),
                ('restore_from', models.BooleanField(help_text='Select to include this node as a choice to restore content from.', default=False)),
                ('restore_to', models.BooleanField(help_text='Select to allow node to request restore from you.', default=False)),
                ('me', models.BooleanField(help_text='Mark if this node is you.', default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now_add=True, auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.IPAddressField()),
                ('port', models.PositiveIntegerField()),
                ('note', models.CharField(blank=True, null=True, max_length=100)),
                ('node', models.ForeignKey(to='data.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Protocol',
            fields=[
                ('name', models.CharField(serialize=False, primary_key=True, max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RegistryEntry',
            fields=[
                ('dpn_object_id', models.CharField(serialize=False, primary_key=True, max_length=64)),
                ('local_id', models.TextField(blank=True, null=True, max_length=100)),
                ('version_number', models.PositiveIntegerField(default=1)),
                ('fixity_algorithm', models.CharField(max_length=10)),
                ('fixity_value', models.CharField(max_length=128)),
                ('last_fixity_date', models.DateTimeField()),
                ('creation_date', models.DateTimeField()),
                ('last_modified_date', models.DateTimeField()),
                ('bag_size', models.BigIntegerField()),
                ('object_type', models.CharField(choices=[('D', 'Data'), ('R', 'Rights'), ('B', 'Brightening')], default='D', max_length=1)),
                ('previous_version', models.CharField(blank=True, null=True, max_length=64)),
                ('forward_version', models.CharField(blank=True, null=True, max_length=64)),
                ('first_version', models.CharField(blank=True, null=True, max_length=64)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now_add=True, auto_now=True)),
                ('published', models.BooleanField(default=False)),
                ('brightening_objects', models.ManyToManyField(blank=True, null=True, to='data.RegistryEntry', related_name='brightening_objects_rel_+')),
                ('first_node', models.ForeignKey(related_name='first_node', to='data.Node')),
                ('replicating_nodes', models.ManyToManyField(related_name='replicating_nodes', to='data.Node')),
                ('rights_objects', models.ManyToManyField(blank=True, null=True, to='data.RegistryEntry', related_name='rights_objects_rel_+')),
            ],
            options={
                'verbose_name_plural': 'registry entries',
                'ordering': ['-updated_on'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(choices=[('AL', 'AL'), ('AK', 'AK'), ('AZ', 'AZ'), ('AR', 'AR'), ('CA', 'CA'), ('CO', 'CO'), ('CT', 'CT'), ('DC', 'DC'), ('DE', 'DE'), ('FL', 'FL'), ('GA', 'GA'), ('HI', 'HI'), ('ID', 'ID'), ('IL', 'IL'), ('IN', 'IN'), ('IA', 'IA'), ('KS', 'KS'), ('KY', 'KY'), ('LA', 'LA'), ('ME', 'ME'), ('MD', 'MD'), ('MA', 'MA'), ('MI', 'MI'), ('MN', 'MN'), ('MS', 'MS'), ('MO', 'MO'), ('MT', 'MT'), ('NE', 'NE'), ('NV', 'NV'), ('NH', 'NH'), ('NJ', 'NJ'), ('NM', 'NM'), ('NY', 'NY'), ('NC', 'NC'), ('ND', 'ND'), ('OH', 'OH'), ('OK', 'OK'), ('OR', 'OR'), ('PA', 'PA'), ('RI', 'RI'), ('SC', 'SC'), ('SD', 'SD'), ('TN', 'TN'), ('TX', 'TX'), ('UT', 'UT'), ('VT', 'VT'), ('VA', 'VA'), ('WA', 'WA'), ('WV', 'WV'), ('WI', 'WI'), ('WY', 'WY')], max_length=2)),
                ('type', models.CharField(max_length=50)),
                ('node', models.ForeignKey(to='data.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.CharField(blank=True, null=True, max_length=20, unique=True)),
                ('protocol', models.CharField(choices=[('H', 'https'), ('R', 'rsync')], default='R', max_length=1)),
                ('link', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('P', 'Pending'), ('A', 'Accept'), ('R', 'Reject'), ('C', 'Confirmed')], default='P', max_length=1)),
                ('size', models.BigIntegerField()),
                ('receipt', models.CharField(blank=True, null=True, max_length=128)),
                ('exp_fixity', models.CharField(max_length=128)),
                ('fixity', models.NullBooleanField()),
                ('valid', models.NullBooleanField()),
                ('error', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now_add=True, auto_now=True)),
                ('node', models.ForeignKey(to='data.Node')),
                ('registry_entry', models.ForeignKey(to='data.RegistryEntry')),
            ],
            options={
                'ordering': ['-created_on'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('node', models.ForeignKey(null=True, to='data.Node', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='profile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='storage',
            unique_together=set([('node', 'region')]),
        ),
        migrations.AlterUniqueTogether(
            name='port',
            unique_together=set([('node', 'ip', 'port')]),
        ),
        migrations.AddField(
            model_name='node',
            name='protocols',
            field=models.ManyToManyField(blank=True, null=True, to='data.Protocol'),
            preserve_default=True,
        ),
    ]
