from django.contrib import admin
from socialapp.models import Profile, ProfileView, Interest, SocialMediaUser, SocialMediaFollower, SocialMediaEngagement, Package, PackageItem, List, ListProfile, Conversation, Message, InstagramInsight

# Register your models here.
admin.site.register(Profile)
admin.site.register(ProfileView)
admin.site.register(Interest)
admin.site.register(SocialMediaUser)
admin.site.register(SocialMediaFollower)
admin.site.register(SocialMediaEngagement)
admin.site.register(Package)
admin.site.register(PackageItem)
admin.site.register(List)
admin.site.register(ListProfile)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(InstagramInsight)
