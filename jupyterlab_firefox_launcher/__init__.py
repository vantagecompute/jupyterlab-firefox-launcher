
"""
JupyterLab Firefox Launcher Extension

A minimal Firefox launcher for JupyterLab that uses jupyter-server-proxy
for process management. This extension is designed to work seamlessly
with SlurmSpawner environments.
"""

import os
from importlib.metadata import version

# Ensure we have the correct version of jupyter-server-proxy
__version__ = version("jupyterlab-firefox-launcher")


HERE = os.path.dirname(os.path.abspath(__file__))


def _jupyter_server_extension_points():
    """
    Minimal entry points - jupyter-server-proxy handles everything
    """
    return []


# For backward compatibility - but we don't actually load anything
def load_jupyter_server_extension(server_app):
    """
    Minimal server extension loader - jupyter-server-proxy handles everything
    """
    server_app.log.info("Firefox Desktop extension (minimal) - using jupyter-server-proxy")


_load_jupyter_server_extension = load_jupyter_server_extension
_jupyter_server_extension_paths = _jupyter_server_extension_points
