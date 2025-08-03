---
# Copyright (c) 2025 Vantage Compute Corporation.
layout: page
title: Dependencies
permalink: /dependencies/
---

# Dependencies

This page provides a comprehensive overview of all dependencies required by the JupyterLab Firefox Launcher extension, including system packages, Python libraries, and frontend dependencies.

## System Dependencies

The extension requires several system packages to function properly. These must be installed before the Python package.

### Core Requirements

#### Display and X11 Components
- **xvfb**: Virtual framebuffer X server for headless display
- **xpra**: Remote display server with HTML5 client support
- **dbus-x11**: D-Bus X11 integration for session management

#### Browser
- **firefox**: Mozilla Firefox browser (latest stable version recommended)

#### Optional but Recommended
- **xauth**: X11 authorization utilities for secure X forwarding
- **xfonts-base**: Basic X11 fonts for proper text rendering
- **ca-certificates**: SSL/TLS certificates for secure web browsing

### Installation by Platform

#### Ubuntu/Debian (apt)
```bash
# Core dependencies
sudo apt update
sudo apt install -y xvfb xpra dbus-x11 firefox

# Optional but recommended
sudo apt install -y xauth xfonts-base ca-certificates

# For development
sudo apt install -y build-essential python3-dev
```

#### CentOS/RHEL/Fedora (dnf/yum)
```bash
# Enable EPEL repository (required for Xpra)
sudo dnf install -y epel-release

# Core dependencies
sudo dnf install -y xorg-x11-server-Xvfb xpra dbus-x11 firefox

# Optional but recommended  
sudo dnf install -y xorg-x11-xauth xorg-x11-fonts-base ca-certificates

# For older systems using yum
# sudo yum install -y epel-release
# sudo yum install -y xorg-x11-server-Xvfb xpra dbus-x11 firefox
```

#### Conda/Mamba
```bash
# Install available packages through conda
conda install -c conda-forge xpra firefox

# Note: Some packages may need system installation
sudo apt install -y xvfb dbus-x11  # Ubuntu/Debian
sudo dnf install -y xorg-x11-server-Xvfb dbus-x11  # CentOS/RHEL/Fedora
```

### Version Requirements

| Package | Minimum Version | Recommended Version | Notes |
|---------|----------------|-------------------|--------|
| **xvfb** | 1.20+ | Latest | Virtual X server |
| **xpra** | 4.0+ | 5.0+ | HTML5 support required |
| **firefox** | 90+ | Latest ESR | Modern web standards |
| **dbus-x11** | 1.12+ | Latest | Session management |

## Python Dependencies

### Runtime Dependencies

#### Core Jupyter Components
```python
# JupyterLab platform and extensions
jupyterlab >= 4.4.5              # JupyterLab platform
jupyter-server >= 2.0.1, < 3     # Jupyter server backend  
tornado >= 6.1.0                 # Async web framework

# Process and system monitoring
psutil                           # Process management and monitoring

# Proxy integration
jupyter-server-proxy >= 3.0.0    # Enhanced proxy support

# HTTP and WebSocket communication
aiohttp >= 3.12.14               # Async HTTP client/server
websockets >= 15.0.1             # WebSocket implementation
requests >= 2.32.4               # HTTP library

# System integration
python-uinput >= 1.0.1           # Input device simulation
```

### Development Dependencies

#### Build Tools
```python
# Package building and management
hatchling >= 1.5.0               # Modern build backend
hatch-jupyter-builder >= 0.8.3   # JupyterLab build integration
build                            # PEP 517 build tool
wheel                            # Wheel package format

# Jupyter packaging
jupyter-packaging >= 0.12, < 1   # Jupyter-specific packaging tools
```

#### Testing Framework
```python
# Core testing
pytest >= 6.0.0                  # Testing framework
pytest-asyncio                   # Async testing support
pytest-cov                       # Coverage reporting
pytest-jupyter[server] >= 0.4    # Jupyter server testing

# Test utilities
coverage                         # Code coverage analysis
```

