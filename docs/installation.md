---
# Copyright (c) 2025 Vantage Compute Corporation.
layout: page
title: Installation Guide
permalink: /installation/
---

# Installation Guide

This guide provides step-by-step instructions for installing the JupyterLab Firefox Launcher extension on Linux systems. This extension **only supports Linux** (Ubuntu, CentOS, RHEL, Fedora, and compatible distributions).

## Quick Install

The quickest way to get started:

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt update && sudo apt install -y xvfb dbus-x11 xpra firefox

# Install the extension
pip install jupyterlab-firefox-launcher

# Start JupyterLab
jupyter lab
```

Click the Firefox icon in the JupyterLab launcher to start browsing!

## Detailed Installation

### Prerequisites

Before installing the extension, ensure your system meets the requirements:

- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+, or equivalent)
- **Python**: 3.10 or higher
- **JupyterLab**: 4.0 or higher
- **Node.js**: 16+ (for development only)
- **xpra**: +5.x
- **xfvb**: --
- **Firefox**: --


## System Dependencies

The extension requires several system packages to function properly. Install these first before installing the Python package.

> **⚠️ Important Note for Ubuntu Users**: By default, `apt install firefox` installs the snap-based version of Firefox on Ubuntu. **If you're using SlurmSpawner deployments with cgroups process management, snap-based Firefox will not work** due to sandboxing restrictions. In such environments, you must install Firefox from Mozilla's official repository (shown below) or compile from source.

### Install Firefox, Xpra, dbus-x11, xvfb (Ubuntu Noble)
```bash
# Add Mozilla repository
sudo install -d -m 0755 /etc/apt/keyrings
wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | \
  sudo tee /etc/apt/keyrings/packages.mozilla.org.asc > /dev/null

echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | \
  sudo tee -a /etc/apt/sources.list.d/mozilla.list > /dev/null

echo 'Package: *
Pin: origin packages.mozilla.org
Pin-Priority: 1000' | \
  sudo tee /etc/apt/preferences.d/mozilla


# Add Xpra Key and Repo
sudo wget -O "/usr/share/keyrings/xpra.asc" https://xpra.org/xpra.asc

echo 'Types: deb
URIs: https://xpra.org/lts
Suites: noble
Components: main
Signed-By: /usr/share/keyrings/xpra.asc
Architectures: amd64 arm64' | sudo tee /etc/apt/sources.list.d/xpra.source


# Update and install
sudo apt update
sudo apt install -y xvfb dbus-x11 xpra firefox
```

### CentOS/RHEL/Fedora Systems

```bash
# Enable EPEL repository (required for Xpra)
sudo dnf install -y epel-release

# Install dependencies
sudo dnf install -y xorg-x11-server-Xvfb dbus-x11 xpra firefox

# Alternative for older systems using yum
# sudo yum install -y epel-release
# sudo yum install -y xorg-x11-server-Xvfb dbus-x11 xpra firefox
```

### Conda/Mamba Installation

If you prefer using conda/mamba for system dependencies:

```bash
# Create conda environment (optional)
conda create -n firefox-launcher python=3.11
conda activate firefox-launcher

# Install system dependencies
conda install -c conda-forge xpra firefox

# Note: You may still need to install Xvfb through system package manager
sudo apt install -y xvfb dbus-x11  # Ubuntu/Debian
sudo dnf install -y xorg-x11-server-Xvfb dbus-x11  # CentOS/RHEL/Fedora
```

## Python Installation

### pip 

Install the extension using pip:

```bash
# Install from PyPI
pip install jupyterlab-firefox-launcher

# Or install with development dependencies
pip install "jupyterlab-firefox-launcher[dev]"
```

### uv

If you have `uv` installed:

```bash
# Install the extension
uv pip install jupyterlab-firefox-launcher

# Or install in a virtual environment
uv venv
source .venv/bin/activate
uv pip install jupyterlab-firefox-launcher
```

### Method 3: Development Installation

For development or the latest features:

```bash
# Clone the repository
git clone https://github.com/vantagecompute/jupyterlab-firefox-launcher.git
cd jupyterlab-firefox-launcher

# Or using uv
uv pip install -e .
```

## Verification

After installation, verify that everything is working correctly:

### 1. Check System Dependencies

```bash
# Verify Xvfb is installed
which Xvfb
# Should output: /usr/bin/Xvfb

# Verify Xpra is installed
xpra --version
# Should output version information

# Verify Firefox is installed
firefox --version
# Should output Firefox version
```

### 2. Check Python Installation

```bash
# Check if extension is installed
uv pip list | grep jupyterlab-firefox-launcher
# Should show the installed version

# Check JupyterLab extensions
uv run jupyter labextension list
# Should include jupyterlab-firefox-launcher
```

### 3. Test the Extension

```bash
# Start JupyterLab
uv run jupyter lab

# Look for Firefox icon in the launcher
# Click it to test functionality
```

## Configuration

### Environment Variables

You can customize the extension behavior using environment variables:

```bash
# Firefox quality (1-100, default: 100)
export FIREFOX_LAUNCHER_QUALITY=80

# Compression method (default: none)
export FIREFOX_LAUNCHER_COMPRESS=lz4

# DPI setting (default: 96)
export FIREFOX_LAUNCHER_DPI=120

# Debug mode
export FIREFOX_LAUNCHER_DEBUG=1

