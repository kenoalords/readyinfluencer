from django.contrib.sitemaps import Sitemap
from socialapp.models import Profile

class ProfileSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return Profile.influencer.all()

    def lastmod(self, obj):
        return obj.date
