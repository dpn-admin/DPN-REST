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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20, unique=True)),
                ('api_endpoint', models.URLField(null=True, blank=True)),
                ('ssh_username', models.CharField(max_length=20)),
                ('ssh_pubkey', models.TextField(null=True, blank=True)),
                ('pull_from', models.BooleanField(default=False)),
                ('replicate_to', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('ip', models.IPAddressField()),
                ('port', models.PositiveIntegerField()),
                ('note', models.CharField(null=True, max_length=100, blank=True)),
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
                ('local_id', models.TextField(null=True, max_length=100, blank=True)),
                ('first_node', models.CharField(max_length=20)),
                ('version_number', models.PositiveIntegerField()),
                ('fixity_algorithm', models.CharField(max_length=10)),
                ('fixity_value', models.CharField(max_length=128)),
                ('last_fixity_date', models.DateTimeField()),
                ('creation_date', models.DateTimeField()),
                ('last_modified_date', models.DateTimeField()),
                ('bag_size', models.BigIntegerField()),
                ('object_type', models.CharField(max_length=1, choices=[('D', 'Data'), ('R', 'Rights'), ('B', 'Brightening')], default='D')),
                ('previous_version', models.CharField(null=True, max_length=64, blank=True)),
                ('forward_version', models.CharField(null=True, max_length=64, blank=True)),
                ('first_version', models.CharField(null=True, max_length=64, blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('brightening_objects', models.ManyToManyField(to='data.RegistryEntry', null=True, blank=True, related_name='brightening_objects_rel_+')),
                ('rights_objects', models.ManyToManyField(to='data.RegistryEntry', null=True, blank=True, related_name='rights_objects_rel_+')),
            ],
            options={
                'verbose_name_plural': 'registry entries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('dpn_object_id', models.CharField(max_length=64)),
                ('event_id', models.CharField(null=True, max_length=20, blank=True, unique=True)),
                ('action', models.CharField(max_length=1, choices=[('S', 'Send'), ('R', 'Receive'), ('C', 'Recover')])),
                ('protocol', models.CharField(max_length=1, choices=[('H', 'https'), ('R', 'rsync')])),
                ('link', models.TextField(null=True, blank=True)),
                ('status', models.CharField(max_length=1, choices=[('P', 'Pending'), ('A', 'Accept'), ('R', 'Reject'), ('C', 'Confirmed'), ('V', 'Valid')])),
                ('size', models.BigIntegerField()),
                ('receipt', models.CharField(null=True, max_length=128, blank=True)),
                ('fixity', models.NullBooleanField()),
                ('valid', models.NullBooleanField()),
                ('error', models.TextField(null=True, blank=True)),
                ('node', models.ForeignKey(to='data.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('node', models.ForeignKey(blank=True, to='data.Node', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
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
            field=models.ManyToManyField(to='data.Protocol', null=True, blank=True),
            preserve_default=True,
        ),
    ]
