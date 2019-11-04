from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from socialapp import views
from django.views.generic import TemplateView
from socialapp.views import IndexTemplateView, UserProfileView, DashboardView, ProfileTemplateView, SocialMediaConnectView, SocialMediaConnectInstagramView, authorize_twitter, twitter_access_token, DashboardPackageTemplateView, AddPackageTemplateView, EditPackageTemplateView, ListsTemplateView, AddProfileToList, SingleListTemplateView, DeleteListTemplateView, ContactUser, DashboardMessagesTemplateView, DashboardViewMessageTemplateView, SearchTemplateView, InfluencerTemplateView, InstagramTemplateView, InstagramInsightsTemplateView, AboutPageTemplateView, HowWorksPageTemplateView, custom404handler



from django.contrib.auth.decorators import login_required, permission_required


urlpatterns = [
	path('', IndexTemplateView.as_view(), name='index'),
	path('influencers', InfluencerTemplateView.as_view(), name='influencers'),
	path('about', AboutPageTemplateView.as_view(), name='about'),
	path('how-it-works', HowWorksPageTemplateView.as_view(), name='how_it_works'),
	path('find-influencers', SearchTemplateView.as_view(), name='search'),
	path('instagram-insights', InstagramTemplateView.as_view(), name='instagram'),
	path('instagram-insights/<str:user>', InstagramInsightsTemplateView.as_view(), name='instagram_profile'),
	path('influencer/<str:user>', UserProfileView.as_view(), name='user_profile'),
	path('influencer/<str:user>/add-to-list', AddProfileToList.as_view(), name='add_user_profile_to_list'),
	path('influencer/<str:user>/contact', ContactUser.as_view(), name='contact_user'),
	path('dashboard', DashboardView.as_view(), name='dashboard'),
	path('dashboard/connect', SocialMediaConnectView.as_view(), name='social_media_connect'),
	path('dashboard/connect/failed', views.social_connect_failed, name='social_media_connect_failed'),
	path('dashboard/connect/instagram', SocialMediaConnectInstagramView.as_view(), name='social_media_connect_instagram'),
	path('dashboard/connect/twitter', authorize_twitter, name='social_media_connect_twitter'),
	path('dashboard/connect/twitter/authenticate', twitter_access_token),
	path('dashboard/profile', ProfileTemplateView.as_view(), name='dashboard_profile'),
	path('dashboard/offer', DashboardPackageTemplateView.as_view(), name='dashboard_package'),
	path('dashboard/offer/add', AddPackageTemplateView.as_view(), name='add_dashboard_package'),
	path('dashboard/offer/<int:id>/edit', EditPackageTemplateView.as_view(), name='edit_dashboard_package'),
	path('dashboard/lists', ListsTemplateView.as_view(), name='dashboard_lists'),
	path('dashboard/lists/<int:list>', SingleListTemplateView.as_view(), name='dashboard_list_single'),
	path('dashboard/lists/<int:list>/delete', DeleteListTemplateView.as_view(), name='dashboard_list_delete'),
	path('dashboard/messages', DashboardMessagesTemplateView.as_view(), name='dashboard_messages'),
	path('dashboard/messages/<int:id>/view', DashboardViewMessageTemplateView.as_view(), name='dashboard_view_message'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = custom404handler
