# Python
import requests, json
from urllib import parse
import oauth2 as oauth
import cgi
import numpy as np
from PIL import Image
import os
from sentry_sdk import capture_exception


# Django
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse, HttpResponseRedirect, HttpResponseNotFound
from .models import Profile, SocialMediaEngagement, SocialMediaFollower, SocialMediaUser, Interest, List, ListProfile, InstagramInsight, Package, PackageItem, Conversation, Message
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.db.models import Sum, Avg, Q, Count
from django.forms import formset_factory, modelformset_factory, inlineformset_factory
from django.core.exceptions import PermissionDenied
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.views.decorators.csrf import csrf_exempt, csrf_protect

# Social media modules
from socialapp.twitter import get_user_tweets, get_twitter_profile, twitter_followers_count, twitter_stats
from socialapp.instagram import get_instagram_profile_details, instagram_stats, instagram_crawler, instagram_crawler_stats
from socialapp.social_stats import SocialStats

# Tasks
from socialapp.tasks import save_twitter_followers_task, save_user_tweets, get_instagram_profile_task
from socialapp.templatetags.my_human_int import normalize_int

# Forms
from .forms import ProfileForm, UserForm, PackageForm, PackageItemForm, ListForm, ConversationForm, MessageForm, InstagramInsightsForm

# Mixins
from .mixins import ProfileSetupMixin, MustBeInfluencerMixin

from meta.views import Meta

default_meta = Meta(
	title="Find Instagram and Twitter influencers - ReadyInfluencer",
	description="Find the best Instagram and Twitter social media influencers to promote your products and services",
)

# Create your views here.
class IndexTemplateView(TemplateView):
	template_name = "socialapp/app/index.html"
	context_object_name = 'objects'
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['profiles'] = Profile.influencer.annotate(reach=Sum('followers__followers')).filter(reach__gte = 1).order_by('-reach')
		context['form'] = InstagramInsightsForm()
		context['meta'] = default_meta
		return context

class InfluencerTemplateView(TemplateView):
	template_name = "socialapp/app/influencers.html"
	context_object_name = 'objects'
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['profiles'] = Profile.influencer.annotate(reach=Sum('followers__followers')).filter(reach__gte = 1).order_by('-reach')
		context['form'] = InstagramInsightsForm()
		context['meta'] = default_meta
		return context

class InstagramTemplateView(TemplateView):
	template_name = "socialapp/app/instagram.html"
	def get(self, request):
		form = InstagramInsightsForm()
		meta = Meta(title="Check Instagram User Engagement Rate Free Insights - %s" % (get_current_site(request).name), description="Get free Instagram user engagement rate and relevant insights on any public instagram user account. Try it now")
		return render(request, self.template_name, context={ 'form': form, 'meta': meta })

	def post(self, request):
		form = InstagramInsightsForm(request.POST)
		if form.is_valid():
			data = None
			try:
				data = instagram_crawler(form.cleaned_data['username'])
			except Exception as e:
				messages.error(request, "We couldn't find any insights on %s, please check the username and try again" % form.cleaned_data['username'])
				# capture_exception(e)
				print(e)
				return render(request, self.template_name, context={ 'form': form })
			if data['username']:
				fullname = data['full_name']
				biography = data['biography']
				followers = data['edge_followed_by']['count']
				following = data['edge_follow']['count']
				picture = data['profile_pic_url']
				username = data['username']
				try:
					stats = instagram_crawler_stats(data) # average_likes, average_comments, engagement_rate
				except Exception as e:
					messages.error(request, "We couldn't find any insights on %s, please check the username and try again" % form.cleaned_data['username'])
					# capture_exception(e)
					print(e)
					return render(request, self.template_name, context={ 'form': form })

				try:
					insights = InstagramInsight.objects.get(user_account=username)
					insights.followers = followers
					insights.following = following
					insights.bio = biography
					insights.engagement_rate = stats['engagement_rate']
					insights.average_likes = stats['average_likes']
					insights.pic = picture
					insights.fullname = fullname
					insights.average_comments = stats['average_comments']
					insights.save()
					return HttpResponseRedirect(reverse('instagram_profile', kwargs={ 'user': username }))
				except InstagramInsight.DoesNotExist:
					try:
						insights = InstagramInsight(user_account=username, ip_address=request.META['REMOTE_ADDR'], followers=followers, following=following, engagement_rate=stats['engagement_rate'], average_likes=stats['average_likes'], average_comments=stats['average_comments'], pic=picture, fullname=fullname, bio=biography)
						insights.save()
						return HttpResponseRedirect(reverse('instagram_profile', kwargs={ 'user': username }))
					except Exception as e:
						messages.error(request, "We couldn't find any insights on %s, please check the username and try again" % form.cleaned_data['username'])
						# capture_exception(e)
						print(e)
						return render(request, self.template_name, context={ 'form': form })
				except Exception as e:
					messages.error(request, "We couldn't find any insights on %s, please check the username and try again" % form.cleaned_data['username'])
					# capture_exception(e)
					print(e)
					return render(request, self.template_name, context={ 'form': form })
			else:
				messages.error(request, "We couldn't find any insights on %s, please check the username and try again" % form.cleaned_data['username'])
				return render(request, self.template_name, context={ 'form': form })

