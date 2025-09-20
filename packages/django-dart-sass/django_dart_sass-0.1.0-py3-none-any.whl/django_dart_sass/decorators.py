"""
Django Sass Decorators

This module provides decorators for registering Sass functions and importers
that can be used across all Sass compilations in a Django project.
"""

from typing import Dict, List, Callable

# Global registries
_global_functions: Dict[str, Callable] = {}
_global_importers: List[Callable] = []


def register_function(signature: str, function: Callable) -> None:
    """
    Register a global Sass function.
    
    Args:
        signature: The Sass function signature (e.g., "my-function($arg1, $arg2)")
        function: The Python function that implements the Sass function
        
    Example:
        def my_function(args):
            return SassString("Hello World")
        
        register_function("my-function()", my_function)
        
    Raises:
        ValueError: If the signature is invalid (missing parentheses)
    """
    # Validate signature
    if '(' not in signature:
        raise ValueError(f'Sass function signature "{signature}" is missing "("')
    
    _global_functions[signature] = function


def register_importer(importer: Callable) -> None:
    """
    Register a global Sass importer.
    
    Args:
        importer: The Python importer instance that implements the Sass importer
        
    Example:
        class MyImporter:
            def find_file_url(self, url, context):
                return f'file:///path/to/{url}.scss'
        
        register_importer(MyImporter())
    """
    _global_importers.append(importer)


def sass_function(signature: str):
    """
    Decorator to register a global Sass function.
    
    Args:
        signature: The Sass function signature
        
    Example:
        @sass_function("my-function($arg)")
        def my_function(args):
            return SassString("Hello World")
            
    Raises:
        ValueError: If the signature is invalid (missing parentheses)
    """
    def decorator(func):
        # Validate signature before registering
        if '(' not in signature:
            raise ValueError(f'Sass function signature "{signature}" is missing "("')
        
        register_function(signature, func)
        return func
    return decorator


def sass_importer(cls):
    """
    Decorator to register a global Sass importer class.
    
    For two-method importers (canonicalize + load).
    
    Example:
        @sass_importer
        class MyImporter:
            def canonicalize(self, url, context):
                if url.startswith('theme:'):
                    return f'file:///themes/{url[6:]}.scss'
                return None
            
            def load(self, canonical_url):
                # Load file and return ImporterResult
                return ImporterResult(contents="...", syntax='scss')
    """
    # Register an instance of the class
    register_importer(cls())
    return cls


def sass_file_importer(cls):
    """
    Decorator to register a global Sass FileImporter class.
    
    For one-method importers (find_file_url).
    
    Example:
        @sass_file_importer
        class MyFileImporter:
            def find_file_url(self, url, context):
                if url.startswith('custom:'):
                    return f'file:///path/to/{url[7:]}.scss'
                return None
    """
    # Register an instance of the class
    register_importer(cls())
    return cls


def clear_functions() -> None:
    """
    Clear all registered global functions.
    
    This is mainly useful for testing.
    """
    _global_functions.clear()


def clear_importers() -> None:
    """
    Clear all registered global importers.
    
    This is mainly useful for testing.
    """
    _global_importers.clear()


def clear_all() -> None:
    """
    Clear all registered global functions and importers.
    
    This is mainly useful for testing.
    """
    clear_functions()
    clear_importers()


def get_global_functions() -> Dict[str, Callable]:
    """
    Get all registered global functions.
    
    Returns:
        Dictionary of function signatures to function implementations
    """
    return _global_functions.copy()


def get_global_importers() -> List[Callable]:
    """
    Get all registered global importers.
    
    Returns:
        List of importer instances
    """
    return _global_importers.copy()
