"""
Performance and edge case tests for django-dart-sass
"""

import pytest
import time
import threading
from django.test import TestCase, override_settings
from unittest.mock import patch

from django_dart_sass.registry import compile_string
from django_dart_sass.decorators import sass_function, clear_all
from dart_sass.value import SassString


class TestPerformance(TestCase):
    """Test performance characteristics."""
    
    def test_function_registration_performance(self):
        """Test that function registration is fast."""
        start_time = time.time()
        
        # Register many functions
        for i in range(100):
            @sass_function(f"test-func-{i}($arg)")
            def test_func(args):
                return SassString(f"result-{i}")
        
        end_time = time.time()
        registration_time = end_time - start_time
        
        # Should register 100 functions in less than 1 second
        self.assertLess(registration_time, 1.0)
    
    def test_compilation_caching(self):
        """Test that include paths are cached for performance."""
        from django_dart_sass.importers import DjangoImporter
        
        # Create importer once to test caching
        importer = DjangoImporter()
        
        # Mock get_finders where it's imported in the importers module
        with patch('django_dart_sass.importers.get_finders') as mock_finders:
            mock_finders.return_value = []
            
            # First call should call get_finders
            start_time = time.time()
            paths1 = importer._get_include_paths()
            first_call_time = time.time() - start_time
            
            # Second call should be faster (cached) and not call get_finders again
            start_time = time.time()
            paths2 = importer._get_include_paths()
            second_call_time = time.time() - start_time
            
            self.assertEqual(paths1, paths2)
            # Second call should be faster due to caching
            self.assertLessEqual(second_call_time, first_call_time)
            # get_finders should only be called once due to caching
            self.assertEqual(mock_finders.call_count, 1)
    
    def test_large_scss_compilation(self):
        """Test compilation of large SCSS files."""
        # Generate large SCSS content
        large_scss = ""
        for i in range(1000):
            large_scss += f"""
            .class-{i} {{
                color: theme-color('primary');
                padding: {i}px;
            }}
            """
        
        start_time = time.time()
        result = compile_string(large_scss)
        compilation_time = time.time() - start_time
        
        # Should compile in reasonable time (less than 5 seconds)
        self.assertLess(compilation_time, 5.0)
        self.assertIn('.class-0', result['css'])
        self.assertIn('.class-999', result['css'])
    
    def test_concurrent_compilations(self):
        """Test thread safety of concurrent compilations."""
        results = {}
        errors = {}
        
        def compile_worker(worker_id):
            try:
                scss_code = f"""
                .worker-{worker_id} {{
                    color: theme-color('primary');
                    content: "worker-{worker_id}";
                }}
                """
                result = compile_string(scss_code)
                results[worker_id] = result['css']
            except Exception as e:
                errors[worker_id] = str(e)
        
        # Start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=compile_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        self.assertEqual(len(errors), 0, f"Compilation errors: {errors}")
        self.assertEqual(len(results), 10)
        
        for worker_id, css in results.items():
            self.assertIn(f'.worker-{worker_id}', css)
            self.assertIn(f'"worker-{worker_id}"', css)


