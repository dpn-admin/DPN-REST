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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20, unique=True)),
                ('namespace', models.CharField(max_length=20, unique=True)),
                ('api_endpoint', models.URLField(null=True, blank=True)),
                ('ssh_username', models.CharField(max_length=20)),
                ('ssh_pubkey', models.TextField(null=True, blank=True)),
                ('pull_from', models.BooleanField(default=False)),
                ('replicate_to', models.BooleanField(default=False)),
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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('ip', models.IPAddressField()),
                ('port', models.PositiveIntegerField()),
                ('note', models.CharField(max_length=100, null=True, blank=True)),
                ('node', models.ForeignKey(to='data.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Protocol',
            fields=[
                ('name', models.CharField(max_length=20, primary_key=True, serialize=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RegistryEntry',
            fields=[
                ('dpn_object_id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('local_id', models.TextField(max_length=100, null=True, blank=True)),
                ('version_number', models.PositiveIntegerField(default=1)),
                ('fixity_algorithm', models.CharField(max_length=10)),
                ('fixity_value', models.CharField(max_length=128)),
                ('last_fixity_date', models.DateTimeField()),
                ('creation_date', models.DateTimeField()),
                ('last_modified_date', models.DateTimeField()),
                ('bag_size', models.BigIntegerField()),
                ('object_type', models.CharField(default='D', max_length=1, choices=[('D', 'Data'), ('R', 'Rights'), ('B', 'Brightening')])),
                ('previous_version', models.CharField(max_length=64, null=True, blank=True)),
                ('forward_version', models.CharField(max_length=64, null=True, blank=True)),
                ('first_version', models.CharField(max_length=64, null=True, blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('published', models.BooleanField(default=False)),
                ('brightening_objects', models.ManyToManyField(related_name='brightening_objects_rel_+', to='data.RegistryEntry', null=True, blank=True)),
                ('first_node', models.ForeignKey(to='data.Node')),
                ('rights_objects', models.ManyToManyField(related_name='rights_objects_rel_+', to='data.RegistryEntry', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'registry entries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('dpn_object_id', models.CharField(max_length=64)),
                ('event_id', models.CharField(max_length=20, null=True, unique=True, blank=True)),
                ('protocol', models.CharField(choices=[('H', 'https'), ('R', 'rsync')], max_length=1)),
                ('link', models.TextField(null=True, blank=True)),
                ('status', models.CharField(choices=[('P', 'Pending'), ('A', 'Accept'), ('R', 'Reject'), ('C', 'Confirmed')], max_length=1)),
                ('size', models.BigIntegerField()),
                ('receipt', models.CharField(max_length=128, null=True, blank=True)),
                ('exp_fixity', models.CharField(max_length=128)),
                ('fixity', models.NullBooleanField()),
                ('valid', models.NullBooleanField()),
                ('error', models.TextField(null=True, blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('node', models.ForeignKey(to='data.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('node', models.ForeignKey(to='data.Node', null=True, blank=True)),
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
