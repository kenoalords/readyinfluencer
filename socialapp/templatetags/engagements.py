from django import template

register = template.Library()

def instagram_video_engagement(data):
    return (data['total_likes'] + data['total_comments']) / data['total_impressions'] * 100

register.filter('engagement_rate', instagram_video_engagement)