# Development override for firefox-xstartup script
export DEV_FIREFOX_LAUNCHER_PATH=/path/to/custom/script
```

### JupyterLab Configuration

Add configuration to your JupyterLab settings:

```json
{
  "jupyterlab-firefox-launcher": {
    "default_quality": 100,
    "default_dpi": 96,
    "auto_cleanup": true,
    "session_timeout": 3600
  }
}
```

## Docker Installation

For containerized environments:

### Dockerfile Example

```dockerfile
FROM jupyter/base-notebook:latest

# Switch to root to install system dependencies
USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    xvfb \
    dbus-x11 \
    xpra \
    firefox \
    && rm -rf /var/lib/apt/lists/*

# Switch back to notebook user
USER ${NB_UID}

# Install the extension
RUN pip install jupyterlab-firefox-launcher

# Start JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
```

### Docker Compose Example

```yaml
version: '3.8'
services:
  jupyter:
    build: .
    ports:
      - "8888:8888"
    volumes:
      - ./work:/home/jovyan/work
    environment:
      - FIREFOX_LAUNCHER_QUALITY=80
      - FIREFOX_LAUNCHER_DEBUG=1
    command: |
      jupyter lab --ip=0.0.0.0 --port=8888 --no-browser 
      --allow-root --NotebookApp.token='' --NotebookApp.password=''
```

## Troubleshooting Installation

### Common Issues

#### 1. Missing System Dependencies

**Error**: `xpra executable not found`

**Solution**:
```bash
# Ubuntu/Debian
sudo apt install -y xpra

# CentOS/RHEL/Fedora
sudo dnf install -y xpra
```

#### 2. Firefox Not Found

**Error**: `firefox executable not found`

**Solution**:
```bash
# Install Firefox
sudo apt install -y firefox  # Ubuntu/Debian
sudo dnf install -y firefox  # CentOS/RHEL/Fedora
```

#### 3. Permission Issues

**Error**: `Permission denied` when running Xvfb

**Solution**:
```bash
# Add user to necessary groups
sudo usermod -a -G audio,video $USER

# Logout and login again, or run:
newgrp audio
newgrp video
```

#### 4. Extension Not Visible

**Error**: Firefox launcher not appearing in JupyterLab

**Solution**:
```bash
# Rebuild JupyterLab
jupyter lab build

# Clear browser cache
# Restart JupyterLab
jupyter lab --port=8889  # Use different port to force refresh
```

#### 5. Snap Firefox Issues on SlurmSpawner/cgroups

**Error**: Firefox fails to start in SlurmSpawner environments with cgroups

**Problem**: Ubuntu's default `apt install firefox` installs the snap version, which conflicts with cgroups process management used by SlurmSpawner.

**Solution**: Install Firefox from Mozilla's official repository:
```bash
# Remove snap Firefox if already installed
sudo snap remove firefox

# Add Mozilla repository (as shown in installation section above)
sudo install -d -m 0755 /etc/apt/keyrings
wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | \
  sudo tee /etc/apt/keyrings/packages.mozilla.org.asc > /dev/null

echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | \
  sudo tee -a /etc/apt/sources.list.d/mozilla.list > /dev/null

echo 'Package: *
Pin: origin packages.mozilla.org
Pin-Priority: 1000' | \
  sudo tee /etc/apt/preferences.d/mozilla

# Update and install non-snap Firefox
sudo apt update
sudo apt install -y firefox
```

**Alternative**: Download and install Firefox manually:
```bash
# Download Firefox directly from Mozilla
wget -O firefox.tar.bz2 "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US"
tar -xjf firefox.tar.bz2
sudo mv firefox /opt/
sudo ln -sf /opt/firefox/firefox /usr/local/bin/firefox
```

### Diagnostic Commands

Use these commands to diagnose installation issues:

```bash
# Check system dependencies
echo "Checking system dependencies..."
which xvfb && echo "✓ Xvfb found" || echo "✗ Xvfb missing"
which xpra && echo "✓ Xpra found" || echo "✗ Xpra missing"  
which firefox && echo "✓ Firefox found" || echo "✗ Firefox missing"

# Check Python installation
echo "Checking Python installation..."
python -c "import jupyterlab_firefox_launcher; print('✓ Extension imported successfully')" 2>/dev/null || echo "✗ Extension import failed"

# Check JupyterLab integration
echo "Checking JupyterLab integration..."
jupyter labextension list | grep firefox-launcher && echo "✓ Extension enabled" || echo "✗ Extension not found"

# Test Xpra functionality
echo "Testing Xpra..."
xpra start --bind-tcp=localhost:9999 --html=on --daemon=no --start-child=echo "test" --exit-with-children=yes
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Look for error messages in JupyterLab console
2. **Enable debug mode**: Set `FIREFOX_LAUNCHER_DEBUG=1`
3. **Check system resources**: Ensure sufficient memory and disk space
4. **Review dependencies**: Verify all system dependencies are properly installed
5. **Consult documentation**: Check [troubleshooting guide]({{ site.baseurl }}/troubleshooting)
6. **Report issues**: Create an issue on [GitHub](https://github.com/vantagecompute/jupyterlab-firefox-launcher/issues)

## Next Steps

After successful installation:

- **[Overview]({{ site.baseurl }}/overview)**: Learn about the extension's capabilities
- **[Architecture]({{ site.baseurl }}/architecture)**: Understand how it works
- **[Development]({{ site.baseurl }}/development)**: Set up development environment
- **[Troubleshooting]({{ site.baseurl }}/troubleshooting)**: Solve common issues
