"""
Django settings for testing django-dart-sass
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'test-secret-key-for-django-dart-sass'

DEBUG = True

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'django_dart_sass',
    'tests.testapp',
]

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'tests' / 'static',
]

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Sass configuration for testing
SASS_THEME_COLORS = {
    'primary': '#007bff',
    'secondary': '#6c757d',
    'success': '#28a745',
    'danger': '#dc3545',
    'warning': '#ffc107',
    'info': '#17a2b8',
    'test-color': '#ff0000',
}

SASS_LOAD_PATHS = [
    BASE_DIR / 'tests' / 'sass',
]

SASS_ADDITIONAL_INCLUDE_PATHS = [
    BASE_DIR / 'tests' / 'additional_sass',
]

SASS_DART_INCLUDE_PATHS = [
    BASE_DIR / 'tests' / 'embedded_sass',
]

SASS_DART_OPTIONS = {
    'style': 'expanded',
    'source_map': False,
}

# Settings that can be accessed via setting() function
SASS_ALLOWED_SETTINGS = [
    'DEBUG',
    'SITE_NAME',
    'SITE_TITLE',
    'BRAND_NAME',
    'VERSION',
    'ENVIRONMENT',
]

# Test-specific settings
SITE_NAME = 'Django Dart Sass Test Site'
SITE_TITLE = 'Test Site'
BRAND_NAME = 'Test Brand'
VERSION = '1.0.0'
ENVIRONMENT = 'test'

# Django compressor settings (if available)
COMPRESS_ENABLED = True
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_dart_sass.compressor.DartSassCompressor'),
)

USE_TZ = True

# Database (required by Django, even if not used)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
