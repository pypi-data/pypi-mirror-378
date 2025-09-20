"""
Django Sass Importers

This module provides a unified Django Sass importer that handles both
standard Django include paths (like django_libsass) and app-specific imports.
"""

import os
from pathlib import Path
from typing import Optional, List

from django.conf import settings
from django.apps import apps
from django.contrib.staticfiles.finders import get_finders

try:
    from dart_sass.canonicalize_context import CanonicalizeContext
except ImportError:
    # Fallback definition if not available
    class CanonicalizeContext:
        def __init__(self, from_import: bool):
            self.from_import = from_import


# Import the decorator - do this after the try/except to avoid circular imports
from .decorators import sass_file_importer


@sass_file_importer
class DjangoImporter:
    """
    Unified Django Sass file importer.
    
    Handles both:
    1. App-specific imports: @import 'app:myapp/styles';
    2. Standard Django include paths: @import 'components/button';
    
    This works like django_libsass include paths but with additional
    app-specific import support.
    
    Uses the FileImporter interface (one method) - Sass automatically
    loads the file once we return the file:// URL.
    """
    
    def __init__(self):
        self._include_paths = None
    
    def find_file_url(self, url: str, context: CanonicalizeContext) -> Optional[str]:
        """
        Find a file URL for the given import.
        
        Priority order:
        1. App-specific imports (app:myapp/file)
        2. Django include paths (standard imports)
        
        Args:
            url: The import URL (e.g., 'components/button' or 'app:myapp/styles')
            context: Context about the canonicalization request
            
        Returns:
            File URL string (file://...) if found, None otherwise
        """
        # Skip URLs that are already absolute or have non-app schemes
        if '://' in url and not url.startswith('app:'):
            return None
        if not url.startswith('app:') and os.path.isabs(url):
            return None
        
        # 1. Try app-specific imports first
        if url.startswith('app:'):
            file_path = self._find_app_sass_file(url)
            if file_path:
                return file_path.as_uri()
        
        # 2. Fall back to Django include paths (standard imports)
        else:
            file_path = self._find_sass_file_in_include_paths(url)
            if file_path:
                return file_path.as_uri()
        
        return None
    
    def _find_app_sass_file(self, url: str) -> Optional[Path]:
        """
        Find a Sass file in a specific Django app.
        
        Args:
            url: App URL like 'app:myapp/styles'
            
        Returns:
            Path to the file if found, None otherwise
        """
        # Parse the URL: app:myapp/path/to/file
        try:
            _, app_path = url.split(':', 1)
            if '/' in app_path:
                app_name, file_path = app_path.split('/', 1)
            else:
                app_name = app_path
                file_path = 'main'  # Default file
        except ValueError:
            return None
        
        # Get the Django app
        try:
            app_config = apps.get_app_config(app_name)
        except LookupError:
            return None
        
        app_dir = Path(app_config.path)
        
        # Search locations within the app (prioritized order)
        search_paths = [
            # App static directory with app namespace (most common)
            app_dir / 'static' / app_name,
            # App static directory with app namespace and sass/scss subdirs
            app_dir / 'static' / app_name / 'sass',
            app_dir / 'static' / app_name / 'scss',
            # App static sass/scss directories
            app_dir / 'static' / 'sass',
            app_dir / 'static' / 'scss',
            # App-level sass/scss directories
            app_dir / 'sass',
            app_dir / 'scss',
            # App styles directory
            app_dir / 'styles',
        ]
        
        return self._search_for_sass_file(file_path, search_paths)
    
    def _find_sass_file_in_include_paths(self, url: str) -> Optional[Path]:
        """
        Find a Sass file in Django's include paths (like django_libsass).
        
        Args:
            url: Standard import URL like 'components/button'
            
        Returns:
            Path to the file if found, None otherwise
        """
        include_paths = self._get_include_paths()
        search_paths = [Path(path) for path in include_paths if Path(path).exists()]
        
        return self._search_for_sass_file(url, search_paths)
    
    def _search_for_sass_file(self, file_path: str, search_paths: List[Path]) -> Optional[Path]:
        """
        Search for a Sass file using standard Sass file resolution rules.
        
        Args:
            file_path: The file path to search for
            search_paths: List of directories to search in
            
        Returns:
            Path to the file if found, None otherwise
        """
        # File patterns to try (following Sass conventions)
        file_patterns = [
            f"{file_path}.scss",
            f"{file_path}.sass",
            f"_{file_path}.scss",      # Sass partials
            f"_{file_path}.sass",      # Sass partials
            f"{file_path}/index.scss", # Index files
            f"{file_path}/index.sass", # Index files
            f"{file_path}/_index.scss", # Partial index files
            f"{file_path}/_index.sass", # Partial index files
        ]
        
        # Search through all paths
        for search_path in search_paths:
            for pattern in file_patterns:
                full_path = search_path / pattern
                if full_path.exists() and full_path.is_file():
                    return full_path
        
        return None
    
    def _get_include_paths(self) -> List[str]:
        """
        Get Django include paths exactly like django_libsass does.
        
        Returns:
            List of include paths for Sass compilation
        """
        if self._include_paths is not None:
            return self._include_paths
        
        include_paths = []

        # Look for staticfile finders that define 'storages' (like django_libsass)
        for finder in get_finders():
            try:
                storages = finder.storages
            except AttributeError:
                continue

            for storage in storages.values():
                try:
                    include_paths.append(storage.path('.'))
                except NotImplementedError:
                    # storages that do not implement 'path' do not store files locally,
                    # and thus cannot provide an include path
                    pass

        # Add additional include paths from settings (like django_libsass)
        additional_paths = getattr(settings, 'SASS_ADDITIONAL_INCLUDE_PATHS', None)
        if additional_paths:
            include_paths.extend(additional_paths)
        
        # Also support the new setting name for consistency
        additional_paths = getattr(settings, 'SASS_DART_INCLUDE_PATHS', None)
        if additional_paths:
            include_paths.extend(additional_paths)

        self._include_paths = include_paths
        return include_paths


# Default Django importer instance
DJANGO_SASS_IMPORTER = DjangoImporter()

# For backward compatibility, provide as a list
DJANGO_SASS_IMPORTERS = [DJANGO_SASS_IMPORTER]


def get_django_importers() -> List[DjangoImporter]:
    """
    Get the list of Django importers to use.
    
    Returns:
        List containing the unified Django importer
    """
    return [DJANGO_SASS_IMPORTER]
