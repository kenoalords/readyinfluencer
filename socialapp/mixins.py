from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from .models import Profile
from django.contrib import messages
from django.core.exceptions import PermissionDenied

class ProfileSetupMixin:
    def dispatch(self, request, *args, **kwargs):

        try:
            profile = Profile.objects.get(user=request.user)
            if profile.user.first_name == '' or profile.user.last_name == '':
                messages.error(request, "Please set up your profile to continue")
                return HttpResponseRedirect(reverse('dashboard_profile') + '?account=new')
            else:
                return super().dispatch(request, *args, **kwargs)
        except Profile.DoesNotExist:
            messages.error(request, "Please set up your profile to continue")
            return HttpResponseRedirect(reverse('dashboard_profile') + '?account=new')


class MustBeInfluencerMixin:
    def dispatch(self, request, *args, **kwargs):
        profile = Profile.objects.get(user=request.user)
        if profile.is_influencer:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied







# End mixins
