# Generated by Django 4.0.6 on 2022-09-28 09:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0006_event_excel_upload_event_file_submission'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='max_per_team',
            field=models.IntegerField(default=4),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='submissions.event')),
                ('participants', models.ManyToManyField(to='submissions.participant')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='submissions.school')),
            ],
        ),
    ]