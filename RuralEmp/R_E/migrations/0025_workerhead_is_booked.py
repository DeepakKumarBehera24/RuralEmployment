# Generated by Django 4.2.15 on 2024-09-04 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('R_E', '0024_alter_job_phonenumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='workerhead',
            name='is_booked',
            field=models.BooleanField(default=False),
        ),
    ]
