# Generated by Django 5.1 on 2024-08-19 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Signup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(max_length=20)),
                ('lastName', models.CharField(max_length=20)),
                ('DOB', models.DateField()),
                ('city', models.CharField(max_length=30)),
                ('state', models.CharField(max_length=15)),
                ('phoneNumber', models.IntegerField()),
                ('userType', models.CharField(choices=[('worker head', 'Worker Head'), ('job provider', 'Job Provider')], default='worker head', max_length=20)),
                ('adharNumber', models.IntegerField(max_length=16)),
                ('password', models.CharField(max_length=128)),
                ('reEnter', models.CharField(max_length=128)),
            ],
        ),
    ]
