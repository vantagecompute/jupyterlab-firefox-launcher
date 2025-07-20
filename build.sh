#!/usr/bin/env bash
# build.sh

set -e

echo "🔄 Pre-build cleanup and version sync"
# Remove build artifacts and nested duplicate directories
rm -rf dist
rm -rf jupyterlab_firefox_launcher/labextension/{built,lib}


python3 sync_version.py

echo "🏗️  Building with uv"
uv build --wheel

echo "🎉 Build complete"

