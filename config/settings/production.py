from .base import *

# Production settings

SECRET_KEY = env('SECRET_KEY')

DEBUG = env('DEBUG', default=False)

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

ERP_CONF = env.json('ERP_CONF')

SFTP_CONF = env.json('SFTP_CONF')

METEO_CONF = env.json('METEO_CONF')

ENEXPA_CONF = env.dict('ENEXPA_CONF')
