# Generated by Django 2.2.6 on 2019-11-01 13:19

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('socialapp', '0002_socialmediaengagement_post_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialmediaengagement',
            name='post_date',
            field=models.DateField(blank=True, default=datetime.datetime(2019, 11, 1, 13, 19, 58, 726131, tzinfo=utc)),
        ),
    ]
