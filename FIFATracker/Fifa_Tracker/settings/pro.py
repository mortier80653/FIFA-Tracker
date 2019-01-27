from .base import *

DEBUG = env.bool('DEBUG', default=True)

SECRET_KEY = env.str('SECRET_KEY')

ALLOWED_HOSTS = tuple(env.list('ALLOWED_HOSTS', default=[]))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('PSQL_DB_NAME'),
        'USER': env.str('PSQL_USER'),
        'PASSWORD': env.str('PSQL_PASS'),
        'HOST': env.str('PSQL_HOST'),
        'PORT': env.int('PSQL_PORT'),
    }
}

SECURE_PROXY_SSL_HEADER = env.tuple('SECURE_PROXY_SSL_HEADER', default=None)
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=False)

EMAIL_SUBJECT_PREFIX = '[FIFA Tracker] '
EMAIL_BACKEND = env.str('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env.str('EMAIL_HOST', default='localhost')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False)
EMAIL_PORT = env.int('EMAIL_PORT', default=25)
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', default='webmaster@localhost')
