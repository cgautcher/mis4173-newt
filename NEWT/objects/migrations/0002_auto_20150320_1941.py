# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='enablementrequest',
            name='slug',
            field=models.SlugField(unique=True, max_length=9, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='enablementrequest',
            name='identifier',
            field=models.CharField(unique=True, max_length=9, blank=True),
            preserve_default=True,
        ),
    ]
