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
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('timestamp', models.DateTimeField()),
                ('pre_comment_state', models.CharField(blank=True, max_length=3, null=True, choices=[(b'ENR', b'Enablement Review'), (b'SSR', b'Sales Review'), (b'EGR', b'Engineering Review'), (b'SPR', b'Support Review'), (b'AIP', b'Accepted In-progress'), (b'REJ', b'Rejected'), (b'CMP', b'Completed')])),
                ('post_comment_state', models.CharField(blank=True, max_length=3, null=True, choices=[(b'ENR', b'Enablement Review'), (b'SSR', b'Sales Review'), (b'EGR', b'Engineering Review'), (b'SPR', b'Support Review'), (b'AIP', b'Accepted In-progress'), (b'REJ', b'Rejected'), (b'CMP', b'Completed')])),
                ('commenter', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConfigurationDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('os_type', models.CharField(max_length=3, choices=[(b'WNS', b'Windows Server'), (b'HVS', b'Hyper-V Server'), (b'LRH', b'Linux - Redhat'), (b'LSU', b'Linux - SuSE'), (b'LOR', b'Linux - Oracle'), (b'OVM', b'Oracle VM'), (b'VMW', b'VMware vSphere'), (b'SOL', b'Solaris'), (b'AIX', b'AIX'), (b'HPX', b'HP-UX')])),
                ('os_version', models.CharField(max_length=32)),
                ('storage_adapter_vendor', models.CharField(max_length=3, choices=[(b'CSC', b'Cisco'), (b'BRC', b'Brocade'), (b'QLC', b'QLogic'), (b'ELX', b'Emulex'), (b'BDC', b'Broadcom'), (b'INT', b'Intel')])),
                ('storage_adapter_model', models.CharField(max_length=32)),
                ('storage_adapter_driver', models.CharField(max_length=32)),
                ('storage_adapter_firmware', models.CharField(max_length=32)),
                ('data_ontap_version', models.CharField(max_length=32)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnablementRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.SlugField(unique=True, max_length=9, blank=True)),
                ('creation_timestamp', models.DateTimeField(auto_now_add=True)),
                ('current_state', models.CharField(max_length=3, choices=[(b'ENR', b'Enablement Review'), (b'SSR', b'Sales Review'), (b'EGR', b'Engineering Review'), (b'SPR', b'Support Review'), (b'AIP', b'Accepted In-progress'), (b'REJ', b'Rejected'), (b'CMP', b'Completed')])),
                ('customer_name', models.CharField(max_length=100)),
                ('assigned_engineer', models.ForeignKey(related_name='enablement_engineer', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('configuration_details', models.ForeignKey(to='objects.ConfigurationDetails')),
                ('parent_request', models.ForeignKey(to_field=b'identifier', blank=True, to='objects.EnablementRequest', null=True)),
                ('sales_initiator', models.ForeignKey(related_name='sales_representative', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='comment',
            name='enablement_request',
            field=models.ForeignKey(to='objects.EnablementRequest'),
            preserve_default=True,
        ),
    ]
