# Generated by Django 2.2.12 on 2020-06-02 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('somexchanger99', '0010_auto_20200507_2046'),
    ]

    operations = [
        migrations.AddField(
            model_name='curve2exchange',
            name='pattern',
            field=models.CharField(default='', help_text='Patern of the curve file', max_length=128, verbose_name='Pattern'),
            preserve_default=False,
        ),
    ]
