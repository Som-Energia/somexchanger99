# Generated by Django 2.1.4 on 2019-01-29 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File2Exchange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('process', models.CharField(help_text='ATR process asociated with the type (F1, A3, C1, ...)', max_length=128, verbose_name='Process')),
                ('step', models.CharField(help_text='Step of the ATR process. No used when process is F1', max_length=10, verbose_name='Step')),
                ('model', models.CharField(help_text='dotted model name in erp, eg. "giscedata.switching"', max_length=256, verbose_name='ERP model')),
            ],
        ),
    ]