#### Code Quality Tools
```python
# Formatting and linting
black                            # Code formatting
isort                            # Import sorting
mypy                             # Static type checking
flake8                           # Linting

# Documentation
sphinx                           # Documentation generation
sphinx-rtd-theme                 # ReadTheDocs theme
```

### Installation Commands

#### Standard Installation
```bash
# Install runtime dependencies
pip install jupyterlab-firefox-launcher
```

#### Development Installation
```bash
# Install with all development dependencies
pip install "jupyterlab-firefox-launcher[dev]"

# Or install from source
git clone https://github.com/vantagecompute/jupyterlab-firefox-launcher.git
cd jupyterlab-firefox-launcher
pip install -e ".[dev]"
```

#### Using uv (Fast Package Manager)
```bash
# Standard installation
uv pip install jupyterlab-firefox-launcher

# Development installation
uv pip install -e ".[dev]"
```

## Frontend Dependencies

### Core Dependencies

#### JupyterLab Platform
```json
{
  "@jupyterlab/application": "^4.0.0",    // Main JupyterLab application
  "@jupyterlab/launcher": "^4.0.0",       // Launcher integration
  "@jupyterlab/services": "^7.0.0",       // Jupyter services API
  "@lumino/widgets": "^2.0.0"             // Widget framework
}
```

#### TypeScript and Build Tools
```json
{
  "typescript": "~5.0.0",                 // TypeScript compiler
  "webpack": "^5.0.0",                    // Module bundler
  "css-loader": "^6.0.0",                // CSS processing
  "style-loader": "^3.0.0",              // Style injection
  "source-map-loader": "^4.0.0"          // Source map support
}
```

### Development Dependencies

#### Build and Development Tools
```json
{
  "@types/node": "^18.0.0",               // Node.js type definitions
  "rimraf": "^4.0.0",                     // Cross-platform rm -rf
  "npm-run-all": "^4.1.5",               // Run multiple npm commands
  "eslint": "^8.0.0",                     // JavaScript/TypeScript linting
  "prettier": "^2.0.0"                    // Code formatting
}
```

#### JupyterLab Development
```json
{
  "@jupyterlab/builder": "^4.0.0",        // JupyterLab build tools
  "@jupyterlab/testutils": "^4.0.0",      // Testing utilities
  "jest": "^29.0.0",                      // Testing framework
  "@types/jest": "^29.0.0"                // Jest type definitions
}
```

### Node.js Requirements

| Tool | Minimum Version | Recommended Version | Purpose |
|------|----------------|-------------------|---------|
| **Node.js** | 16.0+ | 18.0+ | JavaScript runtime |
| **npm** | 8.0+ | 9.0+ | Package manager |
| **jlpm** | Latest | Latest | JupyterLab package manager |

## Dependency Management

### Python Environment

#### Using pip
```bash
# Create virtual environment
python -m venv firefox-launcher-env
source firefox-launcher-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Using conda
```bash
# Create conda environment
conda create -n firefox-launcher python=3.11
conda activate firefox-launcher

# Install dependencies
conda install --file conda-requirements.txt
pip install -r pip-requirements.txt  # For packages not in conda
```

#### Using uv
```bash
# Create virtual environment with uv
uv venv firefox-launcher-env
source firefox-launcher-env/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### Node.js Environment

#### Using npm
```bash
# Install dependencies
npm install

# Install development dependencies
npm install --include=dev
```

#### Using yarn
```bash
# Install dependencies
yarn install

# Install development dependencies
yarn install --dev
```

#### Using JupyterLab's jlpm
```bash
# Install dependencies (recommended for JupyterLab extensions)
jlpm install
```

## Dependency Verification

### System Dependencies Check
```bash
#!/bin/bash
echo "Checking system dependencies..."

# Check for required binaries
command -v xvfb >/dev/null 2>&1 && echo "✓ Xvfb found" || echo "✗ Xvfb missing"
command -v xpra >/dev/null 2>&1 && echo "✓ Xpra found" || echo "✗ Xpra missing" 
command -v firefox >/dev/null 2>&1 && echo "✓ Firefox found" || echo "✗ Firefox missing"
command -v dbus-launch >/dev/null 2>&1 && echo "✓ D-Bus found" || echo "✗ D-Bus missing"

# Check versions
echo "Checking versions..."
xpra --version 2>/dev/null | head -n1 || echo "Could not get Xpra version"
firefox --version 2>/dev/null || echo "Could not get Firefox version"
```

