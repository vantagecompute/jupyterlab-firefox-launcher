---
# Copyright (c) 2025 Vantage Compute Corporation.
layout: home
title: Home
permalink: /
---

# JupyterLab Firefox Launcher

<div style="text-align: center; margin-bottom: 2rem;">
  <img src="https://vantage-compute-public-assets.s3.us-east-1.amazonaws.com/branding/vantage-logo-text-black-horz.png" alt="Vantage Compute" style="height: 60px; width: auto; margin-bottom: 1rem;">
</div>

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](https://github.com/vantagecompute/jupyterlab-firefox-launcher/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![JupyterLab](https://img.shields.io/badge/jupyterlab-4.0+-orange.svg)](https://jupyterlab.readthedocs.io)
[![GitHub Stars](https://img.shields.io/github/stars/vantagecompute/jupyterlab-firefox-launcher?style=social)](https://github.com/vantagecompute/jupyterlab-firefox-launcher)

<div class="hero-section" style="text-align: center; margin: 2rem 0; padding: 2rem; background: linear-gradient(135deg, #E8E3F3 0%, #F3F1F8 30%, #F8F9FA 70%, #FFFFFF 100%); border-radius: 12px;">
  <div class="hero-logos" style="display: flex; justify-content: center; align-items: center; gap: 3rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
    <div class="logo-container" style="display: flex; flex-direction: column; align-items: center;">
      <img src="https://upload.wikimedia.org/wikipedia/commons/7/76/Mozilla_Firefox_logo_2013.svg" alt="Firefox" style="width: 60px; height: 60px; margin-bottom: 0.5rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
      <span style="font-size: 0.9rem; color: #333; font-weight: 500;">Firefox</span>
    </div>
    <div style="font-size: 2rem; color: #666; margin: 0 1rem;">+</div>
    <div class="logo-container" style="display: flex; flex-direction: column; align-items: center;">
      <img src="https://upload.wikimedia.org/wikipedia/commons/3/38/Jupyter_logo.svg" alt="Jupyter" style="width: 60px; height: 60px; margin-bottom: 0.5rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); background: white; padding: 10px;">
      <span style="font-size: 0.9rem; color: #333; font-weight: 500;">Jupyter</span>
    </div>
  </div>
  <h2 style="margin: 0; color: #333; font-size: 1.5rem; font-weight: 600;">Seamless Firefox Integration for JupyterLab</h2>
  <p style="margin: 0.5rem 0 0 0; color: #555; font-size: 1.1rem;">Powered by Xpra + Jupyter Server Proxy</p>
</div>

The JupyterLab Firefox Launcher provides seamless integration of a full Firefox browser environment within your JupyterLab workspace. This extension is designed for data scientists, researchers, and developers who need web browsing capabilities from where the notebook server runs.

## Quick Start

Get up and running with JupyterLab Firefox Launcher in minutes:

### 1. Install System Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install xvfb dbus-x11 xpra firefox -y

# CentOS/RHEL/Fedora
sudo dnf install xorg-x11-server-Xvfb dbus-x11 xpra firefox
```

### 2. Install Extension
```bash
pip install jupyterlab-firefox-launcher
```

### 3. Launch JupyterLab
```bash
jupyter lab
```

### 4. Open Firefox
Click the Firefox icon in the JupyterLab launcher to start browsing!

## Key Features

<div class="feature-grid">
  <div class="feature-card">
    <h3>🚀 On-Demand Sessions</h3>
    <p>Launch multiple independent Firefox instances with isolated profiles and configurations.</p>
  </div>
  
  <div class="feature-card">
    <h3>🔒 Session Isolation</h3>
    <p>Each Firefox session runs in its own isolated environment with dedicated resources.</p>
  </div>
  
  <div class="feature-card">
    <h3>📱 Responsive Integration</h3>
    <p>Firefox runs natively within JupyterLab tabs with seamless user experience.</p>
  </div>
  
  <div class="feature-card">
    <h3>🎯 Multi-Session Support</h3>
    <p>Run multiple concurrent Firefox sessions without conflicts or interference.</p>
  </div>
  
  <div class="feature-card">
    <h3>🧹 Automatic Cleanup</h3>
    <p>Proper session management and resource cleanup when sessions end.</p>
  </div>
  
  <div class="feature-card">
    <h3>⚡ High Performance</h3>
    <p>Optimized for remote display using advanced Xpra technology.</p>
  </div>
</div>

## Use Cases

- **Web-based Research**: Access web resources directly within your computational environment
- **Data Visualization**: View interactive web-based charts and dashboards
- **API Testing**: Test web APIs and services from within JupyterLab
- **Documentation**: Access online documentation while coding
- **Remote Development**: Full browser access in remote JupyterLab deployments

## Documentation Structure

<div class="docs-nav">
  <div class="nav-section">
    <h3>Getting Started</h3>
    <ul>
      <li><a href="{{ site.baseurl }}/overview">Overview</a></li>
      <li><a href="{{ site.baseurl }}/installation">Installation Guide</a></li>
      <li><a href="{{ site.baseurl }}/dependencies">Dependencies</a></li>
    </ul>
  </div>
  
  <div class="nav-section">
    <h3>Technical Details</h3>
    <ul>
      <li><a href="{{ site.baseurl }}/architecture">Architecture</a></li>
      <li><a href="{{ site.baseurl }}/api-reference">API Reference</a></li>
      <li><a href="{{ site.baseurl }}/troubleshooting">Troubleshooting</a></li>
    </ul>
  </div>
  
  <div class="nav-section">
    <h3>Development</h3>
    <ul>
      <li><a href="{{ site.baseurl }}/development">Development Guide</a></li>
      <li><a href="{{ site.baseurl }}/contributing">Contributing</a></li>
      <li><a href="{{ site.baseurl }}/contact">Contact & Support</a></li>
    </ul>
  </div>
</div>

## Latest Updates

- **Multi-Session Support**: Run multiple Firefox instances simultaneously
- **Enhanced Security**: Improved session isolation and cleanup
- **Apache License**: Now available under Apache License 2.0
- **Performance Improvements**: Optimized for better remote display performance

---

**Built with ❤️ by [Vantage Compute](https://vantagecompute.ai)**

<style>
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.feature-card {
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  padding: 1.5rem;
  background: #f6f8fa;
}

.feature-card h3 {
  margin-top: 0;
  color: #0366d6;
}

.docs-nav {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.nav-section {
  background: #f6f8fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e1e4e8;
}

.nav-section h3 {
  margin-top: 0;
  color: #0366d6;
}

.nav-section ul {
  list-style: none;
  padding-left: 0;
}

.nav-section li {
  margin: 0.5rem 0;
}

.nav-section a {
  text-decoration: none;
  color: #586069;
  font-weight: 500;
}

.nav-section a:hover {
  color: #0366d6;
}
</style>
