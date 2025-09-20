"""
End-to-end integration tests for django-dart-sass
"""

import pytest
import tempfile
from pathlib import Path
from django.test import TestCase, override_settings
from django.apps import apps
from unittest.mock import patch

from django_dart_sass.registry import compile_string, compile_file, get_compile_options
from django_dart_sass.decorators import sass_function, sass_file_importer, clear_all
from dart_sass.value import SassString, SassArgumentList


class TestEndToEndIntegration(TestCase):
    """Test complete end-to-end functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Clear any cached include paths from previous tests
        # This is needed because the global DjangoImporter caches paths
        # and we've added testapp to INSTALLED_APPS
        from django_dart_sass.decorators import get_global_importers
        for importer in get_global_importers():
            if hasattr(importer, '_include_paths'):
                importer._include_paths = None
    
    def test_basic_compilation_with_django_functions(self):
        """Test basic Sass compilation with Django functions."""
        scss_code = """
        .logo {
            background-image: url(static('images/logo.png'));
            color: theme-color('primary');
        }
        """
        
        result = compile_string(scss_code)
        
        self.assertIn('.logo', result['css'])
        self.assertIn('"/static/images/logo.png"', result['css'])  # URL is quoted in CSS
        self.assertIn('#007bff', result['css'])  # Default primary color
    
    @override_settings(SASS_THEME_COLORS={'custom': '#ff5722'})
    def test_compilation_with_custom_theme_colors(self):
        """Test compilation with custom theme colors from settings."""
        scss_code = """
        .custom-element {
            color: theme-color('custom');
        }
        """
        
        result = compile_string(scss_code)
        
        self.assertIn('#ff5722', result['css'])
    
    def test_compilation_with_custom_function(self):
        """Test compilation with custom registered function."""
        @sass_function("double($number)")
        def double_function(args):
            from dart_sass.value import SassNumber
            number = args[0].assert_number()
            return SassNumber(number.value * 2, number.unit)
        
        scss_code = """
        .test {
            width: double(10px);
        }
        """
        
        result = compile_string(scss_code)
        
        self.assertIn('width: 20px', result['css'])
    
    def test_compilation_with_custom_importer(self):
        """Test compilation with custom file importer."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = Path(temp_dir) / 'custom.scss'
            test_file.write_text('$imported-color: #00ff00;')
            
            @sass_file_importer
            class CustomImporter:
                def find_file_url(self, url, context):
                    if url == 'custom-import':
                        return test_file.as_uri()
                    return None
            
            scss_code = """
            @import 'custom-import';
            .test {
                color: $imported-color;
            }
            """
            
            result = compile_string(scss_code)
            
            self.assertIn('color: #00ff00', result['css'])
    
    def test_app_import_integration(self):
        """Test app: import functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock app structure
            app_dir = Path(temp_dir) / 'testapp'
            static_dir = app_dir / 'static' / 'testapp' / 'sass'
            static_dir.mkdir(parents=True)
            
            # Create test Sass file
            sass_file = static_dir / 'variables.scss'
            sass_file.write_text('$app-color: #purple;')
            
            # Mock Django app
            mock_app_config = type('MockAppConfig', (), {'path': str(app_dir)})()
            
            with patch('django.apps.apps.get_app_config') as mock_get_app:
                mock_get_app.return_value = mock_app_config
                
                # Create a contextual importer for this test
                from django_dart_sass.importers import DjangoImporter
                test_importer = DjangoImporter()
                
                scss_code = """
                @import 'app:testapp/variables';
                .app-element {
                    color: $app-color;
                }
                """
                
                # Use contextual importer instead of global one
                result = compile_string(scss_code, {
                    'importers': [test_importer]
                })
                
                self.assertIn('color: #purple', result['css'])
    
    def test_file_compilation(self):
        """Test compiling from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.scss', delete=False) as f:
            f.write("""
            .file-test {
                background: theme-color('secondary');
                padding: 1rem;
            }
            """)
            temp_file = f.name
        
        try:
            result = compile_file(temp_file)
            
            self.assertIn('.file-test', result['css'])
            self.assertIn('#6c757d', result['css'])  # Default secondary color
        finally:
            Path(temp_file).unlink()
    
    def test_compile_options_merging(self):
        """Test that compile options are properly merged."""
        @sass_function("test-func($arg)")
        def test_func(args):
            return SassString("from-global")
        
        # Test with additional options
        additional_options = {
            'style': 'compressed',
            'functions': {
                'local-func($arg)': lambda args: SassString("from-local")
            }
        }
        
        options = get_compile_options(additional_options)
        
        # Should have both global and local functions
        self.assertIn('test-func($arg)', options['functions'])
        self.assertIn('local-func($arg)', options['functions'])
        
        # Should have additional options
        self.assertEqual(options['style'], 'compressed')
    
    def test_function_override_priority(self):
        """Test that local functions override global functions."""
        @sass_function("override-test($arg)")
        def global_func(args):
            return SassString("global")
        
        def local_func(args):
            return SassString("local")
        
        additional_options = {
            'functions': {
                'override-test($arg)': local_func
            }
        }
        
        options = get_compile_options(additional_options)
        
        # Local function should override global
        self.assertEqual(options['functions']['override-test($arg)'], local_func)
    
    def test_importer_priority(self):
        """Test that local importers have higher priority than global importers."""
        @sass_file_importer
        class GlobalImporter:
            def find_file_url(self, url, context):
                return None
        
        class LocalImporter:
            def find_file_url(self, url, context):
                return None
        
        local_importer = LocalImporter()
        additional_options = {
            'importers': [local_importer]
        }
        
        options = get_compile_options(additional_options)
        
        # Local importer should come first
        self.assertEqual(options['importers'][0], local_importer)
        # Should have at least 2 importers (local + global ones)
        self.assertGreaterEqual(len(options['importers']), 2)
    
    @override_settings(
        SASS_THEME_COLORS={'integration': '#123456'},
        STATIC_URL='/assets/',
        MEDIA_URL='/uploads/'
    )
    def test_full_django_integration(self):
        """Test full integration with Django settings and functions."""
        scss_code = """
        $theme: theme-color('integration');
        
        .full-integration {
            color: $theme;
            background-image: url(static('bg.jpg'));
            content: url(media-url('avatar.png'));
        }
        """
        
        result = compile_string(scss_code)
        css = result['css']
        
        self.assertIn('color: #123456', css)
        self.assertIn('/assets/bg.jpg', css)
        self.assertIn('/uploads/avatar.png', css)
    
    def test_error_handling(self):
        """Test error handling in compilation."""
        # Invalid Sass syntax
        invalid_scss = """
        .test {
            color: $undefined-variable;
        }
        """
        
        with self.assertRaises(Exception):
            compile_string(invalid_scss)
    
    def test_multiple_compilations_with_global_state(self):
        """Test that global state persists across multiple compilations."""
        @sass_function("persistent-func($arg)")
        def persistent_func(args):
            return SassString("persistent")
        
        # First compilation
        result1 = compile_string('.test1 { content: persistent-func(1); }')
        self.assertIn('content: "persistent"', result1['css'])
        
        # Second compilation should still have the function
        result2 = compile_string('.test2 { content: persistent-func(2); }')
        self.assertIn('content: "persistent"', result2['css'])
    
    def test_django_app_ready_integration(self):
        """Test that Django functions are registered when app is ready."""
        # This tests the apps.py integration
        from django_dart_sass.decorators import _global_functions
        
        # Django functions should be automatically registered
        expected_functions = [
            'static($path)',
            'theme-color($name)',
            'url-for($name)',
            'asset-url($path)',
            'media-url($path)',
            'setting($name)'
        ]
        
        for func_sig in expected_functions:
            self.assertIn(func_sig, _global_functions)


