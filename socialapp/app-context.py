from django.conf import settings
from .models import Profile, Interest
from django.contrib.sites.shortcuts import get_current_site

def is_influencer(request):
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            return { 'is_influencer': profile.is_influencer }
        except Profile.DoesNotExist as e:
            return { 'is_influencer': False }
    else:
        return { 'is_influencer': False }

def user_profile(request):
    if request.user.is_authenticated:
        try:
            return { 'user_profile': Profile.objects.get(user=request.user)}
        except Profile.DoesNotExist as e:
            return { 'user_profile': False }
    else:
        return { 'user_profile': False }

def user_interests(request):
    try:
        interests = Interest.objects.all().values()
        return { 'user_interests':  interests}
    except Exception as e:
        return { 'user_interests': None }

def sites_context(request):
    if get_current_site(request):
        return { 'site': get_current_site(request) }
    else:
        return { 'site': None }
