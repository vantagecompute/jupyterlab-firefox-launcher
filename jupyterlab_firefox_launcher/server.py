import os


def get_firefox_config():
    """Get configuration for Firefox server proxy"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, '..', 'launch-firefox-xpra.sh')
    script_path = os.path.abspath(script_path)
    
    def get_port():
        try:
            with open('/tmp/xpra-port', 'r') as f:
                return int(f.read().strip())
        except:
            return 15000  # Default fallback port
    
    return {
        "command": [script_path],
        "timeout": 30,
        "port": get_port,
        "mappath": {"/": "/"},
        "launcher_entry": {
            "title": "Firefox Browser",
            "icon_path": "/usr/share/icons/hicolor/48x48/apps/firefox.png",
        },
    }


def load_jupyter_server_extension(app):
    """Called when the extension is loaded."""
    # Register with jupyter-server-proxy if available
    try:
        from jupyter_server_proxy import get_server_info
        # This will be handled by the config
        pass
    except ImportError:
        app.log.warning("jupyter-server-proxy not available")


def _jupyter_server_extension_paths():
    return [{
        "module": "jupyterlab_firefox_launcher"
    }]

