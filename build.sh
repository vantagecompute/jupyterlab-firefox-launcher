#!/usr/bin/env bash
# build.sh

set -e
echo "🔄 Pre-build cleanup and version sync"
rm -rf jupyterlab_firefox_launcher/labextension lib dist
uv run sync_version.py
node copy-package-json-to-labextension.cjs || true

echo "🏗️  Building with uv"
uv build

