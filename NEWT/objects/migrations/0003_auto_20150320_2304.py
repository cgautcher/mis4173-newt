# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0002_auto_20150320_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configurationdetails',
            name='os_type',
            field=models.CharField(max_length=32, choices=[(b'Windows Server', b'Windows Server'), (b'Hyper-V Server', b'Hyper-V Server'), (b'Linux - Redhat', b'Linux - Redhat'), (b'Linux - SuSE', b'Linux - SuSE'), (b'Linux - Oracle', b'Linux - Oracle'), (b'Oracle VM', b'Oracle VM'), (b'VMware vSphere', b'VMware vSphere'), (b'Solaris', b'Solaris'), (b'AIX', b'AIX'), (b'HP-UX', b'HP-UX')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='configurationdetails',
            name='storage_adapter_vendor',
            field=models.CharField(max_length=32, choices=[(b'Cisco', b'Cisco'), (b'Brocade', b'Brocade'), (b'QLogic', b'QLogic'), (b'Emulex', b'Emulex'), (b'Broadcom', b'Broadcom'), (b'Intel', b'Intel')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='enablementrequest',
            name='current_state',
            field=models.CharField(max_length=32, choices=[(b'Enablement Review', b'Enablement Review'), (b'Sales Review', b'Sales Review'), (b'Engineering Review', b'Engineering Review'), (b'Support Review', b'Support Review'), (b'Accepted In-progress', b'Accepted In-progress'), (b'Rejected', b'Rejected'), (b'Completed', b'Completed')]),
            preserve_default=True,
        ),
    ]
