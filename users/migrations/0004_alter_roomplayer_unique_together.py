# Generated by Django 4.2.2 on 2023-06-30 20:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0001_initial'),
        ('users', '0003_alter_croupieruser_room'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='roomplayer',
            unique_together={('room', 'player')},
        ),
    ]
