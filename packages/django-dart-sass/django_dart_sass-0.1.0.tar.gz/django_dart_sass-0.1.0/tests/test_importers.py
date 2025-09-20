"""
Tests for Django Sass importers
"""

import pytest
import tempfile
import os
from pathlib import Path
from django.test import TestCase, override_settings
from django.apps import apps
from unittest.mock import patch, MagicMock

from django_dart_sass.importers import DjangoImporter

try:
    from dart_sass.canonicalize_context import CanonicalizeContext
except ImportError:
    # Fallback for testing
    class CanonicalizeContext:
        def __init__(self, containing_url=None, from_import=False):
            self.containing_url = containing_url
            self.from_import = from_import


class TestDjangoImporter(TestCase):
    """Test the unified Django importer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.importer = DjangoImporter()
        self.context = CanonicalizeContext(from_import=False)
    
    def test_skip_absolute_urls(self):
        """Test that absolute URLs are skipped."""
        result = self.importer.find_file_url('http://example.com/style.css', self.context)
        self.assertIsNone(result)
        
        result = self.importer.find_file_url('https://example.com/style.css', self.context)
        self.assertIsNone(result)
    
    def test_skip_absolute_paths(self):
        """Test that absolute file paths are skipped."""
        result = self.importer.find_file_url('/absolute/path/style.scss', self.context)
        self.assertIsNone(result)
    
    def test_app_import_invalid_format(self):
        """Test app imports with invalid format."""
        result = self.importer.find_file_url('app:', self.context)
        self.assertIsNone(result)
        
        result = self.importer.find_file_url('app:invalid:format', self.context)
        self.assertIsNone(result)
    
    def test_app_import_nonexistent_app(self):
        """Test app imports with non-existent Django app."""
        result = self.importer.find_file_url('app:nonexistent/styles', self.context)
        self.assertIsNone(result)
    
    def test_app_import_with_mock_app(self):
        """Test app imports with mocked Django app."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file structure
            app_dir = Path(temp_dir) / 'testapp'
            static_dir = app_dir / 'static' / 'testapp'
            static_dir.mkdir(parents=True)
            
            test_file = static_dir / 'styles.scss'
            test_file.write_text('$color: blue; .test { color: $color; }')
            
            # Mock Django app config
            mock_app_config = MagicMock()
            mock_app_config.path = str(app_dir)
            
            with patch('django.apps.apps.get_app_config') as mock_get_app:
                mock_get_app.return_value = mock_app_config
                
                result = self.importer.find_file_url('app:testapp/styles', self.context)
                
                self.assertIsNotNone(result)
                self.assertTrue(result.startswith('file://'))
                self.assertTrue(result.endswith('styles.scss'))
    
    def test_standard_import_with_include_paths(self):
        """Test standard imports using Django include paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file = Path(temp_dir) / 'components' / 'button.scss'
            test_file.parent.mkdir(parents=True)
            test_file.write_text('.button { padding: 10px; }')
            
            # Mock include paths
            with patch.object(self.importer, '_get_include_paths') as mock_paths:
                mock_paths.return_value = [temp_dir]
                
                result = self.importer.find_file_url('components/button', self.context)
                
                self.assertIsNotNone(result)
                self.assertTrue(result.startswith('file://'))
                self.assertTrue(result.endswith('button.scss'))
    
    def test_sass_partial_files(self):
        """Test that Sass partial files are found correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create partial file
            partial_file = Path(temp_dir) / '_variables.scss'
            partial_file.write_text('$primary: #007bff;')
            
            with patch.object(self.importer, '_get_include_paths') as mock_paths:
                mock_paths.return_value = [temp_dir]
                
                result = self.importer.find_file_url('variables', self.context)
                
                self.assertIsNotNone(result)
                self.assertTrue(result.endswith('_variables.scss'))
    
    def test_index_files(self):
        """Test that index files are found correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create index file
            index_dir = Path(temp_dir) / 'components'
            index_dir.mkdir()
            index_file = index_dir / 'index.scss'
            index_file.write_text('@import "button"; @import "form";')
            
            with patch.object(self.importer, '_get_include_paths') as mock_paths:
                mock_paths.return_value = [temp_dir]
                
                result = self.importer.find_file_url('components', self.context)
                
                self.assertIsNotNone(result)
                self.assertTrue(result.endswith('index.scss'))
    
    def test_sass_vs_scss_priority(self):
        """Test file extension priority (.scss vs .sass)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create both .scss and .sass files
            scss_file = Path(temp_dir) / 'test.scss'
            sass_file = Path(temp_dir) / 'test.sass'
            
            scss_file.write_text('.test { color: blue; }')
            sass_file.write_text('.test\n  color: red')
            
            with patch.object(self.importer, '_get_include_paths') as mock_paths:
                mock_paths.return_value = [temp_dir]
                
                result = self.importer.find_file_url('test', self.context)
                
                self.assertIsNotNone(result)
                # Should prefer .scss over .sass
                self.assertTrue(result.endswith('test.scss'))
    
    @override_settings(SASS_ADDITIONAL_INCLUDE_PATHS=['/custom/path'])
    def test_additional_include_paths_setting(self):
        """Test SASS_ADDITIONAL_INCLUDE_PATHS setting."""
        with patch('django.contrib.staticfiles.finders.get_finders') as mock_finders:
            mock_finders.return_value = []
            
            paths = self.importer._get_include_paths()
            
            self.assertIn('/custom/path', paths)
    
    @override_settings(SASS_DART_INCLUDE_PATHS=['/embedded/path'])
    def test_embedded_include_paths_setting(self):
        """Test SASS_DART_INCLUDE_PATHS setting."""
        with patch('django.contrib.staticfiles.finders.get_finders') as mock_finders:
            mock_finders.return_value = []
            
            paths = self.importer._get_include_paths()
            
            self.assertIn('/embedded/path', paths)
    
    def test_include_paths_caching(self):
        """Test that include paths are cached."""
        with patch('django_dart_sass.importers.get_finders') as mock_finders:
            mock_finders.return_value = []
            
            # First call
            paths1 = self.importer._get_include_paths()
            
            # Second call should use cached result
            paths2 = self.importer._get_include_paths()
            
            self.assertEqual(paths1, paths2)
            # get_finders should only be called once due to caching
            self.assertEqual(mock_finders.call_count, 1)


