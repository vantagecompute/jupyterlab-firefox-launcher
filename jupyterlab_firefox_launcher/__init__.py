
import os
import sys
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("jupyterlab-firefox-launcher")
except PackageNotFoundError:
    __version__ = "unknown"


def firefox():
    """Entry point for jupyter-server-proxy"""
    # Use the installed script from bin directory
    script_name = "launch-firefox-xpra"
    if sys.platform == "win32":
        script_name += ".exe"
    
    # Find the script in the virtual environment bin directory
    script_path = None
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're in a virtual environment
        bin_dir = os.path.join(sys.prefix, 'bin')
        if sys.platform == "win32":
            bin_dir = os.path.join(sys.prefix, 'Scripts')
        script_path = os.path.join(bin_dir, script_name)
    else:
        # System installation, look in PATH
        import shutil
        script_path = shutil.which(script_name)
    
    if not script_path or not os.path.exists(script_path):
        # Fallback to python -m execution
        script_path = [sys.executable, "-m", "jupyterlab_firefox_launcher.scripts"]
    else:
        script_path = [script_path]
    
    def get_port():
        try:
            with open('/tmp/xpra-port', 'r') as f:
                return int(f.read().strip())
        except:
            return 15000  # Default fallback port
    
    return {
        "command": script_path,
        "timeout": 90,  # Increased timeout to 90 seconds
        "port": get_port(),
        "mappath": {"/": "/"},
        "launcher_entry": {
            "enabled": False  # Disable default launcher entry
        }
    }


def _jupyter_server_extension_points():
    return [{
        "module": "jupyterlab_firefox_launcher"
    }]


def _load_jupyter_server_extension(server_app):
    """Called when the extension is loaded"""
    server_app.log.info("Loaded jupyterlab_firefox_launcher extension")
