# Generated by Django 4.2.15 on 2024-08-24 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('R_E', '0018_alter_workerhead_id_alter_workerhead_machineimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='workerhead',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
