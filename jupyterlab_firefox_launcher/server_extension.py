# Copyright (c) 2025 Vantage Compute Corporation.
"""
Server extension for jupyterlab_firefox_launcher.

This module registers the Firefox launcher handlers with Jupyter Server
using jupyter_server_extension_points and configures jupyter-server-proxy.
"""
from .firefox_handler import (
    FirefoxLauncherHandler,
    FirefoxCleanupHandler,
    get_server_proxy_config,
)


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

    # Handler for Firefox launcher API
    firefox_launcher_pattern = _url_path_join(
        base_url, "firefox-launcher", "api", "firefox"
    )

    # Handler for Firefox cleanup API
    firefox_cleanup_pattern = _url_path_join(
        base_url, "firefox-launcher", "api", "cleanup"
    )

    # Add handlers - make sure patterns are properly escaped for regex
    handlers = [
        (firefox_launcher_pattern + r"(?:\?.*)?", FirefoxLauncherHandler),
        (firefox_cleanup_pattern + r"(?:\?.*)?", FirefoxCleanupHandler),
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

            # Register our proxy configuration
            proxy_config = get_server_proxy_config()

        # Try multiple methods to register with jupyter-server-proxy
        registered = False

        # Method 1: Direct server proxy config attribute
        if hasattr(serverapp, "server_proxy_config"):
            serverapp.server_proxy_config.update(proxy_config)
            registered = True
            serverapp.log.info("✅ Registered Firefox proxy via server_proxy_config")

        # Method 2: Check for ServerProxyApp in extensions
        elif hasattr(serverapp, "extension_manager"):
            try:
                # Try to find and configure server proxy extension
                for ext_name, ext_instance in getattr(
                    serverapp.extension_manager, "extensions", {}
                ).items():
                    if "server_proxy" in ext_name.lower():
                        if hasattr(ext_instance, "proxy_config"):
                            ext_instance.proxy_config.update(proxy_config)
                            registered = True
                            serverapp.log.info(
                                f"✅ Registered Firefox proxy via extension {ext_name}"
                            )
                            break
            except Exception as ext_error:
                serverapp.log.debug(f"Extension registration failed: {ext_error}")

        # Method 3: Try to register via jupyter_server_proxy directly
        if not registered:
            try:
                from jupyter_server_proxy.api import setup_proxy

                # This may not work in all versions, but worth trying
                setup_proxy(serverapp, proxy_config)
                registered = True
                serverapp.log.info(
                    "✅ Registered Firefox proxy via jupyter_server_proxy.api"
                )
            except (ImportError, AttributeError) as api_error:
                serverapp.log.debug(f"API registration failed: {api_error}")

        if not registered:
            serverapp.log.warning(
                "⚠️ Could not register with jupyter-server-proxy: No compatible registration method found"
            )
            serverapp.log.warning(
                "   Firefox launcher will use direct API endpoints instead of proxy"
            )

    except ImportError:
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
