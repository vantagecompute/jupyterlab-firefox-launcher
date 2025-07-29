# Changelog

All notable changes to the JupyterLab Firefox Launcher project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete README overhaul with comprehensive documentation
- Architecture diagrams and component descriptions
- Detailed dependency documentation
- Contributing guidelines and development workflow
- Professional contact and support information

### Changed
- SESSION_DIR-based path building instead of individual path variables
- Improved session isolation and directory structure
- Enhanced firefox-xstartup script with better path management
- Streamlined environment variable passing to Firefox

### Fixed
- Session killer bug where new sessions would terminate existing ones
- Removed global signal handlers that caused cross-session interference
- Improved session cleanup and resource management
- Fixed premature cleanup calls from frontend widget lifecycle

### Security
- Enhanced session isolation with dedicated directory structures
- Improved process cleanup to prevent resource leaks
- Better handling of orphaned processes

## [0.1.0] - 2025-01-XX

### Added
- Initial release of JupyterLab Firefox Launcher
- Core functionality for launching Firefox in JupyterLab tabs
- Xpra-based remote display integration
- Multi-session support with session isolation
- Custom launcher button in JupyterLab interface
- Session management and cleanup handlers
- Firefox startup script with optimized preferences
- Jupyter server extension integration
- TypeScript-based frontend widget
- Python-based backend handlers

### Features
- On-demand Firefox session launching
- Session-specific profile and cache directories
- Automatic cleanup on widget disposal
- Support for multiple concurrent sessions
- Responsive Firefox integration within JupyterLab tabs
- Configurable Firefox preferences and display settings

### Dependencies
- JupyterLab 4.0+ support
- Python 3.10+ compatibility
- Xpra remote display server
- Mozilla Firefox browser
- System dependencies: xvfb, dbus-x11

### Build System
- UV-based Python package management
- Hatch build backend integration
- TypeScript compilation and webpack bundling
- Streamlined development workflow
- Automated extension building
