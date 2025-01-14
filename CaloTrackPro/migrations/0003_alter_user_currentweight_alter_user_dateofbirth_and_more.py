# Generated by Django 5.0.6 on 2024-05-21 16:01

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CaloTrackPro', '0002_alter_user_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='currentweight',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='dateofbirth',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('Female', 'Female'), ('Male', 'Male')], default='Female', max_length=6),
        ),
        migrations.AlterField(
            model_name='user',
            name='height',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='recommendcalo',
            field=models.IntegerField(default=0),
        ),
    ]