### Python Dependencies Check
```python
#!/usr/bin/env python3
"""Check Python dependencies for JupyterLab Firefox Launcher."""

import sys
import importlib
import pkg_resources

required_packages = [
    'jupyterlab>=4.0.0',
    'jupyter_server>=2.0.0', 
    'tornado>=6.0.0',
    'psutil>=5.8.0'
]

optional_packages = [
    'jupyter_server_proxy>=3.0.0',
    'python_uinput>=1.0.1'
]

def check_package(package_spec):
    """Check if a package meets version requirements."""
    try:
        pkg_resources.require(package_spec)
        return True, "✓"
    except pkg_resources.DistributionNotFound:
        return False, "✗ Not installed"
    except pkg_resources.VersionConflict as e:
        return False, f"✗ Version conflict: {e}"

print("Checking Python dependencies...")
print("=" * 50)

all_good = True

print("Required packages:")
for package in required_packages:
    success, message = check_package(package)
    print(f"  {message} {package}")
    if not success:
        all_good = False

print("\nOptional packages:")
for package in optional_packages:
    success, message = check_package(package)
    print(f"  {message} {package}")

print("\nPython version:")
print(f"  ✓ Python {sys.version}")

if all_good:
    print("\n✓ All required dependencies satisfied!")
else:
    print("\n✗ Some required dependencies are missing or incompatible.")
    sys.exit(1)
```

### Frontend Dependencies Check
```bash
#!/bin/bash
echo "Checking frontend dependencies..."

# Check Node.js and npm
node --version >/dev/null 2>&1 && echo "✓ Node.js: $(node --version)" || echo "✗ Node.js missing"
npm --version >/dev/null 2>&1 && echo "✓ npm: $(npm --version)" || echo "✗ npm missing"

# Check if dependencies are installed
if [ -d "node_modules" ]; then
    echo "✓ node_modules directory exists"
    
    # Check key dependencies
    if [ -d "node_modules/@jupyterlab" ]; then
        echo "✓ JupyterLab packages installed"
    else
        echo "✗ JupyterLab packages missing"
    fi
else
    echo "✗ node_modules directory missing - run 'npm install'"
fi

# Check TypeScript
npx tsc --version >/dev/null 2>&1 && echo "✓ TypeScript: $(npx tsc --version)" || echo "✗ TypeScript missing"
```

## Troubleshooting Dependencies

### Common Issues

#### 1. Xpra Version Too Old
**Problem**: Xpra version doesn't support HTML5 client
**Solution**: 
```bash
# Ubuntu/Debian - add Xpra repository for latest version
wget -O - https://xpra.org/gpg.asc | sudo apt-key add -
echo "deb https://xpra.org/ jammy main" | sudo tee /etc/apt/sources.list.d/xpra.list
sudo apt update && sudo apt install xpra
```

#### 2. Firefox Permission Issues
**Problem**: Firefox fails to start due to permissions
**Solution**:
```bash
# Add user to necessary groups
sudo usermod -a -G audio,video $USER
# Logout and login, or run: newgrp audio && newgrp video
```

#### 3. Python Version Conflicts
**Problem**: Incompatible Python versions
**Solution**:
```bash
# Use specific Python version
python3.11 -m pip install jupyterlab-firefox-launcher

# Or create environment with specific version
conda create -n firefox-launcher python=3.11
```

#### 4. Node.js/npm Issues
**Problem**: Node.js version too old or npm conflicts
**Solution**:
```bash
# Update Node.js using nvm
nvm install 18
nvm use 18

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

- **[Installation Guide]({{ site.baseurl }}/installation)**: Complete installation instructions
- **[Architecture]({{ site.baseurl }}/architecture)**: Understand system architecture
- **[Development]({{ site.baseurl }}/development)**: Set up development environment
- **[Troubleshooting]({{ site.baseurl }}/troubleshooting)**: Solve common issues
