import os
import sys
import logging
from django.utils.translation import ugettext_lazy as _

import environ


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# reading .env file
env = environ.Env()
env.read_env(os.path.join(BASE_DIR, '.env'))


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'widget_tweaks',
    'django_extensions',

    'core.apps.CoreConfig',
    'account_settings.apps.AccountSettingsConfig',
    'accounts.apps.AccountsConfig',
    'players.apps.PlayersConfig',
    'teams.apps.TeamsConfig',
    'transfer_history.apps.TransferHistoryConfig',
    'tools.apps.ToolsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.LastUserActivityMiddleware',
]

ROOT_URLCONF = 'Fifa_Tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['./templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'common_templatetags': 'common_templatetags.common_tags',
            },
        },
    },
]

WSGI_APPLICATION = 'Fifa_Tracker.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# DATABASES are located in "pro.py"


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

# Supported languages
LANGUAGES = (
    ('en', _('English')),
    ('pl', _('Polish')),
)
# Default language
LANGUAGE_CODE = 'en-us'

# Translation file
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

TIME_ZONE = 'Europe/Warsaw'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# LOGS
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filename=os.path.join(os.path.dirname(BASE_DIR), 'FIFA_TRACKER_LOGS.log'),
)

# Tests without migrations
RUN_MODE = sys.argv[1] if len(sys.argv) > 1 else None

if RUN_MODE == 'test':
    class DisableMigrations(dict):
        except_apps = {'app_to_run_migrations_for'}

        def __contains__(self, item):
            return item not in self.except_apps

        def __getitem__(self, item):
            return super(DisableMigrations, self).__getitem__(item) if item in self.except_apps else None

    MIGRATION_MODULES = DisableMigrations()

# Django Debug Toolbar
# https://django-debug-toolbar.readthedocs.io/en/stable/index.html#
'''
if DEBUG:
    INTERNAL_IPS = ('127.0.0.1', )
    INSTALLED_APPS += [
        'debug_toolbar',
    ]
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]
'''


# LastUserActivityMiddleware
LAST_ACTIVITY_INTERVAL_SECS = 30
