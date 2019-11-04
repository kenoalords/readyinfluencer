# Python
import oauth2 as oauth
import cgi
import json
import urllib

# Django
from django.conf import settings
from socialapp.models import SocialMediaUser, SocialMediaFollower, SocialMediaEngagement, Profile
from django.contrib import messages
from django.db.models import Avg, Max, Count, Sum
from django.contrib.auth.models import User

# Twitter Oauth

def twitter_api(url, method, oauth_token, oauth_token_secret):
    consumer = oauth.Consumer(settings.TWITTER['CONSUMER_KEY'], settings.TWITTER['CONSUMER_SECRET'])
    token = oauth.Token(oauth_token, oauth_token_secret)
    client = oauth.Client(consumer, token)
    resp, content = client.request(url, method)
    return content.decode('utf-8')


def get_user_tweets(user_id, count=200, since_id=None):
    user = User.objects.get(pk=user_id)
    try:
        twitter = SocialMediaUser.objects.get(profile__user=user, social_name='twitter')
        print(twitter)
        opts = {
            'count': count,
            'screen_name': twitter.social_username,
            'exclude_replies': False
        }
        if since_id is not None:
            opts['since_id'] = since_id
        return twitter_api('https://api.twitter.com/1.1/statuses/user_timeline.json?%s' % (urllib.parse.urlencode(opts)), 'GET', twitter.oauth_token, twitter.oauth_token_secret)
    except SocialMediaUser.DoesNotExist:
        return None

def get_twitter_profile(user_id):
    user = User.objects.get(pk=user_id)
    try:
        twitter = SocialMediaUser.objects.get(profile__user=user, social_name='twitter')
        return twitter_api('https://api.twitter.com/1.1/users/show.json?screen_name=%s' % (twitter.social_username), 'GET', twitter.oauth_token, twitter.oauth_token_secret)
    except SocialMediaUser.DoesNotExist:
        return None

def twitter_followers_count(req):
    return SocialMediaFollower.objects.filter(user=req.user, social_name='twitter').order_by('-date')[0]

def twitter_stats(req):
    tweets = SocialMediaEngagement.objects.filter(profile__user=req.user, social_name='twitter').aggregate(retweets=Avg('retweets'), favourites=Avg('favourites'))

    if tweets:
        return tweets
    else:
        return None
