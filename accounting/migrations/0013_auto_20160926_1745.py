# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-26 21:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0012_auto_20160919_1420'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='date_paid',
            field=models.DateField(blank=True, default=None, null=True, verbose_name=b'Date Paid'),
        ),
        migrations.AlterField(
            model_name='income',
            name='date_paid',
            field=models.DateField(blank=True, default=None, null=True, verbose_name=b'Date Paid'),
        ),
    ]
