from .base import *

DEBUG = True


SECRET_KEY = os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PSQL_DB_NAME'),
        'USER': os.environ.get('PSQL_USER'),
        'PASSWORD': os.environ.get('PSQL_PASS'),
        'HOST': os.environ.get('PSQL_HOST'),
        'PORT': os.environ.get('PSQL_PORT'),
    }
}
