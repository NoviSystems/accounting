# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-14 18:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0017_placeholder_data_copy'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cash',
            name='lineitem_ptr',
        ),
        migrations.RemoveField(
            model_name='expense',
            name='lineitem_ptr',
        ),
        migrations.RemoveField(
            model_name='fulltime',
            name='personnel_ptr',
        ),
        migrations.RemoveField(
            model_name='income',
            name='lineitem_ptr',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='contract',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='income_ptr',
        ),
        migrations.RemoveField(
            model_name='lineitem',
            name='business_unit',
        ),
        migrations.RemoveField(
            model_name='parttime',
            name='personnel_ptr',
        ),
        migrations.RemoveField(
            model_name='payroll',
            name='expense',
        ),
        migrations.RemoveField(
            model_name='personnel',
            name='business_unit',
        ),
        migrations.DeleteModel(
            name='Cash',
        ),
        migrations.DeleteModel(
            name='Expense',
        ),
        migrations.DeleteModel(
            name='FullTime',
        ),
        migrations.DeleteModel(
            name='Income',
        ),
        migrations.DeleteModel(
            name='Invoice',
        ),
        migrations.DeleteModel(
            name='LineItem',
        ),
        migrations.DeleteModel(
            name='PartTime',
        ),
        migrations.DeleteModel(
            name='Payroll',
        ),
        migrations.DeleteModel(
            name='Personnel',
        ),
    ]