class InstagramInsightsTemplateView(TemplateView):
	template_name = 'socialapp/app/instagram_insight.html'
	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)

		context['insight'] = InstagramInsight.objects.get(user_account=kwargs['user'])
		context['form'] = InstagramInsightsForm()
		meta = Meta(title="%s %s percent Instagram Engagement Rate - %s" % (kwargs['user'], context['insight'].engagement_rate, get_current_site(self.request).name), description="Get free Instagram user engagement rate and relevant insights on any public instagram user account. Try it now")
		context['meta'] = meta
		return context

class SearchTemplateView(TemplateView):
	template_name = 'socialapp/app/search.html'
	def get(self, request, *args, **kwargs):
		q = SearchQuery(request.GET['q'])
		profiles = Profile.objects.annotate( vector=SearchVector('interests__interest') ).filter(vector=q, is_public=True, is_influencer=True).annotate(reach=Sum('followers__followers')).order_by('-reach')

		meta = Meta(title="Find %s Instagram and Twitter Influencers - %s" % (request.GET['q'], get_current_site(request).name), description="Looking for %s Influencers on Instagram and Twitter? Check out these influencers and promote your brand" % request.GET['q'])
		return render(request, self.template_name, context={ 'profiles': profiles, 'meta': meta })

class DashboardView(LoginRequiredMixin, ProfileSetupMixin, TemplateView):
	template_name = 'socialapp/dashboard/index.html'
	def get(self, request, *args, **kwargs):
		stats = SocialStats(request.user).get_follower_stats()
		meta = Meta(title="Dashboard - %s" % (get_current_site(request).name))
		return render(request, self.template_name, context={'stats': stats, 'meta': meta})


	def get_instagram(self, req):
		try:
			return SocialMediaFollower.objects.get(user=req.user, social_name='instagram')
		except SocialMediaFollower.DoesNotExist:
			return False

class SocialMediaConnectView(LoginRequiredMixin, ProfileSetupMixin, MustBeInfluencerMixin, TemplateView):
	template_name = 'socialapp/dashboard/social_media_connect.html'

	def get(self, request, *args, **kwargs):
		twitter_callback_url =  settings.SITE_URL + reverse('social_media_connect_twitter')
		instagram_props = {
			'app_id': settings.INSTAGRAM['APP_ID'],
			'redirect_uri': settings.SITE_URL + '/dashboard/connect/instagram',
			'scope': 'user_profile,user_media',
			'response_type': 'code',
			'state': 1
		}
		instagram_url = settings.INSTAGRAM['AUTH_URL'] + '?' + parse.urlencode(instagram_props)
		profile = Profile.objects.get(user=request.user)
		accounts = profile.accounts.all().values('social_name')
		accounts = [ [name['social_name'], True] for name in accounts ]
		meta = Meta(title="Connect your social media account - %s" % (get_current_site(request).name), description="Connect your social media account")
		return render(request, self.template_name, context= { 'twitter_callback_url': twitter_callback_url, 'instagram_url': instagram_url , 'account': dict(accounts), 'meta': meta } )

