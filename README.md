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

- Python 3.8+
- Node.js
- Yarn

### Setup

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install -e .
   ```
3. Install and build the frontend:
   ```bash
   yarn install
   yarn build
   ```

### Building

To build the extension:

```bash
yarn build
python -m build
```

TODO
* Get firefox advanced launcher working
* Remove additional icon in notebooks section

## License

BSD-3-Clause License
