# Django Dart Sass

Django integration for Python Dart Sass with django-compressor support and powerful Django-specific Sass functions.

## Features

- 🚀 **Fast Sass compilation** using the Dart Sass compiler
- 🔧 **Django integration** with `static()`, `url-for()`, and `theme-color()` functions
- 📦 **django-compressor support** for seamless asset pipeline integration
- 🎯 **Two-tier function system** - global decorators + contextual functions
- 📁 **App-specific imports** with `@import 'app:myapp/styles'` syntax
- ⚡ **Production ready** with comprehensive error handling and caching
- 🧪 **100% test coverage** with 77 passing tests

## Installation

```bash
pip install django-dart-sass
```

For django-compressor integration:
```bash
pip install django-dart-sass[compressor]
```

## Quick Start

### 1. Add to Django Settings

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'django_dart_sass',
]

# Optional: Configure theme colors
SASS_THEME_COLORS = {
    'primary': '#007bff',
    'secondary': '#6c757d',
    'success': '#28a745',
    'danger': '#dc3545',
    'warning': '#ffc107',
    'info': '#17a2b8',
}

# Optional: Additional Sass load paths
SASS_LOAD_PATHS = [
    BASE_DIR / 'assets' / 'sass',
    BASE_DIR / 'components',
]

# Optional: Sass compilation options
SASS_DART_OPTIONS = {
    'style': 'compressed',
    'source_map': True,
}
```

### 2. Use Django Functions in Sass

```scss
// styles.scss
.header {
    background-image: url(static('images/header-bg.jpg'));
    color: theme-color('primary');
}

.api-link::after {
    content: url-for('api:users');
}
```

### 3. Compile Sass

```python
# In your views or management commands
from django_dart_sass import compile_string, compile_file

# Compile from string
result = compile_string("""
.test {
    color: theme-color('primary');
    background: url(static('images/bg.jpg'));
}
""")
print(result['css'])

# Compile from file
result = compile_file('path/to/styles.scss')
print(result['css'])
```

## Django-Compressor Integration

### Setup

```python
# settings.py
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_dart_sass.compressor.DartSassCompressor'),
)

COMPRESS_ENABLED = True
```

### Template Usage

```html
<!-- template.html -->
{% load compress %}

{% compress css %}
<link rel="stylesheet" type="text/x-scss" href="{% static 'styles/main.scss' %}" />
<style type="text/x-scss">
.dynamic-style {
    color: theme-color('primary');
    background: url(static('images/pattern.png'));
}
</style>
{% endcompress %}
```

## Built-in Django Functions

### `static($path)` - Static File URLs

Generate Django static file URLs:

```scss
// Input
.logo {
    background-image: url(static('images/logo.png'));
}

// Output
.logo {
    background-image: url('/static/images/logo.png');
}
```

### `url-for($name, ...)` - URL Reversing

Reverse Django URLs with optional arguments:

```scss
// Input
.api-endpoint::after {
    content: url-for('api:users');
}

.user-profile::after {
    content: url-for('user:profile', 123);
}

// Output
.api-endpoint::after {
    content: '/api/users/';
}

.user-profile::after {
    content: '/users/123/';
}
```

### `theme-color($name)` - Theme Colors

Access theme colors from Django settings:

```scss
// Input
.btn-primary {
    background-color: theme-color('primary');
    border-color: theme-color('primary');
}

// Output (with SASS_THEME_COLORS = {'primary': '#007bff'})
.btn-primary {
    background-color: #007bff;
    border-color: #007bff;
}
```

## App-Specific Imports

Import Sass files from specific Django apps:

```scss
// Import from myapp/static/myapp/sass/variables.scss
@import 'app:myapp/variables';

// Import from myapp/static/myapp/components.scss  
@import 'app:myapp/components';

// Standard imports still work
@import 'bootstrap/variables';
```

### App Structure

```
myapp/
├── static/
│   └── myapp/
│       ├── sass/
│       │   ├── variables.scss
│       │   └── mixins.scss
│       └── components.scss
└── ...
```

## Custom Functions

### Global Functions (Decorator)

Register functions globally across all compilations:

```python
# myapp/sass_functions.py
from django_dart_sass import sass_function
from dart_sass.value import SassString, SassNumber

@sass_function("asset-url($path)")
def asset_url(args):
    """Generate asset URLs with cache busting."""
    path = args[0].assert_string().text
    # Your custom logic here
    versioned_path = f"{path}?v={get_asset_version(path)}"
    return SassString(f'url("{versioned_path}")', quoted=False)

@sass_function("rem($pixels)")
def pixels_to_rem(args):
    """Convert pixels to rem units."""
    pixels = args[0].assert_number().value
    rem_value = pixels / 16  # Assuming 16px base
    return SassNumber(rem_value, unit='rem')
```

### Contextual Functions (Per-Compilation)

Override or add functions for specific compilations:

```python
from django_dart_sass import compile_string

def custom_function(args):
    return SassString("custom-value")

