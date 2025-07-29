#!/bin/bash
# Helper script to create a new release
# Usage: ./scripts/create_release.sh [new_version]
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}


# Generate updated changelog
print_info "Generating changelog with git-cliff..."


# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository"
    exit 1
fi

# Check if working directory is clean
if ! git diff-index --quiet HEAD --; then
    print_error "Working directory is not clean. Please commit or stash your changes."
    exit 1
fi


# Get current version from pyproject.toml
CURRENT_VERSION=$(python3 -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
print(data['project']['version'])
" 2>/dev/null)

if [ $? -ne 0 ]; then
    print_error "Could not read version from pyproject.toml"
    exit 1
fi

print_info "Current version: $CURRENT_VERSION"

# Get new version from argument or prompt
if [ -n "$1" ]; then
    NEW_VERSION="$1"
else
    echo -n "Enter new version (current: $CURRENT_VERSION): "
    read NEW_VERSION
fi

if [ -z "$NEW_VERSION" ]; then
    print_error "Version cannot be empty"
    exit 1
fi

# Check if git-cliff is available
if ! command -v git-cliff &> /dev/null; then
    print_warning "git-cliff not found. Installing via cargo..."
    if command -v cargo &> /dev/null; then
        cargo install git-cliff
    else
        print_error "git-cliff not available and cargo not found for installation"
        print_error "Please install git-cliff: https://github.com/orhun/git-cliff#installation"
        exit 1
    fi
fi

# Generate changelog up to the new version
git-cliff --tag "$NEW_VERSION" --output CHANGELOG.md
if [ $? -eq 0 ]; then
    print_info "✅ Changelog updated successfully"
else
    print_error "Failed to generate changelog"
    exit 1
fi


# Validate version format (basic semver check)
if ! echo "$NEW_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$'; then
    print_warning "Version '$NEW_VERSION' doesn't follow semantic versioning format"
    echo -n "Continue anyway? (y/N): "
    read CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        print_info "Cancelled"
        exit 0
    fi
fi

# Check if tag already exists
if git tag -l | grep -q "^$NEW_VERSION$"; then
    print_error "Tag $NEW_VERSION already exists"
    exit 1
fi

print_info "Preparing release $NEW_VERSION..."

# Update version in pyproject.toml, package.json, and docs
# Update pyproject.toml using sed
sed -i 's/^version = ".*"/version = "'$NEW_VERSION'"/' pyproject.toml

# Update package.json using sed
sed -i 's/"version": ".*"/"version": "'$NEW_VERSION'"/' package.json

# Update docs version data file
UPDATED_DATE=$(date +%Y-%m-%d)
print_info "Updating documentation version data..."

# Create docs directory if it doesn't exist
mkdir -p docs/_data

# Update Jekyll data file with new version and date
cat > docs/_data/project.yml << EOF
# Copyright (c) 2025 Vantage Compute Corporation.
# Project metadata - auto-generated, do not edit manually
version: "$NEW_VERSION"
updated: "$UPDATED_DATE"
EOF

print_info "✅ Updated pyproject.toml, package.json, and docs/_data/project.yml to version $NEW_VERSION"

if [ $? -ne 0 ]; then
    print_error "Failed to update version files."
    exit 1
fi

# Add and commit version changes
git add pyproject.toml package.json docs/_data/project.yml CHANGELOG.md
git commit -m "Bump version to $NEW_VERSION"

# Create and push tag
print_info "Creating tag $NEW_VERSION..."
git tag -a "$NEW_VERSION" -m "Release $NEW_VERSION"

print_info "Pushing changes and tag..."
git push origin main
git push origin "$NEW_VERSION"

print_info "Release $NEW_VERSION created successfully!"
print_info "GitHub Actions will now build and publish the release."
print_info "Check the Actions tab for progress: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')/actions"
