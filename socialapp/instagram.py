# Python
import requests
from urllib import parse
from bs4 import BeautifulSoup
import json
import pprint
import datetime
import numpy as np

# Django
from django.conf import settings
from django.urls import reverse
from socialapp.models import SocialMediaUser, SocialMediaFollower, SocialMediaEngagement, Profile
from django.db.models import Avg, Sum, Max
from django.http import Http404

def get_instagram_profile_details(user):
    try:
        instagram = SocialMediaUser.objects.get(profile__user=user, social_name='instagram')
        query = {
            'fields': 'media_count,username',
            'access_token': instagram.access_token
        }
        url = settings.INSTAGRAM['GRAPH_URL'] + '/' + str(instagram.social_id) + '?' + parse.urlencode(query)
        req = requests.get(url)
        if req.status_code == 200:
            return req.json()
        else:
            return False
    except SocialMediaUser.DoesNotExist:
        return None

def update_instagram_profile_media(user, data):
    videos_count = data['edge_felix_video_timeline']['count']
    user_profile = Profile.objects.get(user=user)
    if videos_count > 0:
        videos = data['edge_felix_video_timeline']['edges']
        for video in videos:
            try:
                text = video['node']['edge_media_to_caption']['edges'][0]['node']['text']
            except Exception as e:
                text = ''
                print('No instagram video text')
            try:
                media = SocialMediaEngagement.objects.get(social_name="instagram", post_id=video['node']['id'])
                media.comments = video['node']['edge_media_to_comment']['count']
                media.likes = video['node']['edge_liked_by']['count']
                media.impressions = video['node']['video_view_count']
                media.text = text
                media.post_date = datetime.datetime.fromtimestamp(video['node']['taken_at_timestamp'])
                media.save()
            except SocialMediaEngagement.DoesNotExist:
                media = SocialMediaEngagement(
                    social_name="instagram",
                    post_id=video['node']['id'],
                    comments=video['node']['edge_media_to_comment']['count'],
                    likes=video['node']['edge_liked_by']['count'],
                    media_type='video',
                    impressions=video['node']['video_view_count'],
                    text=text,
                    post_date=datetime.datetime.fromtimestamp(video['node']['taken_at_timestamp'])
                )
                media.save()
                user_profile.medias.add(media)
    images_count = data['edge_owner_to_timeline_media']['count']
    if images_count > 0:
        images = data['edge_owner_to_timeline_media']['edges']
        for image in images:
            try:
                text = image['node']['edge_media_to_caption']['edges'][0]['node']['text']
            except Exception as e:
                text = ''
                print('No instagram image text')
            try:
                media = SocialMediaEngagement.objects.get(social_name="instagram", post_id=image['node']['id'])
                media.comments = image['node']['edge_media_to_comment']['count']
                media.likes = image['node']['edge_liked_by']['count']
                media.text = text
                media.post_date = datetime.datetime.fromtimestamp(image['node']['taken_at_timestamp'])
                media.save()
            except SocialMediaEngagement.DoesNotExist:
                media = SocialMediaEngagement(
                    comments=image['node']['edge_media_to_comment']['count'],
                    likes=image['node']['edge_liked_by']['count'],
                    social_name="instagram",
                    post_id=image['node']['id'],
                    media_type='image',
                    text=text,
                    post_date=datetime.datetime.fromtimestamp(image['node']['taken_at_timestamp']),
                )
                media.save()
                user_profile.medias.add(media)
    # pass


def instagram_stats(req):
    instagram = SocialMediaEngagement.objects.filter(profile__user=req.user, social_name='instagram')
    video_stats = instagram.filter(media_type__exact="video").aggregate(avg_impressions=Avg('impressions'), total_impressions=Sum('impressions'), total_likes=Sum('likes'), total_comments=Sum('comments'))
    avg_stats = instagram.aggregate(comments=Avg('comments'), likes=Avg('likes'), sum_likes=Sum('likes'))
    media = {
        'all': avg_stats,
        'video': video_stats,
    }
    # print(media)
    return media


def instagram_crawler(username):
    instagram_url = "https://instagram.com/%s" % username.lower()
    req = requests.get(instagram_url)
    if req.status_code == 200:
        bs = BeautifulSoup(req.content, 'html.parser')
        import re
        scripts = bs.find(string=re.compile("graphql"))
        d = json.loads(scripts.replace('window._sharedData = ', '').replace(';',''))
        return d['entry_data']['ProfilePage'][0]['graphql']['user']
    else:
        raise Http404

def instagram_crawler_stats(data):
    comments = []
    likes = []
    followers = data['edge_followed_by']['count']
    # Check video content
    if data['edge_felix_video_timeline']['count'] > 0:
        for video in data['edge_felix_video_timeline']['edges']:
            comments.append(video['node']['edge_media_to_comment']['count'])
            likes.append(video['node']['edge_liked_by']['count'])

    # Check image content
    if data['edge_owner_to_timeline_media']['count'] > 0:
        for image in data['edge_owner_to_timeline_media']['edges']:
            comments.append(image['node']['edge_media_to_comment']['count'])
            likes.append(image['node']['edge_liked_by']['count'])

    total_comments = sum(comments)
    total_likes = sum(likes)
    average_comments = np.round( total_comments/len(comments), 2 )
    average_likes = np.round(total_likes/len(likes), 2)
    return {
            'total_comments': total_comments,
            'total_likes': total_likes,
            'average_comments': average_comments,
            'average_likes': average_likes,
            'engagement_rate': np.round( (average_comments+average_likes)/followers * 100, 2 )
        }


# End
