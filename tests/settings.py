# Bare ``settings.py`` for running tests for url_filter

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'url_filter.sqlite'
    }
}

INSTALLED_APPS = (
    'django_nose',
    'url_filter',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = (
    '--all-modules',
    '--with-doctest',
    '--with-coverage',
    '--cover-package=url_filter',
)

STATIC_URL = '/static/'
SECRET_KEY = 'foo'
