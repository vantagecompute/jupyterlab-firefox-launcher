<a href="https://www.vantagecompute.ai/">
  <img src="https://vantage-compute-public-assets.s3.us-east-1.amazonaws.com/branding/vantage-logo-text-black-horz.png" alt="Vantage Compute Logo" width="100" style="margin-bottom: 0.5em;"/>
</a>

<div align="center">

# JupyterLab Firefox Launcher

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![JupyterLab](https://img.shields.io/badge/jupyterlab-4.0+-orange.svg)](https://jupyterlab.readthedocs.io)

![Build Status](https://img.shields.io/github/actions/workflow/status/vantagecompute/jupyterlab-firefox-launcher/test.yaml?branch=main&label=build&logo=github&style=plastic)
![GitHub Issues](https://img.shields.io/github/issues/vantagecompute/jupyterlab-firefox-launcher?label=issues&logo=github&style=plastic)
![Pull Requests](https://img.shields.io/github/issues-pr/vantagecompute/jupyterlab-firefox-launcher?label=pull-requests&logo=github&style=plastic)
![GitHub Contributors](https://img.shields.io/github/contributors/vantagecompute/jupyterlab-firefox-launcher?logo=github&style=plastic)

</div>

A JupyterLab extension that enables running Firefox browser sessions directly within JupyterLab tabs using Xpra remote display technology.

## 🚀 Quick Start

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt update && sudo apt install -y xvfb dbus-x11 xpra firefox

# Install the extension
pip install jupyterlab-firefox-launcher

# Start JupyterLab
jupyter lab
```

Click the Firefox icon in the JupyterLab launcher to start browsing!

## ✨ Key Features

- **On-Demand Firefox Sessions**: Launch multiple independent Firefox instances
- **Session Isolation**: Each session runs in its own isolated environment  
- **Multi-Session Support**: Run multiple concurrent Firefox sessions
- **Automatic Cleanup**: Proper session management and resource cleanup
- **High Performance**: Optimized remote display using Xpra technology

## � Documentation

Visit our comprehensive documentation site: **[vantagecompute.github.io/jupyterlab-firefox-launcher](https://vantagecompute.github.io/jupyterlab-firefox-launcher)**

- **[Installation Guide](https://vantagecompute.github.io/jupyterlab-firefox-launcher/installation/)**: Detailed setup instructions
- **[Architecture Overview](https://vantagecompute.github.io/jupyterlab-firefox-launcher/architecture/)**: How the extension works
- **[Development Guide](https://vantagecompute.github.io/jupyterlab-firefox-launcher/development/)**: Contributing and development setup
- **[API Reference](https://vantagecompute.github.io/jupyterlab-firefox-launcher/api-reference/)**: Complete API documentation
- **[Troubleshooting](https://vantagecompute.github.io/jupyterlab-firefox-launcher/troubleshooting/)**: Common issues and solutions

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](https://vantagecompute.github.io/jupyterlab-firefox-launcher/contributing/) for details on:

- Setting up development environment
- Code style guidelines  
- Submitting pull requests
- Reporting issues

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/vantagecompute/jupyterlab-firefox-launcher/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vantagecompute/jupyterlab-firefox-launcher/discussions)
- **Email**: [james@vantagecompute.ai](mailto:james@vantagecompute.ai)

---

**Made with ❤️ by [Vantage Compute](https://vantagecompute.ai)**
