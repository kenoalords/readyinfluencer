from django.db import models

class ProfileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_public=True, is_influencer=True)
