import os
import subprocess
from tornado import web
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from jupyter_server.extension.application import ExtensionApp


class FirefoxLauncherHandler(APIHandler):
    @web.authenticated
    def post(self):
        # Only spawn if not already running
        if not self._is_firefox_running():
            try:
                # This can be replaced with your preferred X11 setup (e.g., xvfb-run)
                subprocess.Popen(
                    [
                        "xvfb-run",
                        "--auto-servernum",
                        "--server-args=-screen 0 1024x768x24",
                        "firefox"
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                self.finish({"status": "started"})
            except Exception as e:
                self.set_status(500)
                self.finish({"error": str(e)})
        else:
            self.finish({"status": "already running"})

    def _is_firefox_running(self):
        try:
            out = subprocess.check_output(["pgrep", "-f", "firefox"])
            return bool(out.strip())
        except subprocess.CalledProcessError:
            return False


def setup_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, "jupyterhub-firefox-launcher", "launch")
    handlers = [(route_pattern, FirefoxLauncherHandler)]
    web_app.add_handlers(host_pattern, handlers)


class FirefoxLauncherExtension(ExtensionApp):
    """JupyterLab Firefox Launcher Extension"""
    
    name = "jupyterlab_firefox_launcher"
    
    def initialize_handlers(self):
        """Initialize the extension handlers"""
        setup_handlers(self.serverapp.web_app)


def _jupyter_labextension_paths():
    """Return metadata for the labextension"""
    return [{
        "src": "labextension",
        "dest": "jupyterlab-firefox-launcher"
    }]


def _jupyter_server_extension_points():
    """Return the server extension points"""
    return [{
        "module": "jupyterlab_firefox_launcher.server",
        "app": FirefoxLauncherExtension
    }]


def _load_jupyter_server_extension(server_app):
    """Load the server extension"""
    extension = FirefoxLauncherExtension()
    extension.initialize(server_app)
    extension.initialize_handlers()

