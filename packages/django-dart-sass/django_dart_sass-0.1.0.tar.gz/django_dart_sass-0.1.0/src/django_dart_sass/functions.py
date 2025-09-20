"""
Django Sass Functions

This module provides Django-specific Sass functions that can be used in Sass/SCSS files
to integrate with Django's static file handling, URL routing, and other Django features.
"""

import os
from typing import List, Optional
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse, NoReverseMatch
from django.utils.html import escape

from dart_sass.value import SassString, SassNumber, SassArgumentList, Value

# Import the decorator
from .decorators import sass_function


@sass_function('static($path)')
def static(args: SassArgumentList) -> SassString:
    """
    Django static() function for Sass.
    
    Usage in Sass:
        background-image: url(static('images/logo.png'));
        // Outputs: background-image: url('/static/images/logo.png');
    
    Args:
        args: Sass argument list containing the static file path
        
    Returns:
        SassString with the full static URL
        
    Raises:
        ValueError: If no path argument provided or path is not a string
    """
    if len(args) == 0:
        raise ValueError("static() function requires a file path argument")
    
    path_arg = args[0]
    if not isinstance(path_arg, SassString):
        raise ValueError("static() function path must be a string")
    
    # Get the file path from the Sass string
    file_path = path_arg.text
    
    # Use Django's static file storage to get the URL
    try:
        static_url = staticfiles_storage.url(file_path)
    except ValueError as e:
        # Handle cases where the file doesn't exist or other storage errors
        # Fall back to manual URL construction
        static_url = urljoin(settings.STATIC_URL or '/static/', file_path)
    
    # Return as quoted string (URLs should be quoted in CSS)
    return SassString(static_url, quoted=True)


@sass_function('url-for($name)')
def url_for(args: SassArgumentList) -> SassString:
    """
    Django URL reverse function for Sass.
    
    Usage in Sass:
        $api_endpoint: url-for('api:users');
        // Outputs: $api_endpoint: '/api/users/';
    
    Args:
        args: Sass argument list containing the URL name and optional arguments
        
    Returns:
        SassString with the reversed URL
        
    Raises:
        ValueError: If URL name not provided or reverse fails
    """
    if len(args) == 0:
        raise ValueError("url-for() function requires a URL name argument")
    
    url_name_arg = args[0]
    if not isinstance(url_name_arg, SassString):
        raise ValueError("url-for() function URL name must be a string")
    
    url_name = url_name_arg.text
    
    # TODO: Support URL arguments in future versions
    # For now, only support simple URL names without arguments
    
    try:
        url = reverse(url_name)
    except NoReverseMatch as e:
        raise ValueError(f"Could not reverse URL '{url_name}': {e}")
    
    # Return as quoted string
    return SassString(url, quoted=True)


@sass_function('asset-url($path)')
def asset_url(args: SassArgumentList) -> SassString:
    """
    Generic asset URL function for Sass.
    
    This is an alias for static() but can be extended for other asset types
    like media files, CDN assets, etc.
    
    Usage in Sass:
        background: url(asset-url('images/bg.jpg'));
        // Outputs: background: url('/static/images/bg.jpg');
    
    Args:
        args: Sass argument list containing the asset path
        
    Returns:
        SassString with the full asset URL
    """
    # For now, this is just an alias for static()
    # In the future, this could be extended to handle different asset types
    return static(args)


@sass_function('media-url($path)')
def media_url(args: SassArgumentList) -> SassString:
    """
    Django media URL function for Sass.
    
    Usage in Sass:
        background-image: url(media-url('uploads/avatar.jpg'));
        // Outputs: background-image: url('/media/uploads/avatar.jpg');
    
    Args:
        args: Sass argument list containing the media file path
        
    Returns:
        SassString with the full media URL
    """
    if len(args) == 0:
        raise ValueError("media-url() function requires a file path argument")
    
    path_arg = args[0]
    if not isinstance(path_arg, SassString):
        raise ValueError("media-url() function path must be a string")
    
    file_path = path_arg.text
    
    # Construct media URL
    media_url = urljoin(settings.MEDIA_URL or '/media/', file_path)
    
    # Return as quoted string
    return SassString(media_url, quoted=True)


@sass_function('theme-color($name)')
def theme_color(args: SassArgumentList) -> SassString:
    """
    Django theme color function for Sass.
    
    This function can be used to access theme colors defined in Django settings.
    
    Usage in Sass:
        color: theme-color('primary');
        // Outputs: color: #007bff; (or whatever is defined in settings)
    
    Args:
        args: Sass argument list containing the color name
        
    Returns:
        SassString with the color value
        
    Raises:
        ValueError: If color name not provided or not found
    """
    if len(args) == 0:
        raise ValueError("theme-color() function requires a color name argument")
    
    color_name_arg = args[0]
    if not isinstance(color_name_arg, SassString):
        raise ValueError("theme-color() function color name must be a string")
    
    color_name = color_name_arg.text
    
    # Get theme colors from Django settings
    theme_colors = getattr(settings, 'SASS_THEME_COLORS', {})
    
    # Handle None setting (convert to empty dict)
    if theme_colors is None:
        theme_colors = {}
    
    if color_name not in theme_colors:
        # Provide some sensible defaults
        default_colors = {
            'primary': '#007bff',
            'secondary': '#6c757d',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
        }
        
        if color_name in default_colors:
            color_value = default_colors[color_name]
        else:
            raise ValueError(f"Theme color '{color_name}' not found in SASS_THEME_COLORS setting")
    else:
        color_value = theme_colors[color_name]
    
    # Return as unquoted string (colors don't need quotes)
    return SassString(color_value, quoted=False)


@sass_function('setting($name)')
def setting(args: SassArgumentList) -> Value:
    """
    Django setting access function for Sass.
    
    This function allows accessing Django settings from Sass files.
    Only allows access to settings that are explicitly whitelisted for security.
    
    Usage in Sass:
        $debug: setting('DEBUG');
        $site_name: setting('SITE_NAME');
    
    Args:
        args: Sass argument list containing the setting name
        
    Returns:
        Appropriate Sass value based on the setting type
        
    Raises:
        ValueError: If setting name not provided or not whitelisted
    """
    if len(args) == 0:
        raise ValueError("setting() function requires a setting name argument")
    
    setting_name_arg = args[0]
    if not isinstance(setting_name_arg, SassString):
        raise ValueError("setting() function setting name must be a string")
    
    setting_name = setting_name_arg.text
    
    # Whitelist of settings that are safe to expose to Sass
    # This prevents accidental exposure of sensitive settings
    whitelisted_settings = getattr(settings, 'SASS_ALLOWED_SETTINGS', [
        'DEBUG',
        'SITE_NAME',
        'SITE_TITLE',
        'BRAND_NAME',
        'VERSION',
        'ENVIRONMENT',
    ])
    
    if setting_name not in whitelisted_settings:
        raise ValueError(f"Setting '{setting_name}' is not whitelisted for Sass access")
    
    try:
        setting_value = getattr(settings, setting_name)
    except AttributeError:
        raise ValueError(f"Setting '{setting_name}' not found")
    
    # Convert Python value to appropriate Sass value
    if isinstance(setting_value, bool):
        from dart_sass.value import sass_true, sass_false
        return sass_true if setting_value else sass_false
    elif isinstance(setting_value, (int, float)):
        return SassNumber(setting_value)
    elif isinstance(setting_value, str):
        return SassString(setting_value, quoted=True)
    else:
        # For other types, convert to string
        return SassString(str(setting_value), quoted=True)
