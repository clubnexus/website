import json, os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
__default_key = 'c8au@b3fl5jige=#))s@qf)gt@=kkh17*@mf07ki*8@mdfotba'

__environ = {}
if os.path.isfile(os.path.join(BASE_DIR, '..', 'site.env')):
    with open(os.path.join(BASE_DIR, '..', 'site.env'), 'rb') as f:
        __environ = json.loads(f.read())

SECRET_KEY = __environ.get('SECRET_KEY', __default_key)
DEBUG = TEMPLATE_DEBUG = (SECRET_KEY == __default_key) or __environ.get('FORCE_DEBUG', False)
ALLOWED_HOSTS = __environ.get('HOSTS', '').split(';')

if not DEBUG:        
    ALLOWED_HOSTS.extend(['127.0.0.1', 'localhost', 'toontownnext.crinform.com.br', 'www.toontownnext.crinform.com.br', 'test.toontownnext.crinform.com.br'])

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor',
    'news',
    'users',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

PASSWORD_HASHERS = (
    'users.hashers.PBKDF2SHA512PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
)

ROOT_URLCONF = 'ttsite.urls'
WSGI_APPLICATION = 'ttsite.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default' : {
      'ENGINE' : 'django_mongodb_engine',
      'NAME' : 'sitedata'
    },
    'sqlite3': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = USE_L10N = USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

# Templates
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

###### MISC

# Users
LOGIN_REDIRECT_URL = '/'
CAPTCHA_ALWAYS_CORRECT = DEBUG or __environ.get('CAPTCHA_ALWAYS_CORRECT', 0)
SESSION_COOKIE_NAME = '__sessionid'
SESSION_COOKIE_DOMAIN = '.toontownnext.crinform.com.br' if not DEBUG else ''

# News
POST_PIC_UPLOAD_DIR = __environ.get('UPLOAD_PREFIX', '') + STATIC_URL.strip('/') + '/img/posts'
CKEDITOR_UPLOAD_PATH = POST_PIC_UPLOAD_DIR
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'

# Email
if DEBUG and __environ.get('FORCE_EMAIL_MODE', '') != 'PROD':
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    EMAIL_USE_TLS = False
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''

else:
    # Use production settings
    # N. B. Raises KeyError, on purpose, if EMAIL_PASSOWORD is not set
    EMAIL_USE_TLS = True
    EMAIL_HOST = __environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_HOST_USER = __environ.get('EMAIL_USER', 'clubnexus1@gmail.com')
    EMAIL_HOST_PASSWORD = __environ['EMAIL_PASSWORD']
    EMAIL_PORT = 587
    
DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'Toontown Next <toontownnext@crinform.com.br>'

# API
__dfgs =  'localhost' if DEBUG else ''
GAMESERVERS = __environ.get('GAMESERVERS', __dfgs).split(';')

API_KEY = __environ.get('API_KEY', 'dev')

__dfrl = GAMESERVERS[0] + ':19200' if GAMESERVERS else ''
API_RELAY = __environ.get('API_RELAY', __dfrl)

WANT_INVASION_DEBUG = __environ.get('WANT_INVASION_DEBUG', False)
