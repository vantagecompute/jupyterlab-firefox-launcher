# Copyright (c) 2025 Vantage Compute Corporation.
# This file provides version information using importlib.metadata
import importlib.metadata

try:
    __version__ = importlib.metadata.version("jupyterlab_firefox_launcher")
except importlib.metadata.PackageNotFoundError:
    # Package is not installed, so use a fallback version
    __version__ = "0.1.0"

VERSION = __version__
