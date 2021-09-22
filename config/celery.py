from __future__ import absolute_import, unicode_literals
import os

import sentry_sdk
from celery import Celery
from django.conf import settings
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from somexchanger99 import VERSION

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

app = Celery('somexchanger')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[CeleryIntegration(), RedisIntegration()],
    send_default_pii=True,
    environment=os.environ['DJANGO_SETTINGS_MODULE'].split('.')[-1],
    release=VERSION,
)
