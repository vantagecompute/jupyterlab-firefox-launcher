#!/usr/bin/env bash
# build.sh

set -e

echo "🔄 Pre-build cleanup and version sync"
# Remove build artifacts and nested duplicate directories
rm -rf dist
rm -rf build

uv run sync_version.py

echo "🏗️  Building with uv"
uv build

echo "🎉 Build complete"

