import json, os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
__default_key = 'c8au@b3fl5jige=#))s@qf)gt@=kkh17*@mf07ki*8@mdfotba'

__environ = {}
if os.path.isfile(os.path.join(BASE_DIR, '..', 'site.env')):
    with open(os.path.join(BASE_DIR, '..', 'site.env'), 'rb') as f:
        __environ = json.loads(f.read())

SECRET_KEY = __environ.get('SECRET_KEY', __default_key)
DEBUG = TEMPLATE_DEBUG = (SECRET_KEY == __default_key)
ALLOWED_HOSTS = []

if not DEBUG:        
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'toontownnext.net', 'www.toontownnext.net']

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
TIME_ZONE = 'UTC'
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

# News
POST_PIC_UPLOAD_DIR = __environ.get('UPLOAD_PREFIX', '') + STATIC_URL.strip('/') + '/img/posts'
CKEDITOR_UPLOAD_PATH = POST_PIC_UPLOAD_DIR
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'

# API
API_RELAY = 'localhost:19200'

__dfgs =  'localhost' if DEBUG else ''
GAMESERVERS = __environ.get('GAMESERVERS', __dfgs).split(';')

LAUNCHERFILES_URL = STATIC_URL + 'data'
LAUNCHERFILES_DIR = os.path.join(STATICFILES_DIRS[0], 'data')
