from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set default django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialinfluence.settings')

app = Celery('socialinfluence')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
from django.conf import settings
app.autodiscover_tasks(settings.INSTALLED_APPS)
