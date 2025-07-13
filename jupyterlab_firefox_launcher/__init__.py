
__version__ = "0.1.4"

def _jupyter_labextension_paths():
    """Return metadata for the labextension"""
    return [{
        "src": "labextension",
        "dest": "jupyterlab-firefox-launcher"
    }]

def _jupyter_server_extension_points():
    return [{
        "module": "jupyterlab_firefox_launcher"
    }]

def _load_jupyter_server_extension(server_app):
    from .server import setup_handlers
    setup_handlers(server_app.web_app)
    server_app.log.info("Loaded jupyterlab_firefox_launcher extension")

