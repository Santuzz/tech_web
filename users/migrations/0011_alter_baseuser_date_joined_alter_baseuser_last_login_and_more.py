# Generated by Django 4.2.2 on 2023-07-11 09:05

import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_baseuser_date_joined_alter_baseuser_last_login_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseuser',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 11, 9, 5, 37, 232769, tzinfo=datetime.timezone.utc), verbose_name='date joined'),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='last_login',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 11, 9, 5, 37, 232769, tzinfo=datetime.timezone.utc), verbose_name='last login'),
        ),
        migrations.AlterField(
            model_name='giocata',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
