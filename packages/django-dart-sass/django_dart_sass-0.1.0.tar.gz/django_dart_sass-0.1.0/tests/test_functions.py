"""
Tests for Django Sass functions
"""

import pytest
from unittest.mock import patch

from dart_sass.value import SassString, SassArgumentList, SassNumber
from django_dart_sass.functions import static, theme_color, url_for, asset_url, media_url, setting


class TestDjangoSassFunctions:
    """Test Django-specific Sass functions."""
    
    def test_static_function_basic(self):
        """Test the static() function with basic usage."""
        args = SassArgumentList([SassString('images/logo.png')])
        result = static(args)
        
        assert isinstance(result, SassString)
        assert result.text.endswith('images/logo.png')
        assert result.has_quotes
        assert '/static/' in result.text
    
    def test_static_function_no_args(self):
        """Test static() function with no arguments."""
        args = SassArgumentList([])
        
        with pytest.raises(ValueError, match="requires a file path argument"):
            static(args)
    
    def test_static_function_non_string_arg(self):
        """Test static() function with non-string argument."""
        args = SassArgumentList([SassNumber(123)])
        
        with pytest.raises(ValueError, match="path must be a string"):
            static(args)
    
    def test_theme_color_function(self):
        """Test the theme-color() function."""
        args = SassArgumentList([SassString('test-color')])
        result = theme_color(args)
        
        assert isinstance(result, SassString)
        assert result.text == '#ff0000'
        assert not result.has_quotes  # Colors should not be quoted
    
    def test_theme_color_default_colors(self):
        """Test theme-color() with default colors."""
        args = SassArgumentList([SassString('primary')])
        result = theme_color(args)
        
        assert isinstance(result, SassString)
        assert result.text == '#007bff'
    
    def test_theme_color_unknown_color(self):
        """Test theme-color() with unknown color."""
        args = SassArgumentList([SassString('unknown-color')])
        
        with pytest.raises(ValueError, match="not found in SASS_THEME_COLORS"):
            theme_color(args)
    
    def test_url_for_function(self):
        """Test the url-for() function."""
        # Mock Django's reverse function
        with patch('django_dart_sass.functions.reverse') as mock_reverse:
            mock_reverse.return_value = '/api/users/'
            
            args = SassArgumentList([SassString('api:users')])
            result = url_for(args)
            
            assert isinstance(result, SassString)
            assert result.text == '/api/users/'
            assert result.has_quotes
            mock_reverse.assert_called_once_with('api:users')
    
    def test_url_for_function_no_reverse_match(self):
        """Test url-for() function with invalid URL name."""
        from django.urls import NoReverseMatch
        
        with patch('django_dart_sass.functions.reverse') as mock_reverse:
            mock_reverse.side_effect = NoReverseMatch("No reverse match")
            
            args = SassArgumentList([SassString('invalid:url')])
            
            with pytest.raises(ValueError, match="Could not reverse URL"):
                url_for(args)
    
    def test_asset_url_function(self):
        """Test the asset-url() function (alias for static)."""
        args = SassArgumentList([SassString('images/bg.jpg')])
        result = asset_url(args)
        
        assert isinstance(result, SassString)
        assert result.text.endswith('images/bg.jpg')
        assert result.has_quotes
    
    def test_media_url_function(self):
        """Test the media-url() function."""
        args = SassArgumentList([SassString('uploads/avatar.jpg')])
        result = media_url(args)
        
        assert isinstance(result, SassString)
        assert result.text == '/media/uploads/avatar.jpg'
        assert result.has_quotes
    
    def test_setting_function_boolean(self):
        """Test the setting() function with boolean setting."""
        from dart_sass.value import sass_true, sass_false
        from django.conf import settings
        
        args = SassArgumentList([SassString('DEBUG')])
        result = setting(args)
        
        # Should return the correct boolean singleton based on actual DEBUG value
        expected = sass_true if settings.DEBUG else sass_false
        assert result is expected
    
    def test_setting_function_string(self):
        """Test the setting() function with string setting."""
        args = SassArgumentList([SassString('SITE_NAME')])
        result = setting(args)
        
        assert isinstance(result, SassString)
        assert result.text == 'Django Dart Sass Test Site'
        assert result.has_quotes
    
    def test_setting_function_not_whitelisted(self):
        """Test setting() function with non-whitelisted setting."""
        args = SassArgumentList([SassString('SECRET_KEY')])
        
        with pytest.raises(ValueError, match="not whitelisted for Sass access"):
            setting(args)
    
    def test_setting_function_not_found(self):
        """Test setting() function with non-existent setting."""
        args = SassArgumentList([SassString('NONEXISTENT_SETTING')])
        
        with pytest.raises(ValueError, match="not whitelisted for Sass access"):
            setting(args)


class TestFunctionRegistration:
    """Test function registration and decorator patterns."""
    
    def test_sass_function_decorator(self):
        """Test the @sass_function decorator."""
        from django_dart_sass.decorators import sass_function, _global_functions
        
        @sass_function("test-function($arg)")
        def test_func(args):
            return SassString("test result")
        
        assert "test-function($arg)" in _global_functions
        assert _global_functions["test-function($arg)"] == test_func
    
    def test_register_function_manually(self):
        """Test manual function registration."""
        from django_dart_sass.decorators import register_function, _global_functions
        
        def test_func(args):
            return SassString("manual test")
        
        register_function("manual-function($arg)", test_func)
        
        assert "manual-function($arg)" in _global_functions
        assert _global_functions["manual-function($arg)"] == test_func
    
    def test_get_global_functions(self):
        """Test getting global functions."""
        from django_dart_sass.decorators import sass_function, get_global_functions
        
        @sass_function("get-test($arg)")
        def test_func(args):
            return SassString("get test")
        
        functions = get_global_functions()
        assert "get-test($arg)" in functions
        assert functions["get-test($arg)"] == test_func
        
        # Should return a copy, not the original
        functions["new-function"] = lambda: None
        original_functions = get_global_functions()
        assert "new-function" not in original_functions
