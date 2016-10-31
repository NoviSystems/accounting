# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-31 20:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_auto_20161026_1636'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cash',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('predicted_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Predicted Amount')),
                ('actual_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name=b'Actual Amount')),
                ('reconciled', models.BooleanField(default=False, verbose_name=b'Reconciled')),
                ('name', models.CharField(max_length=50, verbose_name=b'Name')),
                ('date_associated', models.DateField(verbose_name=b'Date Associated')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='businessunit',
            name='cash',
        ),
        migrations.AddField(
            model_name='cash',
            name='business_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.BusinessUnit', verbose_name=b'Business Unit'),
        ),
    ]
