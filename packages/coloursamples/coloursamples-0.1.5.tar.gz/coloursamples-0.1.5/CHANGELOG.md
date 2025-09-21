# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Build system modernization**: Updated Makefile to use `uv run python` for consistency with modern Python project management
- **Default output directory**: Changed from `output_files` to current directory (`.`) for simpler usage
- **Test suite updates**: Updated all tests to reflect new default output directory behavior

### Fixed
- **Build consistency**: Ensured all build commands use the same Python execution method

## [0.1.4] - 2025-09-14

### Added
- **Custom exception system**: Clean error handling without tracebacks
  - `ColourSamplesError`: Base exception class for all application errors
  - `InvalidDimensionsError`: For width/height validation issues
  - `InvalidColourCodeError`: For colour code format validation
  - `FileSystemError`: For directory/file operation failures
  - `ImageCreationError`: For PIL image creation failures
- **Enhanced CLI error display**: User-friendly error messages with helpful examples
- **Improved input validation**: Better error messages with specific guidance
- **Keyboard interrupt handling**: Graceful handling of Ctrl+C during operations

### Changed
- **Error handling architecture**: Migrated from generic exceptions to custom exception hierarchy
- **CLI error display**: Replaced tracebacks with clean, actionable error messages
- **Test suite updates**: Updated all tests to work with new custom exceptions (44 tests, 86% coverage)
- **Code quality improvements**: Fixed linting issues and improved code formatting

### Fixed
- **Argument validation bug**: Fixed issue where `0` values were incorrectly treated as missing arguments
- **Error message consistency**: Standardized error messages across CLI and core modules
- **Exception handling**: Proper exception chaining with `from None` to suppress tracebacks

## [0.1.3] - 2025-09-14

### Added
- **Comprehensive test suite**: 44 tests achieving 98% code coverage
- **Parameterized testing**: Multiple input combinations tested systematically
- **Edge case coverage**: Large dimensions, case handling, JPEG compression tolerance
- **Full CLI testing**: Complete command-line interface testing using `typer.testing.CliRunner`
- **Coverage configuration**: 80% minimum requirement with detailed reporting
- **Google docstring validation**: Enhanced ruff pydocstyle rules with Google convention

### Changed
- **Test organization**: Extracted test data into well-organized module constants
- **Standards compliance**: Removed all inline comments, added missing type hints
- **Enhanced error handling**: Comprehensive validation and error message testing
- **Version bump**: Updated to 0.1.3

### Fixed
- **Code quality**: All coding standards violations resolved
- **Test reliability**: JPEG compression-aware color validation
- **Type annotations**: Added missing type hints throughout test suite

### Technical
- Added pytest-cov integration with automatic coverage reporting
- Configured coverage to fail builds below 80% threshold
- Enhanced test isolation with proper filesystem management
- Comprehensive CLI interactive mode and option validation

## [0.1.2] - 2025-09-14 [SKIPPED - Not Published to PyPI]

### Note
This version was tagged in git but never built or published to PyPI. All changes were included in v0.1.3.

### Added
- Google-style docstring enforcement with ruff pydocstyle rules
- Missing module docstring in test file for full compliance
- Enhanced docstring validation configuration

### Changed
- Updated pydocstyle configuration to use Google convention
- Version bump to 0.1.2 in package metadata

## [0.1.1] - 2025-09-14

### Added
- GitHub repository URL to project metadata
- Comprehensive project URLs (Homepage, Repository, Bug Tracker)
- Enhanced project metadata for better package distribution

### Changed
- **British spelling standardization**: Changed all instances of "color" to "colour" throughout codebase
- **Enhanced error logging**: Added proper exception logging with `logger.exception()` in CLI error handling
- Updated project description to use British spelling
- Version bump to 0.1.1

### Fixed
- Consistent British spelling across code, documentation, tests, and configuration
- Proper exception logging in CLI error handlers
- Project metadata improvements for Python packaging standards

### Technical
- Maintained compatibility with external libraries requiring American spelling (Pillow API)
- All tests passing with enhanced spelling consistency
- Code quality improvements with proper logging practices

## [0.1.0] - 2025-09-14

### Added
- **Initial release**: Python utility for generating JPEG images with specified dimensions and colours
- **Modern CLI interface**: Built with typer and rich for enhanced user experience
- **Core functionality**:
  - `create_image()` function for programmatic use
  - Command-line interface with `coloursamples create` command
  - Interactive mode with rich prompts and validation
- **Input validation**: Comprehensive validation for dimensions and colour codes
- **Flexible output**: Support for custom output directories and string/Path inputs
- **Error handling**: Clear error messages and proper exception handling
- **Modern Python packaging**: Using src-layout structure with hatchling build backend
- **Code quality tools**: Configured ruff for linting and formatting, pytest for testing
- **Dependencies**: Pillow for image creation, typer for CLI, rich for UI formatting

### Technical Details
- **Package structure**: Modern src-layout with `src/coloursamples/`
- **CLI features**: Help command, info command, verbose logging, interactive prompts
- **Image format**: JPEG output with HTML hex colour code support (#RRGGBB format)
- **Python support**: Compatible with Python 3.8+
- **Build system**: Hatchling with proper wheel and source distribution support

---

## Version Policy

- **Major versions** (x.0.0): Breaking changes to public API
- **Minor versions** (0.x.0): New features, enhancements, backwards compatible
- **Patch versions** (0.0.x): Bug fixes, documentation updates, minor improvements

## Release Process

1. Update version via git tag (using semantic versioning)
2. Update this CHANGELOG.md with release notes
3. Create GitHub release with tag
4. Build packages: `uv run hatch build`
5. Publish to PyPI: `uv run twine upload dist/*`
6. Update documentation as needed