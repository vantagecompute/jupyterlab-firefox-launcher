"""
Server extension for JupyterLab Firefox Launcher

This module provides the server-side extension integration with API endpoints
for on-demand Firefox launching via jupyter-server-proxy.
"""

import os
import json
import logging
from pathlib import Path
from tornado import web
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join

HERE = Path(__file__).parent

# Logger for the extension
logger = logging.getLogger(__name__)


class FirefoxLaunchHandler(APIHandler):
    """
    API handler for on-demand Firefox launching.
    """
    
    @web.authenticated
    def post(self):
        """
        Start Firefox via jupyter-server-proxy on demand.
        
        This endpoint returns the proxy URL where Firefox will be available.
        The actual Firefox/xpra startup is handled by jupyter-server-proxy 
        when the proxy URL is first accessed.
        """
        try:
            # Get base URL for constructing proxy path
            base_url = self.application.settings.get('base_url', '/')
            
            # The proxy endpoint is registered via entry point in pyproject.toml
            proxy_path = 'firefox-desktop'
            full_path = url_path_join(base_url, 'proxy', proxy_path)
            
            logger.info(f"Firefox launcher requested - proxy will be available at: {full_path}")
            
            # Return success with the proxy URL
            # jupyter-server-proxy will handle the actual startup when accessed
            self.finish(json.dumps({
                'status': 'success',
                'message': 'Firefox launcher ready - access proxy URL to start',
                'url': full_path,
                'proxy_path': proxy_path
            }))
            
        except Exception as e:
            logger.error(f"Failed to prepare Firefox launcher: {e}")
            self.set_status(500)
            self.finish(json.dumps({
                'status': 'error',
                'message': f'Failed to prepare Firefox launcher: {str(e)}'
            }))


def setup_handlers(web_app):
    """
    Set up the API handlers for the extension.
    """
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    
    # API endpoint for launching Firefox on demand
    launch_pattern = url_path_join(base_url, "firefox-launcher", "launch")
    handlers = [(launch_pattern, FirefoxLaunchHandler)]
    
    web_app.add_handlers(host_pattern, handlers)
    logger.info(f"Firefox launcher API handler registered at {launch_pattern}")


def load_jupyter_server_extension(server_app):
    """
    Called when the server extension is loaded.
    
    Sets up API endpoints for on-demand Firefox launching.
    """
    # Set up API handlers
    setup_handlers(server_app.web_app)
    
    logger.info("JupyterLab Firefox Launcher server extension loaded")
    logger.info("Firefox desktop functionality available via API")
    
    # Log the configuration for debugging
    logger.debug(f"Extension path: {HERE}")
    
    server_app.log.info("JupyterLab Firefox Launcher: Ready to launch Firefox on demand")


# Required function for backward compatibility
def _jupyter_server_extension_points():
    """
    Return the list of server extension entry points.
    """
    return [{"module": "jupyterlab_firefox_launcher.server_extension"}]
