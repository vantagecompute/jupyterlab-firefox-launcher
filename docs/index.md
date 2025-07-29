---
# Copyright (c) 2025 Vantage Compute Corporation.
layout: home
title: Home
permalink: /
---

<div style="display: flex; justify-content: center; align-items: center; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap;">
  <img src="https://img.shields.io/badge/license-Apache--2.0-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/jupyterlab-4.0+-orange.svg" alt="JupyterLab">
</div>
<div style="display: flex; justify-content: center; align-items: center; gap: 0.5rem; margin-bottom: 2rem; flex-wrap: wrap;">
  <img src="https://img.shields.io/github/contributors/vantagecompute/jupyterlab-firefox-launcher?logo=github&style=plastic" alt="Github Contributors">
  <img src="https://img.shields.io/github/issues-pr/vantagecompute/jupyterlab-firefox-launcher?label=pull-requests&logo=github&style=plastic" alt="Github Pull Requests">
  <img src="https://img.shields.io/github/issues/vantagecompute/jupyterlab-firefox-launcher?label=issues&logo=github&style=plastic" alt="Github Issues">
</div>

<div class="hero-section">
  <div style="display: flex; justify-content: center; align-items: center; gap: 4rem; margin-bottom: 2rem; flex-wrap: wrap;">
    <div style="display: flex; flex-direction: column; align-items: center; transform: scale(1.1);">
      <div style="background: #FFFFFF; padding: 20px; border-radius: 16px; box-shadow: 0 8px 25px rgba(107, 70, 193, 0.3); margin-bottom: 1rem; border: 2px solid #E5E7EB;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/7/76/Mozilla_Firefox_logo_2013.svg" alt="Firefox" style="width: 60px; height: 60px;">
      </div>
      <span style="font-size: 1rem; color: #6B7280; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Firefox</span>
    </div>
    <div style="display: flex; align-items: center; justify-content: center;">
      <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #6B46C1, #9333EA); border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(107, 70, 193, 0.3);">
        <span style="color: white; font-size: 2rem; font-weight: 700; line-height: 1;">+</span>
      </div>
    </div>
    <div style="display: flex; flex-direction: column; align-items: center; transform: scale(1.1);">
      <div style="background: #FFFFFF; padding: 20px; border-radius: 16px; box-shadow: 0 8px 25px rgba(147, 51, 234, 0.3); margin-bottom: 1rem; border: 2px solid #E5E7EB;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/3/38/Jupyter_logo.svg" alt="Jupyter" style="width: 60px; height: 60px;">
      </div>
      <span style="font-size: 1rem; color: #6B7280; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Jupyter</span>
    </div>
  </div>
  <h2 style="margin: 0; color: #111827; font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem; background: linear-gradient(135deg, #6B46C1, #9333EA, #A855F7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">Jupyterlab Firefox Launcher Documentation</h2>
  <p style="margin: 0; color: #6B7280; font-size: 1.25rem; font-weight: 500; max-width: 600px; margin: 0 auto;">Created and maintained by Vantage Compute</p>
  <div style="margin-top: 2rem; display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
    <a href="#quick-start" style="background: linear-gradient(135deg, #6B46C1, #9333EA); color: white; padding: 1rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 1.1rem; box-shadow: 0 4px 15px rgba(107, 70, 193, 0.3); transition: all 0.2s ease; display: inline-block;">Get Started</a>
    <a href="https://github.com/vantagecompute/jupyterlab-firefox-launcher" style="background: white; color: #6B46C1; padding: 1rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 1.1rem; border: 2px solid #6B46C1; transition: all 0.2s ease; display: inline-block;">View on GitHub</a>
  </div>
</div>

The JupyterLab Firefox Launcher provides seamless integration of a full Firefox browser environment within your JupyterLab workspace. This extension is designed for data scientists, researchers, and developers who need web browsing capabilities from where the notebook server runs.

## Quick Start {#quick-start}

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
