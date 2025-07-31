# Copyright (c) 2025 Vantage Compute Corporation.

"""
JupyterLab Firefox Launcher

A JupyterLab server extension that provides Firefox launcher functionality
through Xpra for remote desktop access.
"""

from ._version import __version__

__all__ = [
    "__version__",
]


def _jupyter_server_extension_points():
    """
    Returns a list of dictionaries with metadata describing
    where to find the `_load_jupyter_server_extension` function.
    """
    return [
        {
            "module": "jupyterlab_firefox_launcher.server_extension",
            "function": "_load_jupyter_server_extension",
        }
    ]
