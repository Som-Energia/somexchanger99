# Generated by Django 3.0 on 2019-12-13 14:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('somexchanger99', '0008_file2exchange'),
    ]

    operations = [
        migrations.CreateModel(
            name='OriginFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Description name of the origin, eg. Meteologica', max_length=150, verbose_name='Name')),
                ('code_name', models.CharField(help_text='Code name of the origin, eg. METEOLGC', max_length=20, verbose_name='Code')),
            ],
        ),
        migrations.AlterField(
            model_name='file2exchange',
            name='name',
            field=models.CharField(help_text='Description name of the file to exchange, eg "Predicción Matallana"', max_length=150, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='file2exchange',
            name='origin',
            field=models.ForeignKey(help_text='Origin of this file', on_delete=django.db.models.deletion.CASCADE, to='somexchanger99.OriginFile', verbose_name='Origin'),
        ),
    ]