class TestEdgeCases(TestCase):
    """Test edge cases and error conditions."""
    
    def test_empty_scss_compilation(self):
        """Test compilation of empty SCSS."""
        result = compile_string("")
        self.assertEqual(result['css'].strip(), "")
    
    def test_whitespace_only_scss(self):
        """Test compilation of whitespace-only SCSS."""
        result = compile_string("   \n\n   \t   ")
        self.assertEqual(result['css'].strip(), "")
    
    def test_comments_only_scss(self):
        """Test compilation of comments-only SCSS."""
        scss_code = """
        /* This is a CSS comment */
        // This is a Sass comment
        /* Multi-line
           comment */
        """
        result = compile_string(scss_code)
        # Should only contain CSS comments, not Sass comments
        self.assertIn("/* This is a CSS comment */", result['css'])
        self.assertNotIn("// This is a Sass comment", result['css'])
    
    def test_unicode_content(self):
        """Test compilation with Unicode content."""
        scss_code = """
        .unicode-test {
            content: "Hello 世界 🌍";
            font-family: "Noto Sans CJK";
        }
        """
        result = compile_string(scss_code)
        self.assertIn("Hello 世界 🌍", result['css'])
        self.assertIn("Noto Sans CJK", result['css'])
    
    def test_very_long_selectors(self):
        """Test compilation with very long selectors."""
        long_selector = ".very-long-selector-name-that-goes-on-and-on-and-on" * 10
        scss_code = f"""
        {long_selector} {{
            color: red;
        }}
        """
        result = compile_string(scss_code)
        self.assertIn("color: red", result['css'])
    
    def test_deeply_nested_rules(self):
        """Test compilation with deeply nested rules."""
        scss_code = """
        .level1 {
            .level2 {
                .level3 {
                    .level4 {
                        .level5 {
                            color: theme-color('primary');
                        }
                    }
                }
            }
        }
        """
        result = compile_string(scss_code)
        self.assertIn(".level1 .level2 .level3 .level4 .level5", result['css'])
        self.assertIn("#007bff", result['css'])
    
    def test_function_with_no_arguments(self):
        """Test Sass function that takes no arguments."""
        @sass_function("no-args()")
        def no_args_func(args):
            self.assertEqual(len(args), 0)
            return SassString("no-args-result")
        
        scss_code = """
        .test {
            content: no-args();
        }
        """
        result = compile_string(scss_code)
        self.assertIn('content: "no-args-result"', result['css'])
    
    def test_function_with_many_arguments(self):
        """Test Sass function with many arguments."""
        @sass_function("many-args($a, $b, $c, $d, $e)")
        def many_args_func(args):
            self.assertEqual(len(args), 5)
            values = [arg.assert_string().text for arg in args]
            return SassString("-".join(values))
        
        scss_code = """
        .test {
            content: many-args("a", "b", "c", "d", "e");
        }
        """
        result = compile_string(scss_code)
        self.assertIn('content: "a-b-c-d-e"', result['css'])
    
    def test_circular_import_prevention(self):
        """Test that circular imports are handled gracefully."""
        # This is more of a structural test
        try:
            from django_dart_sass import static
            from django_dart_sass.decorators import sass_function
            from django_dart_sass.importers import DjangoImporter
            from django_dart_sass.registry import compile_string
        except ImportError as e:
            self.fail(f"Circular import detected: {e}")
    
    def test_invalid_function_signature(self):
        """Test behavior with invalid function signatures."""
        
        # Test 1: Invalid signature with decorator should raise error and not add to registry
        with self.assertRaises(ValueError) as cm:
            @sass_function("invalid-signature-no-parens")
            def invalid_func(args):
                return SassString("should-not-be-called")
        
        self.assertIn('missing "("', str(cm.exception))
        
        # Verify it was NOT added to the global registry
        from django_dart_sass.decorators import _global_functions
        self.assertNotIn("invalid-signature-no-parens", _global_functions)
        
        # Test 2: Invalid signature passed to compile should also raise error
        def another_invalid_func(args):
            return SassString("should-not-be-called")
        
        with self.assertRaises(ValueError) as cm:
            compile_string('.test { color: red; }', {
                'functions': {
                    'another-invalid-signature-no-parens': another_invalid_func
                }
            })
        
        self.assertIn('missing "("', str(cm.exception))
    
    def test_function_exception_handling(self):
        """Test that exceptions in Sass functions are handled properly."""
        @sass_function("error-func($arg)")
        def error_func(args):
            raise ValueError("Function error")
        
        scss_code = """
        .test {
            content: error-func("test");
        }
        """
        
        # Should raise an exception during compilation
        with self.assertRaises(Exception):
            compile_string(scss_code)
    
    @override_settings(SASS_THEME_COLORS=None)
    def test_missing_theme_colors_setting(self):
        """Test behavior when SASS_THEME_COLORS setting is missing."""
        # Test the function directly with None setting
        from django_dart_sass.functions import theme_color
        from dart_sass.value import SassArgumentList, SassString
        
        args = SassArgumentList([SassString('primary')])
        result = theme_color(args)
        
        # Should return default primary color even when setting is None
        self.assertEqual(result.text, '#007bff')
        self.assertFalse(result.has_quotes)  # Colors should be unquoted
    
    def test_malformed_static_paths(self):
        """Test static() function with malformed paths."""
        from dart_sass.value import SassArgumentList, SassString
        from django_dart_sass.functions import static
        
        # Test with empty string
        args = SassArgumentList([SassString("")])
        result = static(args)
        self.assertIsInstance(result, SassString)
        
        # Test with path containing special characters
        args = SassArgumentList([SassString("path with spaces/file.css")])
        result = static(args)
        # URLs should be properly encoded
        self.assertIn("path%20with%20spaces/file.css", result.text)
    
    def test_memory_usage_with_many_functions(self):
        """Test memory usage doesn't grow excessively with many functions."""
        import gc
        
        # Get initial function count
        from django_dart_sass.decorators import _global_functions
        initial_count = len(_global_functions)
        
        # Register many functions
        for i in range(1000):
            @sass_function(f"memory-test-{i}($arg)")
            def memory_test_func(args):
                return SassString(f"result-{i}")
        
        # Force garbage collection
        gc.collect()
        
        # Check that functions are still accessible
        expected_count = initial_count + 1000
        self.assertEqual(len(_global_functions), expected_count)
        
        # Clear functions to free memory
        clear_all()
        self.assertEqual(len(_global_functions), 0)
