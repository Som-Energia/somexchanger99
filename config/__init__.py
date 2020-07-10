VERSION = '0.1.2'

from .celery import app as celery_app

__all__ = ('celery_app',)