class SocialMediaConnectInstagramView(LoginRequiredMixin, TemplateView):
	def get(self, request):
		# implement canceled authorization
		if request.GET['code']:
			payload = {
				'app_id'		: settings.INSTAGRAM['APP_ID'],
				'app_secret'	: settings.INSTAGRAM['APP_SECRET'],
				'grant_type'	: 'authorization_code',
				'redirect_uri'	: settings.SITE_URL + '/dashboard/connect/instagram',
				'code'			: request.GET['code'],
			}
			try:
				r = requests.post('https://api.instagram.com/oauth/access_token/', data=payload )
				# If we get a good response back
				if r.status_code == 200:
					response = r.json()
					try:
						social = SocialMediaUser.objects.get(profile__user=request.user, social_name='instagram')
						social.social_name = 'instagram'
						social.social_id = response['user_id']
						social.access_token = response['access_token']
						social.save()
					except SocialMediaUser.DoesNotExist:
						social = SocialMediaUser(social_name='instagram', social_id=response['user_id'], access_token=response['access_token'])
						social.save()
						profile = Profile.objects.get(user=request.user)
						profile.accounts.add(social)
					get_instagram_profile_task.delay(request.user.id)
					messages.success(request, "You Instagram account was connected successfully")
				else:
					return HttpResponseRedirect(reverse('social_media_connect_failed') + '?social=instagram&status=1')
			except Exception as e:
				print(e)
				return HttpResponseRedirect(reverse('social_media_connect_failed') + '?social=instagram&status=2')
			return HttpResponseRedirect(reverse('social_media_connect'))
		elif request.GET['error']:
			messages.error(request, request.GET['error_description'])
			return HttpResponseRedirect(reverse('social_media_connect_failed') + '?social=instagram&status=3')
		else:
			messages.error(request, 'An unknown error occured, please try again')
			return HttpResponseRedirect(reverse('social_media_connect_failed') + '?social=instagram&status=4')

# Twitter Oauth
consumer = oauth.Consumer(settings.TWITTER['CONSUMER_KEY'], settings.TWITTER['CONSUMER_SECRET'])
client = oauth.Client(consumer)
request_token_url = 'https://api.twitter.com/oauth/request_token'
access_token_url = 'https://api.twitter.com/oauth/access_token'
authenticate_url = 'https://api.twitter.com/oauth/authenticate'

@login_required
def authorize_twitter(request):
	resp, content = client.request(request_token_url, "GET")

	if resp['status'] != '200':
		raise Exception("Invalid response from Twitter.")

	decoded_content = content.decode('utf-8')
	tokens = [ name.split('=') for name in decoded_content.split('&') ]
	for content in tokens:
		request.session[content[0]] = content[1]

	url = "%s?oauth_token=%s" % (authenticate_url, request.session['oauth_token'])
	return HttpResponseRedirect(url)


@login_required
def twitter_access_token(request):
	token = oauth.Token(request.session['oauth_token'], request.session['oauth_token_secret'])
	token.set_verifier(request.GET['oauth_verifier'])
	client = oauth.Client(consumer, token)
	# Step 2. Request the authorized access token from Twitter.
	resp, content = client.request(access_token_url, "GET")
	if resp['status'] != '200':
		raise Exception("Invalid response from Twitter.")

	access_token = dict(cgi.parse_qsl(content.decode('utf-8')))

	try:
		twitter = SocialMediaUser.objects.get(social_name='twitter', profile__user=request.user)
		twitter.oauth_token = access_token['oauth_token']
		twitter.oauth_token_secret = access_token['oauth_token_secret']
		twitter.social_username = access_token['screen_name']
		twitter.save()
		save_twitter_followers_task.delay(request.user.id)
		save_user_tweets.delay(request.user.id)
		messages.success(request, 'Your twitter account has been successfully updated')
	except SocialMediaUser.DoesNotExist:
		twitter_profile = SocialMediaUser(
							social_name="twitter",
							social_id=access_token['user_id'],
							oauth_token=access_token['oauth_token'],
							oauth_token_secret=access_token['oauth_token_secret'],
							social_username=access_token['screen_name'],
							)
		twitter_profile.save()
		user_profile = Profile.objects.get(user=request.user)
		user_profile.accounts.add(twitter_profile)

		save_twitter_followers_task.delay(request.user.id)
		save_user_tweets.delay(request.user.id)
		messages.success(request, 'You have successfully connected your twitter account')
	return HttpResponseRedirect(reverse('social_media_connect'))

