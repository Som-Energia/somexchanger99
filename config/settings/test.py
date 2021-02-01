from .base import *

env.read_env(
    os.path.join(str(BASE_DIR), 'somexchanger99/tests/.env.test'),
)

SECRET_KEY = env('SECRET_KEY', default='tk!27%+--p!9ukyh7v4nei!rrxt1u+vpn(wv958&b3s7-#o&as')

# Debug
DEBUG = env('DEBUG', default=True)
ERP_CONF = env.json('ERP_CONF')

TEST = 'OK'
