# JupyterLab Firefox Launcher with jupyter-server-proxy

This extension provides Firefox browser access within JupyterLab using `jupyter-server-proxy` and Xpra.

## Prerequisites

1. **Xpra**: Required for browser remoting
   ```bash
   # Ubuntu/Debian
   sudo apt-get install xpra firefox
   
   # CentOS/RHEL
   sudo yum install xpra firefox
   ```

2. **jupyter-server-proxy**: Will be installed automatically as a dependency

## Installation

1. Install the extension:
   ```bash
   pip install -e .
   ```

2. Enable the extensions:
   ```bash
   jupyter server extension enable jupyterlab_firefox_launcher
   jupyter serverextension enable jupyter_server_proxy
   ```

3. Start JupyterLab:
   ```bash
   jupyter lab
   ```

## Usage

1. After starting JupyterLab, you should see a "Firefox Browser" option in the launcher
2. Click on it to start Firefox in a new tab
3. The extension will automatically:
   - Allocate a random port (15000-16000)
   - Start Xpra with Firefox
   - Proxy the connection through JupyterLab

## How it works

- Uses `jupyter-server-proxy` to manage the Firefox service
- Xpra provides HTML5 browser remoting 
- Dynamic port allocation prevents conflicts
- The launch script (`launch-firefox-xpra.sh`) handles the Xpra startup
- No VNC required - Xpra provides direct HTML5 access

## Configuration

The configuration is defined in:
- `jupyterlab_firefox_launcher/__init__.py` - Entry point for jupyter-server-proxy
- `launch-firefox-xpra.sh` - Xpra startup script
- `pyproject.toml` - Package dependencies and entry points

## Debugging

Check if services are running:
```bash
# Check if Xpra is running
ps aux | grep xpra

# Check the allocated port
cat /tmp/xpra-port

# Test direct access
curl http://localhost:$(cat /tmp/xpra-port)
```
