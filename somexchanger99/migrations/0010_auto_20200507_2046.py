# Generated by Django 3.0 on 2020-05-07 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('somexchanger99', '0009_auto_20191213_1505'),
    ]

    operations = [
        migrations.AddField(
            model_name='atr2exchange',
            name='last_upload',
            field=models.DateTimeField(blank=True, help_text='Last time this atr process was uploaded', null=True, verbose_name='Last date uploaded'),
        ),
        migrations.AlterField(
            model_name='file2exchange',
            name='active',
            field=models.BooleanField(help_text='Check to enable or disable exchange this kind of files', verbose_name='Active'),
        ),
        migrations.AlterField(
            model_name='file2exchange',
            name='last_upload',
            field=models.DateTimeField(blank=True, help_text='Last time this kind of files was uploaded', null=True, verbose_name='Last date uploaded'),
        ),
    ]