# Generated by Django 4.1.7 on 2023-03-17 13:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eventApp', '0017_venues_srchdate'),
    ]

    operations = [
        migrations.AddField(
            model_name='venues',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
