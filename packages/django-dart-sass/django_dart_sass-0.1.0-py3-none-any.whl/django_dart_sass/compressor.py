"""
Django Compressor Integration

This module provides django-compressor integration for Sass compilation
using the embedded Sass host with global function/importer support.
"""

import os
from typing import Dict, Any, Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    from compressor.filters import CompilerFilter
except ImportError:
    raise ImportError(
        "django-compressor is required for DartSassCompressor. "
        "Install it with: pip install django-compressor"
    )

from .registry import get_compile_options


class DartSassCompressor(CompilerFilter):
    """
    Django Compressor filter for Sass compilation using Dart Sass.
    
    This filter automatically includes all globally registered Sass functions
    and importers, making Django-specific functions like static() available
    in all Sass files.
    
    Usage in settings.py:
        COMPRESS_PRECOMPILERS = (
            ('text/x-scss', 'django_dart_sass.compressor.DartSassCompressor'),
        )
    """
    
    # Required by CompilerFilter but not used since we use Dart Sass directly
    command = 'dart-sass'
    
    def __init__(self, content: str, attrs: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(content, attrs, **kwargs)
        
        # Get Sass compilation options from Django settings
        self.sass_options = getattr(settings, 'SASS_DART_OPTIONS', {})
    
    def input(self, **kwargs) -> str:
        """
        Compile Sass content to CSS.
        
        Args:
            **kwargs: Additional arguments from django-compressor
            
        Returns:
            Compiled CSS content
        """
        import dart_sass
        
        # Get compile options with global functions/importers
        options = get_compile_options(self.sass_options)
        
        # Add load paths from Django settings
        load_paths = self._get_load_paths()
        if load_paths:
            existing_paths = options.get('load_paths', [])
            options['load_paths'] = existing_paths + load_paths
        
        try:
            # Compile the Sass content
            result = dart_sass.compile_string(self.content, options)
            return result.css
        except Exception as e:
            # Provide helpful error messages
            raise Exception(f"Sass compilation failed: {e}")
    
    def _get_load_paths(self) -> list:
        """Get Sass load paths from Django settings."""
        load_paths = []
        
        # Add paths from settings
        sass_load_paths = getattr(settings, 'SASS_LOAD_PATHS', [])
        load_paths.extend(sass_load_paths)
        
        # Add static files directories
        if hasattr(settings, 'STATICFILES_DIRS'):
            for static_dir in settings.STATICFILES_DIRS:
                if isinstance(static_dir, tuple):
                    # Handle (prefix, path) tuples
                    static_dir = static_dir[1]
                
                # Add sass/scss subdirectories if they exist
                for subdir in ['sass', 'scss', 'styles']:
                    sass_dir = os.path.join(static_dir, subdir)
                    if os.path.isdir(sass_dir):
                        load_paths.append(sass_dir)
        
        return load_paths
