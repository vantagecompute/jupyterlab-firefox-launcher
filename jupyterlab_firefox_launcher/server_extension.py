"""
Server extension for JupyterLab Firefox Launcher

This module provides the server-side extension integration,
following the pattern established by jupyter-remote-desktop-proxy.
The actual Firefox launching is handled by jupyter-server-proxy.
"""

import os
import logging
from pathlib import Path

HERE = Path(__file__).parent

# Logger for the extension
logger = logging.getLogger(__name__)


def load_jupyter_server_extension(server_app):
    """
    Called when the server extension is loaded.
    
    This follows the pattern from jupyter-remote-desktop-proxy but is minimal
    since the actual Firefox proxy functionality is handled by jupyter-server-proxy
    through the entry point configuration.
    """
    logger.info("JupyterLab Firefox Launcher server extension loaded")
    logger.info("Firefox desktop functionality provided via jupyter-server-proxy")
    
    # Log the configuration for debugging
    logger.debug(f"Extension path: {HERE}")
    
    # The actual Firefox proxy is automatically registered via the entry point:
    # jupyter_serverproxy_servers.firefox-desktop
    
    server_app.log.info("JupyterLab Firefox Launcher: Ready to launch Firefox in Xpra HTML5 mode")


# Required function for backward compatibility
def _jupyter_server_extension_points():
    """
    Return the list of server extension entry points.
    """
    return [{"module": "jupyterlab_firefox_launcher.server_extension"}]
