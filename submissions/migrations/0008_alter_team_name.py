# Generated by Django 4.0.6 on 2022-09-28 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0007_event_max_per_team_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
