#!/bin/bash
"""
Test script to verify SESSION_DIR-based path building in firefox-xstartup
"""

# Test with SESSION_DIR set
echo "=== Testing with SESSION_DIR set ==="
export SESSION_DIR="/home/test/.firefox-launcher/sessions/session-8001"
export FIREFOX_WINDOW_SIZE="1280,800"
export FIREFOX_START_URL="https://example.com"
export FIREFOX_CLASS_NAME="Firefox-Test"

# Run just the path-building part of firefox-xstartup
echo "SESSION_DIR: $SESSION_DIR"

if [ -n "$SESSION_DIR" ]; then
    SESSION_DIR=${SESSION_DIR%/}  # Ensure no trailing slash
    FIREFOX_PROFILE_DIR="$SESSION_DIR/profile"
    FIREFOX_CACHE_DIR="$SESSION_DIR/cache"
    FIREFOX_TEMP_DIR="$SESSION_DIR/temp"
    echo "Profile directory: $FIREFOX_PROFILE_DIR"
    echo "Cache directory: $FIREFOX_CACHE_DIR"
    echo "Temp directory: $FIREFOX_TEMP_DIR"
else
    FIREFOX_PROFILE_DIR="$HOME/.firefox-launcher/sessions/default/profile"
    FIREFOX_CACHE_DIR="$HOME/.firefox-launcher/sessions/default/cache"
    FIREFOX_TEMP_DIR="$HOME/.firefox-launcher/sessions/default/temp"
    echo "Using default unified session directories"
fi

PROFILE_NAME="firefox-launcher-$(basename "$SESSION_DIR" 2>/dev/null || echo "default")"
echo "Profile name would be: $PROFILE_NAME"

echo
echo "=== Testing without SESSION_DIR (fallback) ==="
unset SESSION_DIR

if [ -n "$SESSION_DIR" ]; then
    SESSION_DIR=${SESSION_DIR%/}
    FIREFOX_PROFILE_DIR="$SESSION_DIR/profile"
    FIREFOX_CACHE_DIR="$SESSION_DIR/cache"
    FIREFOX_TEMP_DIR="$SESSION_DIR/temp"
    echo "Profile directory: $FIREFOX_PROFILE_DIR"
    echo "Cache directory: $FIREFOX_CACHE_DIR"
    echo "Temp directory: $FIREFOX_TEMP_DIR"
else
    FIREFOX_PROFILE_DIR="$HOME/.firefox-launcher/sessions/default/profile"
    FIREFOX_CACHE_DIR="$HOME/.firefox-launcher/sessions/default/cache"
    FIREFOX_TEMP_DIR="$HOME/.firefox-launcher/sessions/default/temp"
    echo "Using default unified session directories"
    echo "Profile directory: $FIREFOX_PROFILE_DIR"
    echo "Cache directory: $FIREFOX_CACHE_DIR"  
    echo "Temp directory: $FIREFOX_TEMP_DIR"
fi

PROFILE_NAME="firefox-launcher-$(basename "$SESSION_DIR" 2>/dev/null || echo "default")"
echo "Profile name would be: $PROFILE_NAME"

echo
echo "=== Path building test completed ==="
