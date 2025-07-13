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



