# Generated by Django 5.2.1 on 2025-06-05 08:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('twitter_api_key', models.CharField(blank=True, max_length=255, null=True)),
                ('twitter_api_secret', models.CharField(blank=True, max_length=255, null=True)),
                ('twitter_access_token', models.CharField(blank=True, max_length=255, null=True)),
                ('twitter_access_secret', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
