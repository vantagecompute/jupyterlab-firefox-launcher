# Copyright (c) 2025 Vantage Compute Corporation.
"""
Server extension for jupyterlab_firefox_launcher.

This module registers the Firefox launcher handlers with Jupyter Server
using jupyter_server_extension_points and configures jupyter-server-proxy.
"""
from .firefox_handler import (
    FirefoxLauncherHandler,
    FirefoxCleanupHandler,
    XpraWebSocketHandler,
)
from .server_proxy import get_server_proxy_config


def _url_path_join(*parts):
    """Join URL path parts properly."""
    # Remove empty parts and clean up slashes
    parts = [part.strip("/") for part in parts if part.strip("/")]
    return "/" + "/".join(parts)


def _load_jupyter_server_extension(serverapp):
    """
    Called when the extension is loaded.

    Args:
        serverapp: The Jupyter server application instance
    """
    serverapp.log.info("Loading jupyterlab_firefox_launcher extension")

    # Register our handlers
    web_app = serverapp.web_app
    base_url = web_app.settings.get("base_url", "/")
    
    # Log the base URL for debugging
    serverapp.log.info(f"🔧 Base URL detected: {base_url}")

    # Handler for Firefox launcher API
    firefox_launcher_pattern = _url_path_join(
        base_url, "firefox-launcher", "api", "firefox"
    )

    # Handler for Firefox cleanup API
    firefox_cleanup_pattern = _url_path_join(
        base_url, "firefox-launcher", "api", "cleanup"
    )

    # Handler for Xpra WebSocket proxy
    xpra_ws_pattern = _url_path_join(
        base_url, "firefox-launcher", "ws"
    )

    # Log the patterns for debugging
    serverapp.log.info(f"🔧 Firefox launcher pattern: {firefox_launcher_pattern}")
    serverapp.log.info(f"🔧 Firefox cleanup pattern: {firefox_cleanup_pattern}")
    serverapp.log.info(f"🔧 Xpra WebSocket pattern: {xpra_ws_pattern}")

    # Add handlers - make sure patterns are properly escaped for regex
    # Use more permissive regex patterns to handle query parameters and trailing slashes
    handlers = [
        (firefox_launcher_pattern + r"/?(?:\?.*)?$", FirefoxLauncherHandler),
        (firefox_cleanup_pattern + r"/?(?:\?.*)?$", FirefoxCleanupHandler),
        (xpra_ws_pattern + r"/?(?:\?.*)?$", XpraWebSocketHandler),
    ]

    web_app.add_handlers(".*$", handlers)

    serverapp.log.info(f"🔧 Registered handler: {firefox_launcher_pattern}")
    serverapp.log.info(f"🔧 Registered handler: {firefox_cleanup_pattern}")

    # Try to register with jupyter-server-proxy if available
    try:
        # Check if jupyter-server-proxy is available
        import importlib.util

        if importlib.util.find_spec("jupyter_server_proxy") is not None:
            serverapp.log.info(
                "jupyter-server-proxy detected, registering Firefox proxy"
            )

            # The proper way is to let jupyter-server-proxy discover our entry point automatically
            # during its own initialization. We just need to ensure our configuration is accessible.
            
            registered = False

            # Method 1: Check if jupyter-server-proxy has already discovered our entry point
            try:
                import importlib.metadata
                eps = importlib.metadata.entry_points()
                if hasattr(eps, 'select'):
                    proxy_eps = eps.select(group='jupyter_serverproxy_servers')
                else:
                    proxy_eps = eps.get('jupyter_serverproxy_servers', [])
                
                firefox_found = any(ep.name == 'firefox' for ep in proxy_eps)
                if firefox_found:
                    serverapp.log.info("✅ Firefox entry point available for jupyter-server-proxy discovery")
                    registered = True
                else:
                    serverapp.log.warning("❌ Firefox entry point not found in entry points")
                    
            except Exception as ep_error:
                serverapp.log.debug(f"Entry point check failed: {ep_error}")

            # Method 2: Manual registration as fallback
            if not registered:
                try:
                    # Register our proxy configuration manually if needed
                    proxy_config = get_server_proxy_config()
                    
                    # Check if the web app has server proxy settings
                    if hasattr(web_app, 'settings') and 'server_proxy_servers' in web_app.settings:
                        web_app.settings['server_proxy_servers'].update(proxy_config)
                        registered = True
                        serverapp.log.info("✅ Registered Firefox proxy via web app settings")
                    elif hasattr(serverapp, "server_proxy_config"):
                        serverapp.server_proxy_config.update(proxy_config)
                        registered = True
                        serverapp.log.info("✅ Registered Firefox proxy via server_proxy_config")
                        
                except Exception as manual_error:
                    serverapp.log.debug(f"Manual registration failed: {manual_error}")

            if registered:
                serverapp.log.info("   Firefox should be available at /proxy/firefox/")
            else:
                serverapp.log.warning(
                    "⚠️ Could not register with jupyter-server-proxy: No compatible registration method found"
                )
                serverapp.log.warning(
                    "   Firefox launcher will use direct API endpoints instead of proxy"
                )
        else:
            serverapp.log.warning(
                "jupyter-server-proxy not available, using direct API endpoints"
            )

    except Exception as proxy_error:
        serverapp.log.error(
            f"❌ Error configuring proxy: {type(proxy_error).__name__}: {proxy_error}"
        )
        serverapp.log.info("Firefox launcher will use direct API endpoints instead")

    serverapp.log.info("jupyterlab_firefox_launcher extension loaded successfully")
    serverapp.log.info(f"Firefox launcher API available at: {firefox_launcher_pattern}")


# For backward compatibility with classic notebook server
load_jupyter_server_extension = _load_jupyter_server_extension