result = compile_string(scss_code, {
    'functions': {
        'custom($arg)': custom_function,
        # This overrides any global function with same signature
    }
})
```

## Custom Importers

### Global Importers (Decorator)

```python
# myapp/sass_importers.py
from django_dart_sass import sass_importer
from dart_sass.importer import ImportResult

@sass_importer
def theme_importer(url, from_import):
    """Import theme files from a themes directory."""
    if url.startswith('theme:'):
        theme_name = url[6:]  # Remove 'theme:' prefix
        theme_path = f'themes/{theme_name}.scss'
        
        try:
            with open(theme_path, 'r') as f:
                contents = f.read()
            return ImportResult(contents=contents, syntax='scss')
        except FileNotFoundError:
            return None
    
    return None  # Let other importers handle this URL
```

Usage in Sass:
```scss
@import 'theme:dark';
@import 'theme:light';
```

### Contextual Importers (Per-Compilation)

```python
from django_dart_sass import compile_string
from django_dart_sass.importers import DjangoImporter

# Create custom importer for this compilation
custom_importer = DjangoImporter()

result = compile_string(scss_code, {
    'importers': [custom_importer],  # Higher priority than global importers
})
```

## Advanced Configuration

### Load Paths

Configure where Sass looks for imported files:

```python
# settings.py

# Method 1: Django settings
SASS_LOAD_PATHS = [
    BASE_DIR / 'assets' / 'sass',
    BASE_DIR / 'node_modules',
    '/usr/local/share/sass',
]

# Method 2: STATICFILES_DIRS (automatically included)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'assets',
]

# Method 3: Additional include paths
SASS_ADDITIONAL_INCLUDE_PATHS = [
    '/custom/sass/path',
]

# Method 4: Embedded-specific paths
SASS_DART_INCLUDE_PATHS = [
    '/embedded/sass/path',
]
```

### Compilation Options

```python
# settings.py
SASS_DART_OPTIONS = {
    # Output style: 'expanded', 'compressed'
    'style': 'compressed',
    
    # Generate source maps
    'source_map': True,
    
    # Charset handling
    'charset': True,
    
    # Import paths (alternative to SASS_LOAD_PATHS)
    'load_paths': ['/additional/path'],
    
    # Quiet dependency warnings
    'quiet_deps': True,
    
    # Verbose output
    'verbose': False,
}
```

## Error Handling

The package provides comprehensive error handling:

```python
from django_dart_sass import compile_string
from dart_sass.exception import CompileException

try:
    result = compile_string("""
    .invalid {
        color: $undefined-variable;
    }
    """)
except CompileException as e:
    print(f"Sass compilation error: {e}")
    # Error includes line numbers and context
```

## Performance Tips

1. **Use Global Functions**: Register frequently-used functions globally with decorators
2. **Cache Compilation Results**: The package handles internal caching, but consider Django's cache framework for compiled CSS
3. **Minimize Load Paths**: Too many load paths can slow down import resolution
4. **Use Compressed Style**: Set `'style': 'compressed'` in production

## Testing

The package includes comprehensive tests. Run them with:

```bash
# Install dev dependencies
pip install django-dart-sass[dev]

# Run tests
python -m pytest

# Run with coverage
python -m pytest --cov=django_dart_sass
```

## Troubleshooting

### Common Issues

**ImportError: No module named 'compressor'**
```bash
# Install django-compressor
pip install django-compressor
# Or install with compressor support
pip install django-dart-sass[compressor]
```

**Sass compilation fails with "Can't find stylesheet to import"**
- Check your `SASS_LOAD_PATHS` settings
- Verify file paths and extensions (.scss vs .sass)
- Use app-specific imports: `@import 'app:myapp/file'`

**Functions not available in Sass**
- Ensure `django_dart_sass` is in `INSTALLED_APPS`
- Check that function modules are imported (functions are registered on import)
- Verify function signatures match exactly

### Debug Mode

Enable verbose logging:

```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django_dart_sass': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Acknowledgments

This Django integration was developed by Harvey McQueen with assistance from Amazon Q Command-line. It builds upon:

- [python-dart-sass](https://github.com/hmcqueen/python-dart-sass) - The core Python Dart Sass implementation
- [Embedded Sass Protocol](https://github.com/sass/sass/blob/main/spec/embedded-protocol.md) - The communication protocol
- [Dart Sass](https://sass-lang.com/dart-sass) - The Sass compilation engine

This is an independent Django integration and is not affiliated with or endorsed by the official Sass team or Django Software Foundation.

## License

MIT License - see LICENSE file for details.

## Related Projects

- [django-compressor](https://github.com/django-compressor/django-compressor) - Django asset compression framework
- [django-sass-processor](https://github.com/jrief/django-sass-processor) - Alternative Django Sass integration
- [Dart Sass](https://sass-lang.com/dart-sass) - The official Sass implementation

## Changelog

### 0.1.0
- Initial release
- Two-tier function and importer system
- Django-compressor integration
- App-specific imports
- Built-in Django functions (static, url-for, theme-color)
- Comprehensive test suite
