#!/usr/bin/env bash
# build.sh

set -e

echo "🔄 Pre-build cleanup and version sync"
# Remove build artifacts and nested duplicate directories
rm -rf dist
rm -rf build/
rm -rf *.egg-info/
rm -rf jupyterlab_firefox_launcher.egg-info/


# Nuke Python bytecode caches
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "🧨 All caches nuked!"


echo "🏗️  Building with uv"
uv build --wheel --no-cache --verbose

uv pip uninstall jupyterlab-firefox-launcher

uv pip install dist/jupyterlab_firefox_launcher-*.whl

echo "🎉 Build complete"

