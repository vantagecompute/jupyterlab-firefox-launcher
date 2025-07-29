# Copyright (c) 2025 Vantage Compute Corporation.
"""
Server proxy configuration for jupyter-server-proxy integration.
"""

from .firefox_handler import get_server_proxy_config


def setup_firefox_proxy():
    """
    Setup function for jupyter-server-proxy entry point.
    
    Returns:
        dict: Configuration for Firefox proxy
    """
    return get_server_proxy_config()['firefox']
