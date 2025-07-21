#!/usr/bin/env bash
# build.sh

set -e

echo "🔄 Pre-build cleanup and version sync"
# Remove build artifacts and nested duplicate directories
rm -rf dist
rm -rf jupyterlab_firefox_launcher/labextension/{built,lib}

echo "💥 NUKING ALL BUILD CACHES"
# Clear installed extension cache to remove old CSS files
rm -rf .venv/share/jupyter/labextensions/jupyterlab-firefox-launcher/

# Nuke Python build caches
rm -rf build/
rm -rf *.egg-info/
rm -rf jupyterlab_firefox_launcher.egg-info/

# Nuke TypeScript/JavaScript build caches
rm -rf jupyterlab_firefox_launcher/labextension/node_modules/
rm -rf jupyterlab_firefox_launcher/labextension/.webpack_cache/
rm -rf jupyterlab_firefox_launcher/labextension/tsconfig.tsbuildinfo
rm -rf jupyterlab_firefox_launcher/labextension/webpack.config.*

# Nuke webpack and TypeScript caches
rm -rf .webpack_cache/
rm -rf .tscache/
rm -rf tsconfig.tsbuildinfo

# Nuke any JupyterLab staging/build directories
rm -rf .venv/share/jupyter/lab/staging/
rm -rf .venv/share/jupyter/lab/static/

# Nuke Python bytecode caches
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "🧨 All caches nuked!"


python3 sync_version.py

echo "🏗️  Building with uv"
uv build --wheel

echo "🎉 Build complete"

