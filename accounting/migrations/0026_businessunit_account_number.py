# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-20 17:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0025_salary_salary_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessunit',
            name='account_number',
            field=models.CharField(max_length=12),
            preserve_default=False,
        ),
    ]
