# Copyright (c) 2025 Vantage Compute Corporation.
"""
Server proxy configuration for jupyter-server-proxy integration.
"""

import logging
from typing import Dict, Any, List
from .firefox_handler import _create_xpra_command, _find_free_port, _check_dependencies

_logger = logging.getLogger(__name__)


def _firefox_launcher_command(port: int | None = None, base_url: str = "/") -> List[str]:
    """
    Create a command that jupyter-server-proxy can use to launch Firefox via Xpra.
    
    This is called by jupyter-server-proxy when a user accesses the proxy URL.
    
    Args:
        port: Port number assigned by jupyter-server-proxy (we ignore this and find our own)
        base_url: Base URL for the proxy (passed by jupyter-server-proxy)
    
    Returns:
        List[str]: Command to launch Xpra with Firefox
    """
    try:
        # Check dependencies first
        dep_check = _check_dependencies()
        if not dep_check["all_present"]:
            missing_names = [dep['name'] for dep in dep_check['missing']]
            _logger.error(f"Firefox launcher dependencies missing: {missing_names}")
            raise RuntimeError(f"Missing dependencies: {', '.join(missing_names)}")
        
        # Find a free port for Xpra (ignore the port passed by jupyter-server-proxy)
        # We need to find our own port because Xpra needs specific port handling
        xpra_port = _find_free_port()
        if not xpra_port:
            raise RuntimeError("Could not find a free port for Xpra")
            
        # Create the Xpra command for this port
        xpra_cmd = _create_xpra_command(xpra_port)
        
        _logger.info(f"jupyter-server-proxy launching Firefox on port {xpra_port} (proxy port: {port})")
        _logger.info(f"Command: {' '.join(xpra_cmd[:3])}...")  # Log first few parts
        
        return xpra_cmd
        
    except Exception as e:
        _logger.error(f"Firefox launcher command creation failed: {e}")
        raise


def get_server_proxy_config() -> Dict[str, Dict[str, Any]]:
    """
    Get the server proxy configuration for jupyter-server-proxy.

    Returns:
        dict: Configuration dictionary for Firefox launcher proxy
    """
    return {
        "firefox": {
            "command": _firefox_launcher_command,
            "port": _find_free_port,  # Port function for jupyter-server-proxy
            "timeout": 30,
            "new_browser_tab": False,
            "launcher_entry": {
                "title": "Firefox Browser",
                "enabled": False,
            },
            "environment": {
                "XPRA_CRASH_DEBUG": "1",
            },
            "absolute_url": False,  # Use relative URLs
            "request_headers_override": {
                "Sec-WebSocket-Protocol": "binary",  # Required for Xpra WebSocket
            },
            "rewrite_response": False,
        }
    }


def setup_firefox_proxy():
    """
    Setup function for jupyter-server-proxy entry point.

    Returns:
        dict: Configuration for Firefox proxy
    """
    return get_server_proxy_config()["firefox"]
