# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-24 19:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0002_auto_20160224_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='date_payed',
            field=models.DateField(default=None),
        ),
    ]
