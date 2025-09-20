# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-XX

### Added

#### Core Features
- **Two-tier function system**: Global functions via decorators + contextual functions via compile options
- **Two-tier importer system**: Global importers via decorators + contextual importers via compile options
- **Django-compressor integration**: Full support for django-compressor asset pipeline
- **App-specific imports**: Import Sass files from Django apps using `@import 'app:myapp/styles'` syntax

#### Built-in Django Functions
- **`static($path)`**: Generate Django static file URLs
- **`url-for($name, ...)`**: Reverse Django URLs with optional arguments  
- **`theme-color($name)`**: Access theme colors from Django settings

#### Django Integration
- **Automatic function registration**: Functions registered via decorators on app startup
- **Django settings integration**: Configure via `SASS_THEME_COLORS`, `SASS_LOAD_PATHS`, etc.
- **Static files integration**: Automatic inclusion of `STATICFILES_DIRS` in load paths
- **App discovery**: Automatic discovery of Sass files in Django app static directories

#### Advanced Features
- **Custom function decorators**: `@sass_function("name($args)")` for global function registration
- **Custom importer decorators**: `@sass_importer` and `@sass_file_importer` for global importer registration
- **Load path configuration**: Multiple methods for configuring Sass import paths
- **Comprehensive error handling**: Detailed error messages with line numbers and context
- **Performance optimizations**: Caching and efficient compilation pipeline

#### Testing & Quality
- **100% test coverage**: 77 passing tests covering all functionality
- **Integration tests**: End-to-end tests with real Sass compilation
- **Performance tests**: Benchmarks for function and importer systems
- **Django-compressor tests**: Full integration testing with django-compressor
- **Cross-platform support**: Tested on Linux, macOS, and Windows

### Technical Details

#### Architecture
- **Registry system**: Centralized management of functions and importers with proper priority handling
- **Decorator system**: Clean API for registering global functions and importers
- **Django importer**: Sophisticated importer supporting app-specific imports and Django static files
- **Compressor filter**: Full django-compressor integration with automatic global function/importer inclusion

#### Dependencies
- **Python**: 3.10+
- **Django**: 3.2+
- **python-dart-sass**: Latest Python Dart Sass implementation
- **django-compressor**: Optional dependency for asset pipeline integration

#### Configuration Options
- **`SASS_THEME_COLORS`**: Define theme colors accessible via `theme-color()` function
- **`SASS_LOAD_PATHS`**: Additional Sass import paths
- **`SASS_ADDITIONAL_INCLUDE_PATHS`**: Extra include paths for Sass imports
- **`SASS_DART_INCLUDE_PATHS`**: Embedded-specific include paths
- **`SASS_DART_OPTIONS`**: Sass compilation options (style, source maps, etc.)

### Breaking Changes
- None (initial release)

### Migration Guide
- None (initial release)

### Known Issues
- None

### Contributors
- Harvey McQueen - Initial implementation and architecture
- Harvey McQueen - Comprehensive test suite development
- Harvey McQueen - Documentation and examples
- Harvey McQueen - Django-compressor integration
- Harvey McQueen - Performance optimizations

---

## Release Notes Template

### [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Now removed features

### Fixed
- Bug fixes

### Security
- Vulnerability fixes
