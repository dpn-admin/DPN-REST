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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=20)),
                ('api_endpoint', models.URLField(blank=True, null=True)),
                ('ssh_username', models.CharField(max_length=20)),
                ('ssh_pubkey', models.TextField(blank=True, null=True)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('ip', models.IPAddressField()),
                ('port', models.PositiveIntegerField()),
                ('note', models.CharField(blank=True, null=True, max_length=100)),
                ('node', models.ForeignKey(to='dpn_data.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Protocol',
            fields=[
                ('name', models.CharField(primary_key=True, serialize=False, max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RegistryEntry',
            fields=[
                ('dpn_object_id', models.CharField(primary_key=True, serialize=False, max_length=64)),
                ('local_id', models.TextField(blank=True, null=True, max_length=100)),
                ('first_node', models.CharField(max_length=20)),
                ('version_number', models.PositiveIntegerField()),
                ('fixity_algorithm', models.CharField(max_length=10)),
                ('fixity_value', models.CharField(max_length=128)),
                ('last_fixity_date', models.DateTimeField()),
                ('creation_date', models.DateTimeField()),
                ('last_modified_date', models.DateTimeField()),
                ('bag_size', models.BigIntegerField()),
                ('object_type', models.CharField(default='D', choices=[('D', 'Data'), ('R', 'Rights'), ('B', 'Brightening')], max_length=1)),
                ('previous_version', models.CharField(blank=True, null=True, max_length=64)),
                ('forward_version', models.CharField(blank=True, null=True, max_length=64)),
                ('first_version', models.CharField(blank=True, null=True, max_length=64)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now_add=True, auto_now=True)),
                ('brightening_objects', models.ManyToManyField(blank=True, to='dpn_data.RegistryEntry', null=True, related_name='brightening_objects_rel_+')),
                ('rights_objects', models.ManyToManyField(blank=True, to='dpn_data.RegistryEntry', null=True, related_name='rights_objects_rel_+')),
            ],
            options={
                'verbose_name_plural': 'registry entries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('region', models.CharField(choices=[('AL', 'AL'), ('AK', 'AK'), ('AZ', 'AZ'), ('AR', 'AR'), ('CA', 'CA'), ('CO', 'CO'), ('CT', 'CT'), ('DC', 'DC'), ('DE', 'DE'), ('FL', 'FL'), ('GA', 'GA'), ('HI', 'HI'), ('ID', 'ID'), ('IL', 'IL'), ('IN', 'IN'), ('IA', 'IA'), ('KS', 'KS'), ('KY', 'KY'), ('LA', 'LA'), ('ME', 'ME'), ('MD', 'MD'), ('MA', 'MA'), ('MI', 'MI'), ('MN', 'MN'), ('MS', 'MS'), ('MO', 'MO'), ('MT', 'MT'), ('NE', 'NE'), ('NV', 'NV'), ('NH', 'NH'), ('NJ', 'NJ'), ('NM', 'NM'), ('NY', 'NY'), ('NC', 'NC'), ('ND', 'ND'), ('OH', 'OH'), ('OK', 'OK'), ('OR', 'OR'), ('PA', 'PA'), ('RI', 'RI'), ('SC', 'SC'), ('SD', 'SD'), ('TN', 'TN'), ('TX', 'TX'), ('UT', 'UT'), ('VT', 'VT'), ('VA', 'VA'), ('WA', 'WA'), ('WV', 'WV'), ('WI', 'WI'), ('WY', 'WY')], max_length=2)),
                ('type', models.CharField(max_length=50)),
                ('node', models.ForeignKey(to='dpn_data.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('dpn_object_id', models.CharField(max_length=64)),
                ('event_id', models.CharField(blank=True, unique=True, null=True, max_length=20)),
                ('action', models.CharField(choices=[('I', 'Send'), ('R', 'Receive'), ('C', 'Recover')], max_length=1)),
                ('protocol', models.CharField(choices=[('H', 'https'), ('R', 'rsync')], max_length=1)),
                ('link', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('P', 'Pending'), ('A', 'Accept'), ('R', 'Reject'), ('C', 'Confirmed'), ('V', 'Valid')], max_length=1)),
                ('size', models.BigIntegerField()),
                ('receipt', models.CharField(blank=True, null=True, max_length=128)),
                ('fixity', models.NullBooleanField()),
                ('valid', models.NullBooleanField()),
                ('error', models.TextField(blank=True, null=True)),
                ('node', models.ForeignKey(to='dpn_data.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('node', models.ForeignKey(blank=True, to='dpn_data.Node', null=True)),
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
            field=models.ManyToManyField(blank=True, to='dpn_data.Protocol', null=True),
            preserve_default=True,
        ),
    ]
