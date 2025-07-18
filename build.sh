#!/usr/bin/env bash
# build.sh

set -e

echo "🔄 Pre-build cleanup and version sync"
# Remove build artifacts and nested duplicate directories
rm -rf dist
rm -rf build
rm -rf lib
rm -rf jupyterlab_firefox_launcher/labextension/{lib,static}

uv run sync_version.py

echo "🏗️  Building with uv"
uv build

echo "🎉 Build complete"