@login_required
def social_connect_failed(request):
	meta = Meta(title="Failed Social Connection - %s" % (get_current_site(request).name), description="Your social media connection failed")
	return render(request, './socialapp/dashboard/failed_connection.html', context={ 'meta': meta })

# Profile view
class ProfileTemplateView(LoginRequiredMixin, TemplateView):
	template_name = './socialapp/dashboard/profile.html'

	def get(self, request):
		try:
			user_profile = Profile.objects.get(user=request.user)
		except Profile.DoesNotExist:
			user_profile= None
		profile_form = ProfileForm(instance=user_profile)
		user_form = UserForm(instance=request.user)
		meta = Meta(title="Profile - %s" % (get_current_site(request).name), description="Edit and manage your profile")
		return render(request, self.template_name, context={ 'form': profile_form, 'user_form': user_form, 'profile': user_profile, 'meta': meta })

	def post(self, request, *args, **kwargs):
		# request.upload_handlers.insert(0, createAvatarThumbnail(request))
		user_form = UserForm(request.POST)
		profile_form = ProfileForm(request.POST, request.FILES)
		if user_form.is_valid():
			request.user.first_name = user_form.cleaned_data['first_name']
			request.user.last_name = user_form.cleaned_data['last_name']
			request.user.save()
			messages.success(request, "Your profile was saved successfully")

		if profile_form.is_valid():
			try:
				profile = Profile.objects.get(user=request.user)
				profile.gender = profile_form.cleaned_data['gender']
				profile.location = profile_form.cleaned_data['location']
				profile.bio = profile_form.cleaned_data['bio']
				profile.url = profile_form.cleaned_data['url']
				profile.politics = profile_form.cleaned_data['politics']
				profile.avatar = request.FILES['avatar']
				profile.save()
				profile.interests.set(profile_form.cleaned_data['interests'])
				profile.save()
			except Profile.DoesNotExist as e:
				profile = Profile(
					user = request.user,
					gender = profile_form.cleaned_data['gender'],
					bio = profile_form.cleaned_data['bio'],
					location = profile_form.cleaned_data['location'],
					url = profile_form.cleaned_data['url'],
					politics = profile_form.cleaned_data['politics'],
					avatar=request.FILES['avatar'],
				)
				profile.save()
				profile.interests.set(profile_form.cleaned_data['interests'])
				profile.save()
		else:
			print("Not saved!")
		return HttpResponseRedirect(reverse('dashboard_profile'))




class DashboardPackageTemplateView(LoginRequiredMixin, MustBeInfluencerMixin, TemplateView):
	template_name = 'socialapp/dashboard/package.html'

	def get(self, request):
		packages = Package.objects.filter(profile__user=request.user)
		meta = Meta(title="Offers - %s" % (get_current_site(request).name))
		return render(request, self.template_name, context={ 'packages': packages, 'meta': meta })

class AddPackageTemplateView(LoginRequiredMixin, MustBeInfluencerMixin, TemplateView):
	template_name = 'socialapp/dashboard/package_add.html'

	def get(self, request):
		package_form = PackageForm(prefix='package_form')
		PackageItemFormset = inlineformset_factory(Package, PackageItem, form=PackageItemForm, extra=2, min_num=1, max_num=5, validate_min=True)
		package_item_form = PackageItemFormset(prefix='package_item_form')
		meta = Meta(title="Add new offer - %s" % (get_current_site(request).name))
		return render(request, self.template_name, context={ 'package_form': package_form, 'package_item_form': package_item_form })

	def post(self, request):
		package_form = PackageForm(request.POST, request.FILES, prefix='package_form')
		PackageItemFormset = inlineformset_factory(Package, PackageItem, form=PackageItemForm, extra=2, min_num=1, max_num=5, validate_min=True)
		package_item_form = PackageItemFormset(request.POST, request.FILES, prefix='package_item_form')
		if package_form.is_valid() and package_item_form.is_valid():
			profile = Profile.objects.get(user=request.user)
			package = package_form.save()
			profile.packages.add(package)
			items = package_item_form.save(commit=False)
			for item in items:
				item.package = package
				item.save()
			messages.success(request, "Package saved successfully")
			return HttpResponseRedirect(reverse('dashboard_package'))
		return render(request, self.template_name, context={ 'package_form': package_form, 'package_item_form': package_item_form })

