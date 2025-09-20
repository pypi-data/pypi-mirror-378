"""
Tests for django-compressor integration
"""

import pytest
from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock

# Skip all tests if django-compressor is not available
try:
    import compressor
    from django_dart_sass.compressor import DartSassCompressor
    COMPRESSOR_AVAILABLE = True
except ImportError:
    COMPRESSOR_AVAILABLE = False


@pytest.mark.skipif(not COMPRESSOR_AVAILABLE, reason="django-compressor not installed")
class TestDartSassCompressor(TestCase):
    """Test django-compressor integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scss_content = """
        $primary: #007bff;
        .test {
            color: $primary;
            background: url(static('images/bg.jpg'));
        }
        """
    
    def test_compressor_initialization(self):
        """Test that the compressor can be initialized."""
        compressor = DartSassCompressor(self.scss_content)
        self.assertEqual(compressor.content, self.scss_content)
    
    @override_settings(
        SASS_DART_OPTIONS={'style': 'compressed'},
        SASS_THEME_COLORS={'primary': '#ff0000'}
    )
    def test_compressor_with_settings(self):
        """Test compressor with Django settings."""
        compressor = DartSassCompressor(self.scss_content)
        self.assertEqual(compressor.sass_options['style'], 'compressed')
    
    @patch('django_dart_sass.compressor.get_compile_options')
    @patch('dart_sass.compile_string')
    def test_input_method(self, mock_compile, mock_get_options):
        """Test the input() method that compiles Sass."""
        # Mock the compilation result
        mock_result = MagicMock()
        mock_result.css = '.test { color: #007bff; }'
        mock_compile.return_value = mock_result
        
        # Mock compile options
        mock_get_options.return_value = {
            'functions': {'static($path)': lambda x: x},
            'importers': []
        }
        
        compressor = DartSassCompressor(self.scss_content)
        result = compressor.input()
        
        self.assertEqual(result, '.test { color: #007bff; }')
        mock_compile.assert_called_once()
        mock_get_options.assert_called_once()
    
    @override_settings(
        STATICFILES_DIRS=['/app/static'],
        SASS_LOAD_PATHS=['/app/sass']
    )
    def test_load_paths_from_settings(self):
        """Test that load paths are gathered from Django settings."""
        compressor = DartSassCompressor(self.scss_content)
        load_paths = compressor._get_load_paths()
        
        self.assertIn('/app/sass', load_paths)
    
    def test_load_paths_from_staticfiles_dirs(self):
        """Test load paths from STATICFILES_DIRS."""
        with override_settings(STATICFILES_DIRS=['/static1', '/static2']):
            compressor = DartSassCompressor(self.scss_content)
            
            with patch('os.path.isdir') as mock_isdir:
                mock_isdir.return_value = True
                load_paths = compressor._get_load_paths()
                
                # Should check for sass/scss subdirectories
                expected_calls = [
                    '/static1/sass',
                    '/static1/scss', 
                    '/static1/styles',
                    '/static2/sass',
                    '/static2/scss',
                    '/static2/styles'
                ]
                
                for expected_path in expected_calls:
                    self.assertTrue(any(expected_path in str(call) for call in mock_isdir.call_args_list))
    
    def test_load_paths_with_tuple_staticfiles_dirs(self):
        """Test load paths with tuple format STATICFILES_DIRS."""
        with override_settings(STATICFILES_DIRS=[('prefix', '/static/path')]):
            compressor = DartSassCompressor(self.scss_content)
            
            with patch('os.path.isdir') as mock_isdir:
                mock_isdir.return_value = True
                load_paths = compressor._get_load_paths()
                
                # Should use the path part of the tuple
                mock_isdir.assert_any_call('/static/path/sass')
    
    @patch('dart_sass.compile_string')
    def test_compilation_error_handling(self, mock_compile):
        """Test error handling during compilation."""
        mock_compile.side_effect = Exception("Sass compilation error")
        
        compressor = DartSassCompressor(self.scss_content)
        
        with self.assertRaises(Exception) as cm:
            compressor.input()
        
        self.assertIn("Sass compilation failed", str(cm.exception))
    
    def test_compressor_without_django_compressor(self):
        """Test that importing compressor without django-compressor fails gracefully."""
        # This test is more about the import structure
        import sys
        import importlib
        
        # Remove the compressor module from sys.modules if it exists
        compressor_modules = [key for key in sys.modules.keys() if key.startswith('compressor')]
        removed_modules = {}
        
        try:
            # Remove all compressor-related modules
            for module_name in compressor_modules:
                if module_name in sys.modules:
                    removed_modules[module_name] = sys.modules.pop(module_name)
            
            # Also remove our compressor module so it gets reimported
            if 'django_dart_sass.compressor' in sys.modules:
                removed_modules['django_dart_sass.compressor'] = sys.modules.pop('django_dart_sass.compressor')
            
            # Patch sys.modules to make compressor unavailable
            with patch.dict('sys.modules', {'compressor': None, 'compressor.filters': None, 'compressor.filters.base': None}):
                with self.assertRaises(ImportError):
                    # Force reimport of our compressor module
                    import django_dart_sass.compressor
                    importlib.reload(django_dart_sass.compressor)
        finally:
            # Restore the modules
            sys.modules.update(removed_modules)


@pytest.mark.skipif(COMPRESSOR_AVAILABLE, reason="Testing behavior when django-compressor is not available")
class TestCompressorNotAvailable(TestCase):
    """Test behavior when django-compressor is not available."""
    
    def test_lazy_import_error(self):
        """Test that DartSassCompressor raises proper error when not available."""
        with self.assertRaises(ImportError) as cm:
            from django_dart_sass import DartSassCompressor
        
        self.assertIn("django-compressor", str(cm.exception))
    
    def test_main_package_works_without_compressor(self):
        """Test that main package functionality works without django-compressor."""
        from django_dart_sass import static, sass_function
        
        # Should be able to import and use main functionality
        self.assertTrue(callable(static))
        self.assertTrue(callable(sass_function))


class TestCompressorIntegrationPatterns(TestCase):
    """Test common django-compressor usage patterns."""
    
    @pytest.mark.skipif(not COMPRESSOR_AVAILABLE, reason="django-compressor not installed")
    def test_template_tag_pattern(self):
        """Test the typical template tag usage pattern."""
        # This would typically be tested with Django template rendering
        # but we can test the compressor class directly
        
        scss_template = """
        {% load compress %}
        {% compress css %}
        <link rel="stylesheet" type="text/x-scss" href="{% static 'styles/main.scss' %}" />
        {% endcompress %}
        """
        
        # The actual SCSS content that would be processed
        scss_content = """
        @import 'bootstrap/variables';
        
        .header {
            background: theme-color('primary');
            padding: 1rem;
        }
        """
        
        with patch('dart_sass.compile_string') as mock_compile:
            mock_result = MagicMock()
            mock_result.css = '.header { background: #007bff; padding: 1rem; }'
            mock_compile.return_value = mock_result
            
            compressor = DartSassCompressor(scss_content)
            result = compressor.input()
            
            self.assertIn('.header', result)
            self.assertIn('#007bff', result)
    
    @pytest.mark.skipif(not COMPRESSOR_AVAILABLE, reason="django-compressor not installed")
    @override_settings(COMPRESS_PRECOMPILERS=(
        ('text/x-scss', 'django_dart_sass.compressor.DartSassCompressor'),
    ))
    def test_settings_configuration(self):
        """Test that the compressor can be configured via Django settings."""
        # This tests that our compressor class can be referenced in settings
        from django.conf import settings
        
        precompilers = dict(settings.COMPRESS_PRECOMPILERS)
        self.assertEqual(
            precompilers['text/x-scss'],
            'django_dart_sass.compressor.DartSassCompressor'
        )
