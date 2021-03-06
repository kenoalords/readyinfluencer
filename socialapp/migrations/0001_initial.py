# Generated by Django 2.2.6 on 2019-11-01 13:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Interest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interest', models.CharField(max_length=32)),
                ('description', models.CharField(max_length=160)),
            ],
            options={
                'ordering': ['interest'],
            },
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='ProfileView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
                ('country', models.CharField(max_length=64)),
                ('state', models.CharField(max_length=64)),
                ('city', models.CharField(max_length=64)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SocialMediaEngagement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('social_name', models.CharField(max_length=32)),
                ('post_id', models.BigIntegerField(blank=True)),
                ('impressions', models.IntegerField(default=0)),
                ('text', models.CharField(blank=True, max_length=1024)),
                ('media_type', models.CharField(blank=True, max_length=64)),
                ('likes', models.IntegerField(default=0)),
                ('retweets', models.IntegerField(default=0)),
                ('favourites', models.IntegerField(default=0)),
                ('comments', models.IntegerField(default=0)),
                ('saves', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SocialMediaFollower',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('social_name', models.CharField(max_length=32)),
                ('followers', models.BigIntegerField(default=0)),
                ('following', models.BigIntegerField(default=0)),
                ('is_verified', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='SocialMediaFollowerGrowth',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('social_name', models.CharField(max_length=32)),
                ('followers', models.BigIntegerField(default=0)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='SocialMediaUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('social_name', models.CharField(max_length=32)),
                ('social_id', models.BigIntegerField(blank=True)),
                ('access_token', models.CharField(blank=True, max_length=512)),
                ('oauth_token', models.CharField(blank=True, max_length=512)),
                ('oauth_token_secret', models.CharField(blank=True, max_length=512)),
                ('social_username', models.CharField(blank=True, max_length=64)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(blank=True, max_length=128)),
                ('gender', models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female')], max_length=16)),
                ('company', models.CharField(blank=True, max_length=64)),
                ('bio', models.CharField(blank=True, max_length=1024)),
                ('url', models.URLField(blank=True)),
                ('avatar', models.FileField(blank=True, upload_to='media/avatar/%Y/%m/%d/')),
                ('politics', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('locale', models.CharField(default='en-US', max_length=16)),
                ('is_influencer', models.BooleanField(default=False)),
                ('is_public', models.BooleanField(default=False)),
                ('accounts', models.ManyToManyField(blank=True, to='socialapp.SocialMediaUser')),
                ('followers', models.ManyToManyField(blank=True, to='socialapp.SocialMediaFollower')),
                ('followers_growth', models.ManyToManyField(blank=True, to='socialapp.SocialMediaFollowerGrowth')),
                ('interests', models.ManyToManyField(blank=True, to='socialapp.Interest')),
                ('lists', models.ManyToManyField(blank=True, to='socialapp.List')),
                ('medias', models.ManyToManyField(blank=True, to='socialapp.SocialMediaEngagement')),
                ('packages', models.ManyToManyField(blank=True, to='socialapp.Package')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('views', models.ManyToManyField(blank=True, to='socialapp.ProfileView')),
            ],
        ),
        migrations.CreateModel(
            name='PackageItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64)),
                ('cost', models.FloatField(max_length=32)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='socialapp.Package')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=1200)),
                ('unread', models.BooleanField(default=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('sender_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socialapp.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='ListProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profiles', to='socialapp.List')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socialapp.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_sender_deleted', models.BooleanField(default=False)),
                ('is_receiver_deleted', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('messages', models.ManyToManyField(blank=True, to='socialapp.Message')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='socialapp.Profile')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='socialapp.Profile')),
            ],
        ),
    ]
