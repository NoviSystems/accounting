# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-18 21:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0005_auto_20160217_1443'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='business_unit',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit'),
        ),
        migrations.AddField(
            model_name='personnel',
            name='business_unit',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit'),
        ),
    ]
