"""
Jupyter configuration for Firefox launcher with jupyter-server-proxy
"""

import os

# This function will be called by jupyter-server-proxy
def _get_firefox_config():
    # Get the script path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, 'launch-firefox-xpra.sh')
    script_path = os.path.abspath(script_path)
    
    def get_port():
        try:
            with open('/tmp/xpra-port', 'r') as f:
                return int(f.read().strip())
        except:
            return 15000  # Default fallback port
    
    return {
        "command": [script_path],
        "timeout": 30,
        "port": get_port,
        "mappath": {"/": "/"},
        "launcher_entry": {
            "title": "Firefox Browser", 
            "icon_path": "/usr/share/icons/hicolor/48x48/apps/firefox.png",
        },
    }


# For direct configuration if loaded as a config file
try:
    c = get_config()  # This will work when loaded by Jupyter
    
    if not hasattr(c, 'ServerProxy'):
        c.ServerProxy = type('ServerProxy', (), {})()

    if not hasattr(c.ServerProxy, 'servers'):
        c.ServerProxy.servers = {}

    c.ServerProxy.servers['firefox'] = _get_firefox_config()
except NameError:
    # get_config() not available, this is fine when imported as a module
    pass
