# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountregistration',
            name='group_status',
            field=models.CharField(default=b'GENERIC', max_length=32, choices=[(b'GENERIC', b'Generic user (no special permissions needed)'), (b'SALES', b'Sales user (Can create/comment on Enablement Requests)'), (b'ENGSUP', b'Engineering/Support user (Can comment on Enablement Requests)')]),
            preserve_default=True,
        ),
    ]
