"""
Django Sass Registry

This module provides compile options integration for Django Sass functions and importers.
"""

from typing import Dict, List, Callable, Optional, Any

from dart_sass.value import SassArgumentList, Value

from django_dart_sass.decorators import get_global_functions, get_global_importers


def auto_register_django_functions() -> None:
    """
    Automatically register Django Sass functions and importers.
    
    This is called automatically when the Django app is ready.
    Functions are now auto-registered via decorators when functions.py is imported.
    The Django importer is auto-registered via decorator when importers.py is imported.
    
    This function now mainly serves to ensure the modules are imported.
    """
    # Import functions module to trigger decorator registration
    from . import functions
    
    # Import importers module to trigger decorator registration  
    from . import importers
    
    # Note: All registration now happens automatically via decorators!


def get_compile_options(additional_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get compile options with global functions and importers included.
    
    This is the main function used by the compressor and other integrations
    to get a complete set of compile options that includes all global registrations.
    
    Args:
        additional_options: Additional options to merge with global options
        
    Returns:
        Complete compile options dictionary
    """
    options = {}
    
def get_compile_options(additional_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get compile options with global functions and importers included.
    
    This merges:
    1. Global functions (from decorators) - always included
    2. Contextual functions (from options) - override global functions
    3. Global importers (from decorators) - always included  
    4. Contextual importers (from options) - prepended to global importers
    
    Args:
        additional_options: Additional options to merge with global options
        
    Returns:
        Complete compile options dictionary
    """
    options = {}
    
    # Start with global functions (decorator-registered)
    global_functions = get_global_functions()
    
    # Merge contextual functions (passed in options)
    all_functions = global_functions.copy()
    if additional_options and 'functions' in additional_options:
        contextual_functions = additional_options['functions']
        all_functions.update(contextual_functions)  # Contextual overrides global
    
    if all_functions:
        options['functions'] = all_functions
    
    # Add global importers
    global_importers = get_global_importers()
    if global_importers:
        options['importers'] = global_importers
    
    # Merge with additional options
    if additional_options:
        # Additional functions override global functions
        if 'functions' in additional_options:
            functions = options.get('functions', {}).copy()
            functions.update(additional_options['functions'])
            options['functions'] = functions
        
        # Additional importers come before global importers (higher priority)
        if 'importers' in additional_options:
            importers = additional_options['importers'].copy()
            importers.extend(options.get('importers', []))
            options['importers'] = importers
        
        # Merge other options
        for key, value in additional_options.items():
            if key not in ('functions', 'importers'):
                options[key] = value
    
    return options


# Convenience functions that match the python-dart-sass API
def compile_string(source: str, options: Optional[Dict[str, Any]] = None) -> Any:
    """
    Compile Sass string with global functions and importers.
    
    This is a convenience wrapper around dart_sass.compile_string
    that automatically includes global registrations.
    
    Args:
        source: Sass source code
        options: Additional compile options
        
    Returns:
        Compilation result
    """
    import dart_sass
    
    compile_options = get_compile_options(options)
    return dart_sass.compile_string(source, compile_options)


def compile_file(path: str, options: Optional[Dict[str, Any]] = None) -> Any:
    """
    Compile Sass file with global functions and importers.
    
    This is a convenience wrapper around dart_sass.compile
    that automatically includes global registrations.
    
    Args:
        path: Path to Sass file
        options: Additional compile options
        
    Returns:
        Compilation result
    """
    import dart_sass
    
    compile_options = get_compile_options(options)
    return dart_sass.compile(path, compile_options)


# Re-export decorator functions for convenience
from .decorators import (
    register_function,
    register_importer, 
    sass_function,
    sass_importer,
    sass_file_importer,
    clear_functions,
    clear_importers,
    clear_all,
)
