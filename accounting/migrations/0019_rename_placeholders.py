# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-14 18:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0018_delete_old_models'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CashPH',
            new_name='Cash',
        ),
        migrations.RenameModel(
            old_name='ExpensePH',
            new_name='Expense',
        ),
        migrations.RenameModel(
            old_name='FullTimePH',
            new_name='FullTime',
        ),
        migrations.RenameModel(
            old_name='PartTimePH',
            new_name='PartTime',
        ),
        migrations.RenameModel(
            old_name='PayrollPH',
            new_name='Payroll',
        ),
    ]
