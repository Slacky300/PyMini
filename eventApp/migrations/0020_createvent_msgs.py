# Generated by Django 4.1.7 on 2023-03-19 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventApp', '0019_alter_useraccount_is_nuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='createvent',
            name='msgs',
            field=models.TextField(blank=True, null=True),
        ),
    ]
