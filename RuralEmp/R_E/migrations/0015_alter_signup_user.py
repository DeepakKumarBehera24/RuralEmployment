# Generated by Django 4.2.15 on 2024-08-21 02:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('R_E', '0014_remove_signup_password_alter_signup_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signup',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='signup', to=settings.AUTH_USER_MODEL),
        ),
    ]