class EditPackageTemplateView(LoginRequiredMixin, MustBeInfluencerMixin, TemplateView):
	template_name = 'socialapp/dashboard/package_edit.html'

	def get(self, request, *args, **kwargs):
		try:
			package = Package.objects.get(pk=kwargs['id'])
		except Package.DoesNotExist:
			return render(request, 'socialapp/dashboard/package_404.html')
		package_form = PackageForm(instance=package)
		PackageItemFormset = inlineformset_factory(Package, PackageItem, form=PackageItemForm, extra=2, min_num=1, max_num=5, validate_min=True)
		package_item_form = PackageItemFormset(instance=package)
		meta = Meta(title="Edit Offer - %s" % (get_current_site(request).name))
		return render(request, self.template_name, context={ 'package_form': package_form, 'package_item_form': package_item_form, 'package': package, 'meta': meta })

	def post(self, request, *args, **kwargs):
		package = Package.objects.get(pk=kwargs['id'])
		package_form = PackageForm(request.POST, instance=package)
		PackageItemFormset = inlineformset_factory(Package, PackageItem, form=PackageItemForm, extra=2, min_num=1, max_num=5, validate_min=True)
		package_item_form = PackageItemFormset(request.POST, instance=package)
		if package_form.is_valid() and package_item_form.is_valid():
			package_form.save()
			package_item_form.save()
			messages.success(request, "Your changes were saved successfully")
			return HttpResponseRedirect(reverse('dashboard_package'))
		return render(request, self.template_name, context={ 'package_form': package_form, 'package_item_form': package_item_form } )

class ListsTemplateView(LoginRequiredMixin, TemplateView):
	template_name = 'socialapp/dashboard/lists.html'
	def get(self, request):
		meta = Meta(title="Lists - %s" % (get_current_site(request).name))
		return render(request, self.template_name, context={'lists': List.objects.filter(profile__user=request.user), 'form': ListForm(), 'meta': meta})

	def post(self, request):
		form = ListForm(request.POST)
		profile = Profile.objects.get(user=request.user)
		if form.is_valid():
			add_list = form.save()
			profile.lists.add(add_list)
			messages.success(request, "%s list created successfully" % form.cleaned_data['name'])
			return HttpResponseRedirect(reverse('dashboard_lists'))

class AddProfileToList(LoginRequiredMixin, TemplateView):
	template_name = 'socialapp/app/add_to_list.html'
	url = None
	def get(self, request, *args, **kwargs):
		try:
			profile = Profile.objects.filter(user__username=kwargs['user']).annotate(reach=Sum('followers__followers'))[0]
			lists = Profile.objects.get(user=request.user)
			meta = Meta(title="Add %s to list - %s" % (profile.fullname(), get_current_site(request).name))
			return render(request, self.template_name, context={ 'profile': profile, 'lists': lists.lists.all(), 'meta': meta })
		except Profile.DoesNotExist:
			pass

	def post(self, request, *args, **kwargs):

		try:
			list_id = int(request.POST['list'])
			profile = Profile.objects.get(user=request.user)
			list = profile.lists.get(pk=list_id)
			print(list_id, profile, list)
			try:
				check = ListProfile.objects.get(list=list, profile=Profile.objects.get(user__username=kwargs['user']))
				messages.error(request, "This user is already added to your %s list" % (list.name))
				return HttpResponseRedirect(reverse('user_profile', kwargs={ 'user': kwargs['user'] }))
			except ListProfile.DoesNotExist as e:
				print(e)
				user_profile = Profile.objects.get(user__username=kwargs['user'])
				add_user = ListProfile(list=list, profile=user_profile)
				add_user.save()
				messages.success(request, "%s has been added to your %s list" % (user_profile.fullname(), list.name))
				return HttpResponseRedirect(reverse('user_profile', kwargs={ 'user': kwargs['user'] }))
		except Exception as e:
			print(e, 'here')
			profile = Profile.objects.filter(user__username=kwargs['user']).annotate(reach=Sum('followers__followers'))[0]
			lists = Profile.objects.get(user=request.user)
			messages.error(request, "Something went wrong. We have been notified and will look into it.")
			return render(request, self.template_name, context={ 'profile': profile, 'lists': lists.lists.all() })

