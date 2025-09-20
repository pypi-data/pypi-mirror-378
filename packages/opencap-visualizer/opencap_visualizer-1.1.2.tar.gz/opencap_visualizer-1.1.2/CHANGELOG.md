# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.2] - 2024-09-19

### ✨ Added
- **Version Flag**: Added `--version` flag to CLI for easy version checking
  - Standard CLI behavior: `opencap-visualizer --version`
  - Shows program name and version number

## [1.1.1] - 2024-09-19

### 🐛 Fixed
- **Loop Count Bug**: Fixed critical issue where requested loop count was ignored
  - Previously: Requesting 5 loops would only record ~2-3 loops
  - Now: Requesting 5 loops correctly records exactly 5 loops
  - Root cause: Session.vue loop counting logic had off-by-one error
  - Solution: Added automatic compensation in CLI/API layer
- **Video Recording Format**: Enhanced format detection and conversion
  - Better handling of MP4 vs WebM output based on file extension
  - Improved ffmpeg fallback logic for format conversion
  - More robust error handling for unsupported formats
- **Minimum Duration Logic**: Improved automatic loop adjustment for short animations
  - Short animations (<3 seconds) automatically get more loops for usable videos
  - Clear logging when automatic adjustments are made
  - Respects user intent while ensuring video quality

### ✨ Added
- **Version Flag**: Added `--version` flag to CLI for easy version checking
  - Standard CLI behavior: `opencap-visualizer --version`
  - Shows program name and version number

### 🔧 Enhanced
- **Debug Logging**: Added comprehensive logging for troubleshooting
  - Browser console integration for better debugging
  - Clear messages about format choices and loop adjustments
  - Verbose mode shows all recording parameters
- **Error Messages**: More informative error messages and warnings
- **Documentation**: Updated API documentation with loop behavior notes

## [1.1.0] - 2024-07-30

### 🚨 BREAKING CHANGES
- **Package renamed**: `opencap-visualizer-cli` → `opencap-visualizer`
  - Command-line interface remains the same: `opencap-visualizer` and `opencap-viz`
  - Python imports now use: `import opencap_visualizer`

### ✨ Added
- **Python API**: Full programmatic access to video generation functionality
  - `OpenCapVisualizer` class for object-oriented usage  
  - `create_video()` and `create_video_async()` convenience functions
  - Async and sync support for different use cases
  - Comprehensive type hints and documentation
- **Enhanced CLI**: Improved command-line interface
  - Better error messages and progress indicators
  - Verbose mode for debugging and development
  - More robust file handling and validation
- **Format Support**: Extended file format compatibility
  - JSON files (pre-processed motion data)
  - .osim + .mot pairs (OpenSim models with motion)
  - Better error handling for invalid formats

### 🔧 Improved
- **Performance**: Optimized video generation pipeline
- **Reliability**: Enhanced error handling and recovery
- **Documentation**: Comprehensive README and API documentation
- **Testing**: Added automated testing infrastructure

### 🏗️ Infrastructure
- **Build System**: Updated packaging and distribution
- **CI/CD**: Automated testing and deployment
- **Dependencies**: Updated to latest stable versions

## [1.0.0] - 2024-07-15

### ✨ Initial Release
- Command-line tool for generating videos from biomechanics data
- Support for JSON and OpenSim file formats
- Configurable camera angles and visualization options
- Web-based visualization engine
- Cross-platform compatibility (Windows, macOS, Linux)
