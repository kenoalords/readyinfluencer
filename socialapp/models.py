

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from socialapp.templatetags.my_human_int import normalize_int
import datetime
from django.utils import timezone
from .model_managers import ProfileManager

# Create your models here.
GENDER = [
    ('male', 'Male'),
    ('female', 'Female'),
]
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=128, blank=True)
    gender = models.CharField(max_length=16, choices=GENDER, blank=True)
    company = models.CharField(max_length=64, blank=True)
    bio = models.CharField(max_length=1024, blank=True)
    url = models.URLField(max_length=200, blank=True)
    avatar = models.FileField(upload_to='avatar/%Y/%m/%d/', blank=True)
    politics = models.BooleanField(default=False)
    interests = models.ManyToManyField('Interest', blank=True)
    views = models.ManyToManyField('ProfileView', blank=True)
    date = models.DateTimeField(auto_now_add=True)
    locale = models.CharField(max_length=16, default="en-US")
    accounts = models.ManyToManyField('SocialMediaUser', blank=True)
    followers = models.ManyToManyField('SocialMediaFollower', blank=True)
    followers_growth = models.ManyToManyField('SocialMediaFollowerGrowth', blank=True)
    medias = models.ManyToManyField('SocialMediaEngagement', blank=True)
    packages = models.ManyToManyField('Package', blank=True)
    lists = models.ManyToManyField('List', blank=True)
    is_influencer = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    objects = models.Manager()
    influencer = ProfileManager()

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def fullname(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def save(self, *args, **kwargs):
        # super().save(*args, **kwargs)
        if self.avatar:
            from io import BytesIO
            from django.core.files.base import ContentFile
            from datetime import datetime
            import os
            from PIL import Image
            try:
                image_source = os.path.join(settings.BASE_DIR, self.avatar.path)
                output = os.path.splitext(image_source)[0] + '_thumbnail.jpg'
                img = Image.open(image_source)
                img.thumbnail((320,320), Image.ANTIALIAS)
                fp = BytesIO()
                img.save(fp, "JPEG", quality=90)
                fp.seek(0)
                filename = "%s__%s.jpg" % (self.user.username, datetime.timestamp(datetime.now()))
                self.avatar.delete(save=True)
                self.avatar.save( name=filename, content=ContentFile(fp.read()), save=False )
                fp.close()
            except Exception as e:
                print(e)
                print("Couldn't save image thumbnail")

        super(Profile, self).save(*args, **kwargs)

    def thumbnail(self):
        try:
            return self.avatar.url
        except Exception:
            return settings.STATIC_URL + 'no_user_profile-pic.jpg'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('user_profile', args=[str(self.user.username)])

class SocialMediaUser(models.Model):
    social_name = models.CharField(max_length=32)
    social_id = models.BigIntegerField(blank=True)
    access_token = models.CharField(max_length=512, blank=True)
    oauth_token = models.CharField(max_length=512, blank=True)
    oauth_token_secret = models.CharField(max_length=512, blank=True)
    social_username = models.CharField(max_length=64, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.social_name

class SocialMediaFollower(models.Model):
    social_name = models.CharField(max_length=32)
    followers = models.BigIntegerField(default=0)
    following = models.BigIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.social_name} - {self.followers}'

class SocialMediaFollowerGrowth(models.Model):
    social_name = models.CharField(max_length=32)
    followers = models.BigIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.social_name} - {self.followers}'

class SocialMediaEngagement(models.Model):
    social_name = models.CharField(max_length=32)
    post_id = models.BigIntegerField(blank=True)
    impressions = models.IntegerField(default=0)
    text = models.CharField(max_length=1024, blank=True)
    media_type = models.CharField(max_length=64, blank=True)
    likes = models.IntegerField(default=0)
    retweets = models.IntegerField(default=0)
    favourites = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    saves = models.IntegerField()
    post_date = models.DateField(default=timezone.now, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.social_name

class Interest(models.Model):
    interest = models.CharField(max_length=32)
    description = models.CharField(max_length=160)

    def __str__(self):
        return self.interest
    class Meta:
        ordering = ['interest']

class ProfileView(models.Model):
    ip = models.GenericIPAddressField()
    country = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ip

class List(models.Model):
    name = models.CharField(max_length=128)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ListProfile(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='profiles')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.list.name

class Package(models.Model):
    title = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title

class PackageItem(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=64)
    cost = models.FloatField(max_length=32)
    date = models.DateTimeField(auto_now_add=True)

class Conversation(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver')
    messages = models.ManyToManyField('Message', blank=True)
    is_sender_deleted = models.BooleanField(default=False)
    is_receiver_deleted = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def last_message(self):
        try:
            last = self.messages.all()
            return list(last)[-1]
        except Exception as e:
            print(e)
            return

class Message(models.Model):
    message = models.CharField(max_length=1200)
    sender_profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    unread = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)


class InstagramInsight(models.Model):
    user_account = models.CharField(max_length=200)
    fullname = models.CharField(max_length=200)
    bio = models.CharField(max_length=1000)
    ip_address = models.GenericIPAddressField()
    followers = models.BigIntegerField()
    following = models.BigIntegerField()
    pic = models.CharField(blank=True, max_length=1000)
    engagement_rate = models.FloatField()
    average_comments = models.FloatField()
    average_likes = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_account

    def avatar(self):
        if self.pic:
            return self.pic
        else:
            return settings.STATIC_URL + 'no_user_profile-pic.jpg'





# End