class SingleListTemplateView(LoginRequiredMixin, TemplateView):
	template_name = 'socialapp/dashboard/lists_single.html'

	def get(self, request, *args, **kwargs):
		try:
			list = List.objects.get(pk=kwargs['list'])
			members = ListProfile.objects.filter(list=list).annotate(followers=Sum('profile__followers__followers'))
			meta = Meta(title="%s list - %s" % (list.title, get_current_site(request).name))
			return render(request, self.template_name, context={ 'list': list, 'members': members })
		except List.DoesNotExist:
			messages.error(request, "The list you are trying to view does not exist or has been deleted by you")
			return HttpResponseRedirect(reverse('dashboard_lists'))

class DeleteListTemplateView(LoginRequiredMixin, TemplateView):
	template_name = 'socialapp/dashboard/lists_delete.html'

	def get(self, request, *args, **kwargs):
		try:
			list = List.objects.filter(pk=kwargs['list'], profile__user=request.user).annotate(count=Count('profile__listprofile')).values()[0]
			meta = Meta(title="Delete %s - %s" % (list.title, get_current_site(request).name))
			return render(request, self.template_name, context={ 'list': list })
		except Exception as e:
			messages.error(request, "The list you are trying to delete does not exist or has been deleted by you")
			return HttpResponseRedirect(reverse('dashboard_lists'))

	def post(self, request, *args, **kwargs):
		try:
			list_id = int(request.POST['list_id'])
			list = List.objects.filter(pk=list_id, profile__user=request.user)
			list.delete()
			messages.success(request, "List deleted successfully!")
			return HttpResponseRedirect(reverse('dashboard_lists'))
		except Exception as e:
			messages.error(request, "The list you are trying to delete does not exist or has been deleted by you")
			return HttpResponseRedirect(reverse('dashboard_lists'))

class DashboardMessagesTemplateView(LoginRequiredMixin, TemplateView):
	template_name = 'socialapp/dashboard/messages.html'

	def get(self, request):
		profile = Profile.objects.get(user=request.user)
		convos = Conversation.objects.filter((Q(sender=profile) | Q(receiver=profile))).annotate(convo_count=Count('id', distinct=True)).order_by('-date')
		meta = Meta(title="Messages - %s" % (get_current_site(request).name))
		return render(request, self.template_name, context={ 'convos': convos, 'meta': meta })

class DashboardViewMessageTemplateView(LoginRequiredMixin, TemplateView):
	template_name = 'socialapp/dashboard/message_single.html'

	def get(self, request, *args, **kwargs):
		profile= Profile.objects.get(user=request.user)
		convo = Conversation.objects.get(pk=kwargs['id'])
		if convo.sender.user != request.user != convo.receiver.user:
			raise PermissionDenied
		form = MessageForm()
		meta = Meta(title="Conversation - %s" % (get_current_site(request).name))
		return render(request, self.template_name, context={ 'chats': convo, 'form': form, 'meta': meta })

	def post(self, request, *args, **kwargs):
		message = MessageForm(request.POST)
		profile= Profile.objects.get(user=request.user)
		convo = Conversation.objects.get(pk=kwargs['id'])
		if convo.sender.user != request.user != convo.receiver.user:
			raise PermissionDenied
		if message.is_valid():
			# Save the chat
			msg = message.save(commit=False)
			msg.sender_profile = profile
			msg.save()
			convo.messages.add(msg)
			messages.success(request, "Your message was sent successfully")
			return HttpResponseRedirect(reverse('dashboard_view_message', kwargs={ 'id': convo.id }))


