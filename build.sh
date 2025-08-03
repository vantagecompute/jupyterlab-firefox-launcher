#!/bin/bash

deactivate

pkill -f configurable-http-proxy
pkill -f "jupyter*"

rm -rf .venv
# Clean previous build artifacts
rm -rf jupyterlab_firefox_launcher/labextension
rm -rf lib/
rm -rf dist/

uv venv
source .venv/bin/activate
# Build wheel package with verbose output and no cache
uv build --wheel --no-cache --verbose

uv pip install dist/*.whl --no-cache-dir
uv pip install jupyterhub configurable-http-proxy jupyter-server

pkill -f configurable-http-proxy
pkill -f "jupyter*"

jupyterhub --ip=0.0.0.0 --port=8889 --debug --Authenticator.allow_all=True