class TestImporterRegistration(TestCase):
    """Test importer registration and decorator patterns."""
    
    def setUp(self):
        """Clear global importers before each test."""
        from django_dart_sass.decorators import clear_importers
        clear_importers()
    
    def tearDown(self):
        """Clear global importers after each test."""
        from django_dart_sass.decorators import clear_importers
        clear_importers()
    
    def test_sass_file_importer_decorator(self):
        """Test the @sass_file_importer decorator."""
        from django_dart_sass.decorators import sass_file_importer, _global_importers
        
        @sass_file_importer
        class TestFileImporter:
            def find_file_url(self, url, context):
                if url.startswith('test:'):
                    return f'file:///test/{url[5:]}.scss'
                return None
        
        self.assertEqual(len(_global_importers), 1)
        self.assertIsInstance(_global_importers[0], TestFileImporter)
    
    def test_sass_importer_decorator(self):
        """Test the @sass_importer decorator."""
        from django_dart_sass.decorators import sass_importer, _global_importers
        
        @sass_importer
        class TestImporter:
            def canonicalize(self, url, context):
                if url.startswith('custom:'):
                    return f'file:///custom/{url[7:]}.scss'
                return None
            
            def load(self, canonical_url):
                return {'contents': '.test { color: red; }', 'syntax': 'scss'}
        
        self.assertEqual(len(_global_importers), 1)
        self.assertIsInstance(_global_importers[0], TestImporter)
    
    def test_register_importer_manually(self):
        """Test manual importer registration."""
        from django_dart_sass.decorators import register_importer, _global_importers
        
        class ManualImporter:
            def find_file_url(self, url, context):
                return None
        
        importer = ManualImporter()
        register_importer(importer)
        
        self.assertEqual(len(_global_importers), 1)
        self.assertEqual(_global_importers[0], importer)
    
    def test_get_global_importers(self):
        """Test getting global importers."""
        from django_dart_sass.decorators import sass_file_importer, get_global_importers
        
        @sass_file_importer
        class GetTestImporter:
            def find_file_url(self, url, context):
                return None
        
        importers = get_global_importers()
        self.assertEqual(len(importers), 1)
        self.assertIsInstance(importers[0], GetTestImporter)
        
        # Should return a copy, not the original
        importers.append("fake_importer")
        original_importers = get_global_importers()
        self.assertEqual(len(original_importers), 1)
