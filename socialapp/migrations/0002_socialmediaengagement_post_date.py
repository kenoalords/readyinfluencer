# Generated by Django 2.2.6 on 2019-11-01 13:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialmediaengagement',
            name='post_date',
            field=models.DateField(blank=True, default=datetime.datetime(2019, 11, 1, 13, 18, 57, 575807)),
        ),
    ]
