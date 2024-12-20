# Generated by Django 4.2.15 on 2024-08-20 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('R_E', '0008_job_phonenumber'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('feedback', models.TextField()),
                ('rating', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=5)),
                ('date', models.DateField(auto_now_add=True)),
            ],
        ),
    ]