# App views
class UserProfileView(TemplateView):
	template_name = 'socialapp/app/user_profile.html'

	def get(self, request, *args, **kwargs):
		user = kwargs['user']
		profile = Profile.objects.filter(user__username=user).annotate(total=Sum('followers__followers'))[0]
		try:
			twitter_profile = profile.followers.get(social_name='twitter')
			twitter = {
				'stats': twitter_stats(profile),
				'followers': twitter_profile.followers,
				'following': twitter_profile.following
			}
			engagement = np.round( (twitter['stats']['retweets'] + twitter['stats']['favourites'])/twitter_profile.followers * 100, 2 )
			twitter['engagement_rate'] = engagement
		except Exception as e:
			twitter = None

		try:
			instagram_profile = profile.followers.get(social_name='instagram')
			instagram = {
				'stats': instagram_stats(profile),
				'followers': instagram_profile.followers,
				'following': instagram_profile.following
			}
			engagement = np.round( (instagram['stats']['all']['likes'] + instagram['stats']['all']['comments'])/instagram_profile.followers * 100, 2 )
			instagram['engagement_rate'] = engagement
		except Exception as e:
			# print(e)
			instagram = None
		total_reach = 0
		if twitter is not None:
			total_reach += twitter['followers']
		if instagram is not None:
			total_reach += instagram['followers']

		meta = Meta(title="%s Instagram and Twitter Influencer Insights - %s" % (profile.fullname(), get_current_site(request).name), description="Get %s Instagram and Twitter influencer stats and ranking. %s has a total reach of %s people. Contact %s today" % (profile.fullname(), profile.fullname(), normalize_int(total_reach), profile.fullname()))
		return render(request, self.template_name, context={ 'profile': profile, 'twitter': twitter, 'instagram': instagram, 'meta': meta })

class ContactUser(LoginRequiredMixin, TemplateView):
	template_name = 'socialapp/app/contact_user.html'
	def get(self, request, *args, **kwargs):
		try:
			profile = Profile.objects.filter(user__username=kwargs['user']).annotate(reach=Sum('followers__followers'))[0]
			form = ConversationForm()
			meta = Meta(title="Contact %s - %s" % (profile.fullname(), get_current_site(request).name), description="Promote your brand with %s. Get in touch now" % profile.fullname() )
			return render(request, self.template_name, context={ 'profile': profile, 'form': form, 'meta': meta })
		except Exception as e:
			raise Http404()

	def post(self, request, *args, **kwargs):
		form = ConversationForm(request.POST)

		if form.is_valid():
			sender = Profile.objects.get(user=request.user)
			# Save message
			msg = Message(sender_profile=sender, message=form.cleaned_data['conversation'])
			msg.save()
			# Save Convo
			receiver = Profile.objects.get(user__username=kwargs['user'])
			convo = Conversation(sender=sender, receiver=receiver)
			convo.save()
			# Add msg to convo
			convo.messages.add(msg)
			messages.success(request, 'Your message to %s was sent successfully.' % receiver.fullname() )
			return HttpResponseRedirect(request.META['HTTP_REFERER'])


class AboutPageTemplateView(TemplateView):
	template_name='socialapp/app/pages/about.html'
	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context['meta'] = Meta(title="About - %s" % get_current_site(self.request).name, description="Helping Instagram and Twitter influencers connect with brands and earn more money. Sign up today")
		return context

class HowWorksPageTemplateView(TemplateView):
	template_name='socialapp/app/pages/how-it-works.html'
	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context['meta'] = Meta(title="How it works - %s" % get_current_site(self.request).name, description="Helping Instagram and Twitter influencers connect with brands and earn more money. Sign up today")
		return context






# Custom Error Pages
def custom404handler(request, exception):
	response =  render(request, 'socialapp/app/404.html')
	response.status_code = 404
	return response

# End
