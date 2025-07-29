# Copyright (c) 2025 Vantage Compute Corporation.
"""
Server proxy configuration for jupyter-server-proxy integration.
"""

from typing import Dict, Any
from .firefox_handler import _create_xpra_command, _find_free_port


def get_server_proxy_config() -> Dict[str, Dict[str, Any]]:
    """
    Get the server proxy configuration for jupyter-server-proxy.

    Returns:
        dict: Configuration dictionary for Firefox launcher proxy
    """
    return {
        "firefox": {
            "command": lambda port: _create_xpra_command(port),
            "port": _find_free_port,
            "timeout": 30,
            "new_browser_tab": False,
            "launcher_entry": {
                "title": "Firefox Browser",
                "enabled": False,  # We serve the launcher icon with the frontend
            },
        }
    }


def setup_firefox_proxy():
    """
    Setup function for jupyter-server-proxy entry point.

    Returns:
        dict: Configuration for Firefox proxy
    """
    return get_server_proxy_config()["firefox"]
