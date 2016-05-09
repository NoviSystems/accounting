# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-25 21:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0005_remove_invoice_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parttime',
            name='id',
        ),
        migrations.RemoveField(
            model_name='salary',
            name='id',
        ),
        migrations.AddField(
            model_name='parttime',
            name='personnel_ptr',
            field=models.OneToOneField(auto_created=True, default=None, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='accounting.Personnel'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='salary',
            name='personnel_ptr',
            field=models.OneToOneField(auto_created=True, default=None, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='accounting.Personnel'),
            preserve_default=False,
        ),
    ]
