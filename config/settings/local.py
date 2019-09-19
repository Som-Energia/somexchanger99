from .base import *

# Local settings

SECRET_KEY = env('SECRET_KEY', default='tk!27%+--p!9ukyh7v4nei!rrxt1u+vpn(wv958&b3s7-#o&as')

# Debug
DEBUG = env('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Local stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------

ERP_CONF = env.json('ERP_CONF')
SFTP_CONF = env.json('SFTP_CONF')
METEOLOGICA_CONF = env.json('METEOLOGICA_CONF')