class TestRealWorldUsagePatterns(TestCase):
    """Test real-world usage patterns similar to popular Sass packages."""
    
    def test_bootstrap_like_usage(self):
        """Test Bootstrap-like variable and function usage."""
        scss_code = """
        // Bootstrap-like theme colors
        $primary: theme-color('primary');
        $secondary: theme-color('secondary');
        
        // Component styles
        .btn {
            padding: 0.375rem 0.75rem;
            border: 1px solid transparent;
            
            &.btn-primary {
                background-color: $primary;
                border-color: $primary;
            }
            
            &.btn-secondary {
                background-color: $secondary;
                border-color: $secondary;
            }
        }
        """
        
        result = compile_string(scss_code)
        css = result['css']
        
        self.assertIn('.btn', css)
        self.assertIn('.btn-primary', css)
        self.assertIn('.btn-secondary', css)
        self.assertIn('#007bff', css)  # Primary color
        self.assertIn('#6c757d', css)  # Secondary color
    
    def test_component_library_pattern(self):
        """Test component library pattern with imports and functions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create component files
            base_dir = Path(temp_dir)
            
            # Variables file
            variables_file = base_dir / '_variables.scss'
            variables_file.write_text("""
            $component-padding: 1rem;
            $component-margin: 0.5rem;
            """)
            
            # Button component
            button_file = base_dir / '_button.scss'
            button_file.write_text("""
            .btn {
                padding: $component-padding;
                margin: $component-margin;
                background: theme-color('primary');
            }
            """)
            
            # Create a contextual importer for this test
            from django_dart_sass.importers import DjangoImporter
            test_importer = DjangoImporter()
            
            # Mock the include paths for this specific importer instance
            with patch.object(test_importer, '_get_include_paths') as mock_paths:
                mock_paths.return_value = [str(base_dir)]
                
                scss_code = """
                @import 'variables';
                @import 'button';
                
                .custom-btn {
                    @extend .btn;
                    border-radius: 0.25rem;
                }
                """
                
                # Use contextual importer instead of global one
                result = compile_string(scss_code, {
                    'importers': [test_importer]
                })
                css = result['css']
                
                self.assertIn('.btn', css)
                self.assertIn('.custom-btn', css)
                self.assertIn('padding: 1rem', css)
                self.assertIn('#007bff', css)
    
    def test_django_cms_like_pattern(self):
        """Test Django CMS-like dynamic styling pattern."""
        @sass_function("cms-setting($key)")
        def cms_setting(args):
            key = args[0].assert_string().text
            # Simulate CMS settings
            cms_settings = {
                'header-height': '60px',
                'sidebar-width': '250px', 
                'brand-color': '#e74c3c'
            }
            # Return unquoted for CSS values
            return SassString(cms_settings.get(key, 'inherit'), quoted=False)
        
        scss_code = """
        .cms-header {
            height: cms-setting('header-height');
            background: cms-setting('brand-color');
        }
        
        .cms-sidebar {
            width: cms-setting('sidebar-width');
        }
        """
        
        result = compile_string(scss_code)
        css = result['css']
        
        self.assertIn('height: 60px', css)
        self.assertIn('width: 250px', css)
        self.assertIn('background: #e74c3c', css)
