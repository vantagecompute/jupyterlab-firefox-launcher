#!/bin/bash
# Copyright (c) 2025 Vantage Compute Corporation.

rm -rf jupyterlab_firefox_launcher/labextension/static
rm -rf jupyterlab_firefox_launcher/labextension/package.json
rm -rf lib/
rm -rf dist/

uv build --wheel --no-cache --verbose
