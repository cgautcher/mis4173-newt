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
            name='AccountRegistration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_status', models.CharField(default=b'GENERIC', max_length=32, choices=[(b'GENERIC', b'Generic user (no special permissions needed)'), (b'SALES', b'Sales user (Can create/comment on Enablement Requests'), (b'ENGSUP', b'Engineering/Support user (Can comment on Enablement Requests')])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
