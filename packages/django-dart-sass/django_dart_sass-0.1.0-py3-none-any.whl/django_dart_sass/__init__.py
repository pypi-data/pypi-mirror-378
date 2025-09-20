"""
Django Dart Sass - Django integration for Python Dart Sass

This package provides Django integration for the Python Dart Sass package,
including django-compressor support and global Sass function/importer registries.
"""

__version__ = "0.1.0"
__author__ = "Harvey McQueen"
__email__ = "hmcqueen@gmail.com"

# Import main functionality
from .functions import static, url_for, asset_url
from .decorators import register_function, register_importer, sass_function, sass_importer, sass_file_importer

__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__email__",
    
    # Django Sass functions
    "static",
    "url_for", 
    "asset_url",
    
    # Registry functions
    "register_function",
    "register_importer",
    "sass_function",
    "sass_importer",
    "sass_file_importer",
]


def __getattr__(name):
    """
    Lazy import for optional components.
    
    This allows importing DartSassCompressor only when needed,
    avoiding ImportError when django-compressor is not installed.
    """
    if name == "DartSassCompressor":
        try:
            from .compressor import DartSassCompressor
            return DartSassCompressor
        except ImportError:
            raise ImportError(
                "DartSassCompressor requires django-compressor. "
                "Install it with: pip install django-compressor"
            )
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
