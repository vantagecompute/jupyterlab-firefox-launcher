
"""
JupyterLab Firefox Launcher Extension

A minimal Firefox launcher for JupyterLab that uses jupyter-server-proxy
for process management. This extension is designed to work seamlessly
with SlurmSpawner environments.
"""

import os
from importlib.metadata import version

# Import server extension functionality
from .server_extension import load_jupyter_server_extension

# Ensure we have the correct version of jupyter-server-proxy
__version__ = version("jupyterlab-firefox-launcher")


HERE = os.path.dirname(os.path.abspath(__file__))


def _jupyter_server_extension_points():
    """
    Entry points for server extensions - following jupyter-remote-desktop-proxy pattern
    """
    return [{"module": "jupyterlab_firefox_launcher"}]


def load_jupyter_server_extension(server_app):
    """
    Main entry point for the server extension.
    Delegates to the actual implementation in server_extension module.
    """
    from .server_extension import load_jupyter_server_extension as _load_ext
    return _load_ext(server_app)


# For backward compatibility
_load_jupyter_server_extension = load_jupyter_server_extension
_jupyter_server_extension_paths = _jupyter_server_extension_points
