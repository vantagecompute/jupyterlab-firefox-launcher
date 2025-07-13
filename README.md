# JupyterLab Firefox Launcher

[![PyPI version](https://img.shields.io/pypi/v/jupyterlab-firefox-launcher.svg)](https://pypi.org/project/jupyterlab-firefox-launcher/)
[![License](https://img.shields.io/pypi/l/jupyterlab-firefox-launcher.svg)](https://github.com/vantagecompute/jupyterlab-firefox-launcher/blob/main/LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/jupyterlab-firefox-launcher.svg)](https://pypi.org/project/jupyterlab-firefox-launcher/)
[![JupyterLab Version](https://img.shields.io/badge/JupyterLab-4.0%2B-orange.svg)](https://jupyterlab.readthedocs.io/)

A powerful JupyterLab extension that seamlessly integrates Firefox browser functionality directly into your JupyterLab workspace, enabling web browsing, debugging, and development workflow enhancement without leaving your coding environment.

## ✨ Features

- **🚀 One-Click Firefox Launch**: Launch Firefox directly from the JupyterLab launcher with a single click
- **🔧 Integrated Workflow**: Browse documentation, test web applications, and debug without context switching
- **⚡ Modern Architecture**: Built with JupyterLab 4+ using modern TypeScript and Python backend
- **🎯 Seamless Integration**: Appears natively in JupyterLab's launcher interface alongside notebooks and terminals
- **🔒 Secure**: Server-side controlled browser launching with proper security considerations
- **🌐 Development-Friendly**: Perfect for web development, data visualization, and research workflows

## 🛠️ Architecture

This extension consists of two main components:

### Frontend Extension (TypeScript)
- Modern ES2018+ TypeScript implementation
- Webpack module federation for optimal loading
- Integrated with JupyterLab's launcher system
- Responsive UI components using Lumino widgets

### Server Extension (Python)
- Tornado-based web handlers for browser control
- Secure server-side process management
- RESTful API for frontend communication
- Cross-platform Firefox detection and launching

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install jupyterlab-firefox-launcher
```

### From Source

```bash
git clone https://github.com/vantagecompute/jupyterlab-firefox-launcher.git
cd jupyterlab-firefox-launcher
pip install -e .
```

## 🚀 Usage

1. **Install the extension** using pip as shown above
2. **Restart JupyterLab** to load the new extension
3. **Open JupyterLab** in your browser
4. **Look for the Firefox icon** in the JupyterLab launcher
5. **Click the Firefox launcher** to open Firefox in a new window/tab

### Verification

To verify the extension is properly installed:

```bash
# Check server extension
jupyter server extension list

# Check frontend extension  
jupyter labextension list
```

You should see `jupyterlab_firefox_launcher` listed as enabled in both outputs.

## 🔧 Development

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm/yarn
- **JupyterLab 4.0+**
- **Firefox browser** installed on your system

### Development Setup

1. **Clone and navigate to the repository:**
   ```bash
   git clone https://github.com/vantagecompute/jupyterlab-firefox-launcher.git
   cd jupyterlab-firefox-launcher
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install JavaScript dependencies:**
   ```bash
   jlpm install
   ```

5. **Build the extension:**
   ```bash
   jlpm build
   ```

6. **Enable the extension for development:**
   ```bash
   jupyter server extension enable jupyterlab_firefox_launcher
   ```

### Development Workflow

#### Frontend Development
```bash
# Watch mode for frontend changes
jlpm watch

# In another terminal, start JupyterLab
jupyter lab --watch
```

#### Building for Distribution
```bash
# Clean previous builds
jlpm clean

# Build production version
jlpm build:prod

# Build Python wheel
python -m build
```

#### Running Tests
```bash
# Python tests
pytest

# JavaScript tests (if available)
jlpm test
```

### Project Structure

```
jupyterlab-firefox-launcher/
├── README.md                          # This file
├── LICENSE                           # BSD-3-Clause license
├── pyproject.toml                    # Python project configuration
├── tsconfig.json                     # TypeScript configuration
├── package.json                      # Node.js package configuration
├── webpack.config.js                 # Webpack build configuration
├── install.json                      # JupyterLab extension metadata
├── src/                             # TypeScript source code
│   ├── index.ts                     # Main extension entry point
│   └── handler.ts                   # Frontend request handlers
├── jupyterlab_firefox_launcher/     # Python package
│   ├── __init__.py                  # Package initialization
│   ├── server.py                    # Tornado server extension
│   └── labextension/               # Built frontend assets
└── dist/                           # Distribution packages
```

## 🔧 Technical Details

### Build System
- **Python**: Hatchling with hatch-jupyter-builder integration
- **Frontend**: Webpack 5 with module federation
- **TypeScript**: ES2018 target with modern module resolution
- **Package Management**: pip for Python, jlpm (yarn) for JavaScript

### Dependencies
- **Python**: jupyter-server ≥2.0.1, jupyterlab ≥4.0.0, tornado ≥6.1.0
- **JavaScript**: @jupyterlab/application, @jupyterlab/launcher, @lumino/widgets

### Browser Support
- **Firefox**: All modern versions
- **Platform**: Cross-platform (Windows, macOS, Linux)
- **Security**: Server-controlled launching for enhanced security

## 🤝 Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for details.

### Development Guidelines
1. **Fork the repository** and create a feature branch
2. **Follow code style** conventions (Black for Python, Prettier for TypeScript)
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Submit a pull request** with a clear description

### Reporting Issues
- Use the [GitHub issue tracker](https://github.com/vantagecompute/jupyterlab-firefox-launcher/issues)
- Include JupyterLab version, Python version, and browser details
- Provide steps to reproduce the issue

## 📄 License

This project is licensed under the [BSD-3-Clause License](LICENSE).

```
Copyright (c) 2025, Vantage Compute
All rights reserved.
```

## 🙏 Acknowledgments

- **JupyterLab Team** for the excellent extension framework
- **Project Jupyter** for the amazing ecosystem
- **Contributors** who help improve this extension

## 📚 Related Resources

- [JupyterLab Documentation](https://jupyterlab.readthedocs.io/)
- [JupyterLab Extension Developer Guide](https://jupyterlab.readthedocs.io/en/stable/extension/extension_dev.html)
- [Project Jupyter](https://jupyter.org/)

---

**Made with ❤️ for the Jupyter community**
