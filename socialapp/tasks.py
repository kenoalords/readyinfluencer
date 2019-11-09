# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import json
import requests
from bs4 import BeautifulSoup
import datetime
from sentry_sdk import capture_exception

# Django Imports
from socialapp.models import SocialMediaFollower, SocialMediaEngagement, SocialMediaUser, Profile
from django.contrib.auth.models import User
from django.db.models import Max


# Social imports
from socialapp.twitter import get_twitter_profile, get_user_tweets
from socialapp.instagram import get_instagram_profile_details, update_instagram_profile_media
from socialapp.instacrawler import InstagramScraper
# Twitter profile
@shared_task
def save_twitter_followers_task(user_id):
    req = get_twitter_profile(user_id)
    if req is not None:
        p = json.loads(req)
        if req:
            user = User.objects.get(pk=user_id)
            try:
                twitter = SocialMediaFollower.objects.get(profile__user=user, social_name='twitter')
                twitter.followers = int(p['followers_count'])
                twitter.following = int(p['friends_count'])
                twitter.is_verified = int(p['verified'])
                twitter.save()
                return True
            except SocialMediaFollower.DoesNotExist:
                profile_social_media = Profile.objects.get(user=user)
                profile = SocialMediaFollower(social_name="twitter", followers=int(p['followers_count']), following=int(p['friends_count']), is_verified=p['verified'])
                profile.save()
                profile_social_media.followers.add(profile)
                return True


# Twitter tweets
@shared_task
def save_user_tweets(user_id):
    user = User.objects.get(pk=user_id)
    since_id = None
    try:
        since = SocialMediaEngagement.objects.filter(social_name='twitter', profile__user=user).aggregate(max=Max('post_id'))
        since_id = since['max']
    except Exception as e:
        print(e)
        pass


    req = get_user_tweets(user_id, since_id=since_id)
    p = json.loads(req)
    if p:
        user_profile = Profile.objects.get(user=user)
        for tweet in p:
            if tweet['retweeted'] is False:
                save_tweet = SocialMediaEngagement(
                                post_id = tweet['id'],
                                social_name = 'twitter',
                                retweets = tweet['retweet_count'],
                                favourites = tweet['favorite_count'],
                                text = tweet['text'],
                                post_date = datetime.datetime.strptime(tweet['created_at'], "%Y-%m-%d %H:%M:%S.%f")
                            )
                save_tweet.save()
                user_profile.medias.add(save_tweet)
    else:
        return 'No new tweets'

# Instagram Profile Tasks
@shared_task
def get_instagram_profile_task(user_id):
    user = User.objects.get(pk=user_id)
    details = get_instagram_profile_details(user)
    if details:
        try:
            instagram = SocialMediaUser.objects.get(profile__user=user, social_name="instagram")
            instagram.social_username = details['username']
            instagram.save()
            crawl_user_instagram_page.delay(user.id)
        except SocialMediaUser.DoesNotExist:
            instagram = SocialMediaUser(social_username=details['username'], social_name="instagram")
            instagram.save()
            profile = Profile.objects.get(user=user)
            profile.accounts.add(instagram)
            crawl_user_instagram_page.delay(user.id)
    else:
        pass

# Crawl instagram page task
@shared_task
def crawl_user_instagram_page(user_id):
    user = User.objects.get(pk=user_id)
    try:
        instagram_profile = SocialMediaUser.objects.get(profile__user=user, social_name='instagram')
        url = 'https://instagram.com/%s/' % (instagram_profile.social_username)
        try:
            k = InstagramScraper()
            req = k.profile_page_metrics(url)

            if len(req) > 0:
                # Update User Social Media Profile
                try:
                    instagram = SocialMediaFollower.objects.get(profile__user=user, social_name="instagram")
                    instagram.followers = profiledata['edge_followed_by']['count']
                    instagram.following = profiledata['edge_follow']['count']
                    instagram.is_verified = profiledata['is_verified']
                    instagram.save()
                except SocialMediaFollower.DoesNotExist:
                    profile = Profile.objects.get(user=user)
                    instagram = SocialMediaFollower(
                                social_name="instagram",
                                followers=profiledata['edge_followed_by']['count'],
                                following=profiledata['edge_follow']['count'],
                                is_verified=profiledata['is_verified'],
                            )
                    instagram.save()
                    profile.followers.add(instagram)

                # Update instagram social media posts
                update_instagram_profile_media(user, profiledata)
            else:
                # Send a mail to admin
                pass
        except Exception as e:
            capture_exception(e)
            return None
    except SocialMediaUser.DoesNotExist:
        return None

# Allauth send mail task



# End
