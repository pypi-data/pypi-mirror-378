"""
Django App Configuration for django-dart-sass
"""

from django.apps import AppConfig


class DjangoSassEmbeddedConfig(AppConfig):
    """Django app configuration for dart-sass integration."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_dart_sass'
    verbose_name = 'Django Dart Sass'
    
    def ready(self):
        """Initialize the app when Django starts."""
        # Import functions module to trigger @sass_function decorators
        from . import functions
        
        # Import importers module to trigger @sass_importer decorators  
        from . import importers
