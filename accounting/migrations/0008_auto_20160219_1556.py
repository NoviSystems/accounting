# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-19 20:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0007_auto_20160218_1640'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contract',
            old_name='contract_amount',
            new_name='amount',
        ),
        migrations.RenameField(
            model_name='invoice',
            old_name='invoice_amount',
            new_name='amount',
        ),
        migrations.RenameField(
            model_name='invoice',
            old_name='invoice_date',
            new_name='date',
        ),
        migrations.RenameField(
            model_name='invoice',
            old_name='invoice_number',
            new_name='number',
        ),
        migrations.RemoveField(
            model_name='lineitem',
            name='month',
        ),
        migrations.AddField(
            model_name='expense',
            name='month',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounting.Month'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='month',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounting.Month'),
            preserve_default=False,
        ),
    ]
