"""
Jupyter Server configuration for Firefox launcher
"""

c = get_config()

# Import and use our entry point function directly
def firefox_desktop_config():
    from jupyterlab_firefox_launcher.server_proxy import launch_firefox
    return launch_firefox()

# Configure jupyter-server-proxy to register our Firefox server
c.ServerProxy.servers = {
    'firefox-browser': firefox_desktop_config()
}
