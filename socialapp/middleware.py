from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from .models import Profile

class ProfileSetupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            profile = Profile.objects.get(user=request.user)
            if profile.is_influencer == True:
                # Check for first name and last name
                if profile.user.first_name == '' or profile.user.last_name == '':
                    return HttpResponseRedirect(reverse('dashboard_profile'))
        except Exception as e:
            print(e)
        return response
