# Generated by Django 4.1.7 on 2023-03-12 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventApp', '0008_createvent_endtime_createvent_starttime_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='createvent',
            name='tBkngPrice',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='venues',
            name='mobNo',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
