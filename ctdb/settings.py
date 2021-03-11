"""
Django settings for demo project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import json
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


with open(BASE_DIR / 'secrets.json') as secrets_file:
    secrets = json.load(secrets_file)


def get_secret(setting, secrets=secrets):
    """Get secret setting or fail with ImproperlyConfigured"""
    try:
        return secrets[setting]
    except KeyError:
        raise ImproperlyConfigured(f'Please set the "{setting}" setting in secrets_file.')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'va8k29j1o_=rs9bw!ym@s#b8zz3=9cmj_o731i$^6)9+z_9ob#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not get_secret('IS_PRODUCTION')

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'widget_tweaks',  # this package makes it easier to integrate django templates with bootstrap
    'accounts.apps.AccountsConfig',
    'telecom.apps.TelecomConfig',
    'diary.apps.DiaryConfig',
    'day.apps.DayConfig',
    'log.apps.LogConfig',
    'core.apps.CoreConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # this allows us to handle static files with DEBUG = False and runserver
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ctdb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ctdb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES_SQLITE = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DATABASES_MYSQL = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ctdbdb',
        'USER': 'admin',
        'PASSWORD': '20180105',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

DATABASES_MSSQL = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'T21',
        'USER': 'jimmy_lin',
        'PASSWORD': get_secret('DATABASES_MSSQL_PASSWORD'),
        'HOST': '10.210.31.15',
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
}

IS_PRODUCTION = get_secret('IS_PRODUCTION')
if IS_PRODUCTION:
    DATABASES = DATABASES_MSSQL
else:
    DATABASES = DATABASES_MYSQL

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Disable most of the AUTH_PASSWORD_VALIDATORS.
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'zh-Hant'

# For i18n
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# This limits the set_language view option
LANGUAGES = {
    ('zh-hant', ''),
    ('en', ''),
}

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_ROOT = BASE_DIR / 'static'

STATIC_URL = '/static/'

MEDIA_ROOT = BASE_DIR / 'uploads'

MEDIA_URL = '/uploads/'

STATICFILES_DIRS = [
    BASE_DIR / 'node_modules',
]

# Build-in auth system

LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = '/'

# SMTP things

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
USE_GMAIL = False

if USE_GMAIL:
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'j3ycode@gmail.com'
    EMAIL_HOST_PASSWORD = get_secret('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = 'TDB <j3ycode@gmail.com>'
    SERVER_EMAIL = 'TDB <j3ycode@gmail.com>'
else:
    EMAIL_HOST = '223.26.68.17'
    EMAIL_USE_TLS = False
    EMAIL_PORT = 25
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    DEFAULT_FROM_EMAIL = 'TDB <TDB@chief.com.tw>'
    SERVER_EMAIL = 'TDB <TDB@chief.com.tw>'


# Authentication things
AUTHENTICATION_BACKENDS = ['accounts.backends.AuthWithUsernameOrEmailBackend']
