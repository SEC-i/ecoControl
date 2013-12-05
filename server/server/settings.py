"""
Django settings for server project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%+fpp_s!v)#lc$vtnxu^r!7rzq)k+lzb*jt-m%)6pkclmpn7t2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'server',
    'server.webapi',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.cors.XsSharing',
)

ROOT_URLCONF = 'server.urls'

WSGI_APPLICATION = 'server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(os.path.dirname(__file__), 'test.db'),
            'TEST_NAME': os.path.join(os.path.dirname(__file__), 'test.db'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'bp2013h1_prototype',
            'USER': 'bp2013h1',
            'PASSWORD': 'hirsch',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = ''
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "../website"),
)

# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'django': {
            'level': 'WARNING',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 1024*1024*4, # 4 MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
        'webapi': {
            'level': 'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': 'logs/webapi.log',
            'maxBytes': 1024*1024*4, # 4 MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
        'crawler': {
            'level': 'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': 'logs/crawler.log',
            'maxBytes': 1024*1024*4, # 4 MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
        'planner': {
            'level': 'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': 'logs/planner.log',
            'maxBytes': 1024*1024*4, # 4 MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['django'],
            'propagate': True,
            'level':'WARNING',
        },
        'webapi': {
            'handlers': ['webapi'],
            'level': 'DEBUG',
        },
        'crawler': {
            'handlers': ['crawler'],
            'level': 'DEBUG',
        },
        'planner': {
            'handlers': ['planner'],
            'level': 'DEBUG',
        },

    }
}

# CORS middleware

XS_SHARING_ALLOWED_ORIGINS = '*'
XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS']
XS_SHARING_ALLOWED_HEADERS = ['Content-Type', '*']
XS_SHARING_ALLOWED_CREDENTIALS = 'true'