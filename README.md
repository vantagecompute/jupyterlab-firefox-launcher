# JupyterLab Firefox Launcher

A JupyterLab extension to launch Firefox in a tab.

## Description

This extension adds a Firefox launcher to JupyterLab, allowing you to open Firefox directly within the JupyterLab interface.

## Installation


### System Deps
```bash
sudo install -d -m 0755 /etc/apt/keyrings

wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | sudo tee /etc/apt/keyrings/packages.mozilla.org.asc > /dev/null

echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | sudo tee -a /etc/apt/sources.list.d/mozilla.list > /dev/null

echo '
Package: *
Pin: origin packages.mozilla.org
Pin-Priority: 1000
' | sudo tee /etc/apt/preferences.d/mozilla

sudo apt update && sudo apt install xvfb dbus-x11 xpra firefox -y
```

```bash
pip install python-uinput jupyterlab-firefox-launcher
```

## Development

### Prerequisites

- Python 3.10+
- Node.js
- uv (Python package manager)

### Build Process Flow

The extension uses a streamlined build chain with **uv** as the main driver:

1. **`uv build`** (main driver - Python packaging)
2. → calls **hatch** (build backend from pyproject.toml)  
3. → calls **jlpm build:prod** (via hatch-jupyter-builder)
4. → calls **jupyter labextension build** (simplified package.json scripts)
5. → handles TypeScript compilation and webpack bundling internally

This eliminates duplicate TypeScript compilation steps and ensures consistent builds.

### Setup

1. Clone the repository
2. Install with uv:
   ```bash
   uv pip install -e .
   ```

### Building

To build the extension:

```bash
./build.sh
# OR manually:
uv build
```

### Installing for Development

```bash
uv pip install ./dist/jupyterlab_firefox_launcher-*.whl --force-reinstall
```

### Key Features

- **On-Demand xpra Launching**: Firefox only starts when the user clicks the launcher icon
- **No Automatic Startup**: Server-proxy is configured with `enabled: False` 
- **Custom API Endpoint**: `/firefox-launcher/launch` provides on-demand proxy URL
- **JupyterLab Integration**: Custom launcher icon in the "Other" section

TODO
* Get firefox advanced launcher working
* Remove additional icon in notebooks section

## License

BSD-3-Clause License
