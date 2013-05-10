"""
Test Configuration
"""
SECRET_KEY = "desabamento-na-obra-da-arena-palestra-mata-uma-pessoa"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.admin',
    'marimo_comments',
    'example',
)

SHORT_CACHE_TIMEOUT = 60  # One Minute
LOGIN_URL = '/auth/signin/'

TEMPLATE_DIRS = (
    'marimo_comments/templates',
)

MARIMO_TEMPLATE_DIRS = (
     'marimo_comments/templates',
)