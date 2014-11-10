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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Human readable name of the node.', max_length=20, unique=True)),
                ('namespace', models.CharField(help_text='namespace value used to identify the node in important references.', max_length=20, unique=True)),
                ('api_root', models.URLField(null=True, blank=True, help_text='Root url for node api endpoints')),
                ('ssh_username', models.CharField(help_text='Username this node will use for ssh connections to local servers.', max_length=20)),
                ('ssh_pubkey', models.TextField(null=True, blank=True, help_text='SSL public key this node ssh user will use to connect.')),
                ('replicate_from', models.BooleanField(default=False, help_text='Select to enable querying to this node for content to replicate.')),
                ('replicate_to', models.BooleanField(default=False, help_text='Select to include this node as a choice to replicate to.')),
                ('restore_from', models.BooleanField(default=False, help_text='Select to include this node as a choice to restore content from.')),
                ('restore_to', models.BooleanField(default=False, help_text='Select to allow node to request restore from you.')),
                ('me', models.BooleanField(default=False, help_text='Mark if this node is you.')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True, auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.IPAddressField()),
                ('port', models.PositiveIntegerField()),
                ('note', models.CharField(null=True, blank=True, max_length=100)),
                ('node', models.ForeignKey(to='data.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Protocol',
            fields=[
                ('name', models.CharField(serialize=False, max_length=20, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RegistryEntry',
            fields=[
                ('dpn_object_id', models.CharField(serialize=False, max_length=64, primary_key=True)),
                ('local_id', models.TextField(null=True, blank=True, max_length=100)),
                ('version_number', models.PositiveIntegerField(default=1)),
                ('fixity_algorithm', models.CharField(max_length=10)),
                ('fixity_value', models.CharField(max_length=128)),
                ('last_fixity_date', models.DateTimeField()),
                ('creation_date', models.DateTimeField()),
                ('last_modified_date', models.DateTimeField()),
                ('bag_size', models.BigIntegerField()),
                ('object_type', models.CharField(default='D', max_length=1, choices=[('D', 'Data'), ('R', 'Rights'), ('B', 'Brightening')])),
                ('previous_version', models.CharField(null=True, blank=True, max_length=64)),
                ('forward_version', models.CharField(null=True, blank=True, max_length=64)),
                ('first_version', models.CharField(null=True, blank=True, max_length=64)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('published', models.BooleanField(default=False)),
                ('brightening_objects', models.ManyToManyField(null=True, blank=True, to='data.RegistryEntry', related_name='brightening_objects_rel_+')),
                ('first_node', models.ForeignKey(to='data.Node', related_name='first_node')),
                ('replicating_nodes', models.ManyToManyField(related_name='replicating_nodes', to='data.Node')),
                ('rights_objects', models.ManyToManyField(null=True, blank=True, to='data.RegistryEntry', related_name='rights_objects_rel_+')),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('region', models.CharField(max_length=2, choices=[('AL', 'AL'), ('AK', 'AK'), ('AZ', 'AZ'), ('AR', 'AR'), ('CA', 'CA'), ('CO', 'CO'), ('CT', 'CT'), ('DC', 'DC'), ('DE', 'DE'), ('FL', 'FL'), ('GA', 'GA'), ('HI', 'HI'), ('ID', 'ID'), ('IL', 'IL'), ('IN', 'IN'), ('IA', 'IA'), ('KS', 'KS'), ('KY', 'KY'), ('LA', 'LA'), ('ME', 'ME'), ('MD', 'MD'), ('MA', 'MA'), ('MI', 'MI'), ('MN', 'MN'), ('MS', 'MS'), ('MO', 'MO'), ('MT', 'MT'), ('NE', 'NE'), ('NV', 'NV'), ('NH', 'NH'), ('NJ', 'NJ'), ('NM', 'NM'), ('NY', 'NY'), ('NC', 'NC'), ('ND', 'ND'), ('OH', 'OH'), ('OK', 'OK'), ('OR', 'OR'), ('PA', 'PA'), ('RI', 'RI'), ('SC', 'SC'), ('SD', 'SD'), ('TN', 'TN'), ('TX', 'TX'), ('UT', 'UT'), ('VT', 'VT'), ('VA', 'VA'), ('WA', 'WA'), ('WV', 'WV'), ('WI', 'WI'), ('WY', 'WY')])),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_id', models.CharField(null=True, blank=True, max_length=20, unique=True)),
                ('protocol', models.CharField(default='R', max_length=1, choices=[('H', 'https'), ('R', 'rsync')])),
                ('link', models.TextField(null=True, blank=True)),
                ('status', models.CharField(default='P', max_length=1, choices=[('P', 'Pending'), ('A', 'Accept'), ('R', 'Reject'), ('C', 'Confirmed')])),
                ('size', models.BigIntegerField()),
                ('receipt', models.CharField(null=True, blank=True, max_length=128)),
                ('exp_fixity', models.CharField(max_length=128)),
                ('fixity', models.NullBooleanField()),
                ('valid', models.NullBooleanField()),
                ('error', models.TextField(null=True, blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True, auto_now_add=True)),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('node', models.ForeignKey(null=True, blank=True, to='data.Node')),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
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
            field=models.ManyToManyField(null=True, blank=True, to='data.Protocol'),
            preserve_default=True,
        ),
    ]
