# Django
from django.contrib.auth.models import User
from socialapp.models import SocialMediaUser, SocialMediaFollower, SocialMediaEngagement, Profile
from django.db.models import Avg, Max, Count, Sum

class SocialStats:
    user = None
    followers = None

    def __init__(self, user):
        self.user = user
        stats = SocialMediaFollower.objects.filter(profile__user=user)
        if len(stats) > 0:
            self.followers = stats
        else:
            return None

    def get_follower_stats(self):
        if self.followers is not None:
            sum = self.followers.aggregate(sum=Sum('followers'))
            data = self.followers.values('social_name', 'followers', 'following')
            data = [ [ social['social_name'], [social['followers'], social['following']] ] for social in data ]
            return {
                'socials': dict(data),
                'total': sum['sum']
            }
