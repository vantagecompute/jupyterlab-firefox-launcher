#!/usr/bin/env python3
"""
Firefox Desktop Server Proxy Configuration

This module provides Firefox launcher functionality using jupyter-server-proxy
with Xpra HTML5 for superior performance and seamless application integration.
"""

import os
import time
import socket
from shutil import which
from pathlib import Path

HERE = Path(__file__).parent


def check_xpra_ready(port, max_attempts=5):
    """
    Check if Xpra HTML5 server is ready to accept connections.
    """
    for attempt in range(max_attempts):
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=1) as sock:
                return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            if attempt < max_attempts - 1:
                time.sleep(1)
            continue
    return False


def get_firefox_command():
    """
    Get Firefox command, checking for availability on demand.
    This function is called only when Firefox is actually launched.
    """
    # Check for Xpra (only when actually launching)
    xpra = which('xpra')
    if not xpra:
        raise RuntimeError(
            "xpra executable not found. Please install Xpra:\n"
            "  apt-get install xpra xpra-html5\n"
            "  or\n"
            "  yum install xpra python3-xpra-html5\n"
            "  or\n"
            "  conda install -c conda-forge xpra"
        )

    # Check for Firefox (only when actually launching)
    firefox = which('firefox')
    if not firefox:
        # Check macOS Firefox location
        macos_firefox = Path('/Applications/Firefox.app/Contents/MacOS/firefox')
        if macos_firefox.exists():
            firefox = str(macos_firefox)
        else:
            raise RuntimeError(
                "firefox executable not found. Please install Firefox:\n"
                "  apt-get install firefox\n"
                "  or\n"
                "  yum install firefox\n"
                "  or\n"
                "  Download from https://www.mozilla.org/firefox/"
            )

    return xpra, firefox



def create_xpra_command():
    """
    Create the Xpra command dynamically when needed.
    This function checks for dependencies only when Firefox is actually launched.
    """
    # Check dependencies only when actually needed
    xpra, firefox = get_firefox_command()

    # Create user-space socket directory for security
    socket_dir = Path.home() / '.firefox-launcher' / 'sockets'
    socket_dir.mkdir(parents=True, exist_ok=True)

    firefox_wrapper =  Path(__file__).parent.parent / 'bin' / 'firefox-xstartup'

    # Allow development override via environment variable
    if dev_launcher_path := os.getenv("DEV_FIREFOX_LAUNCHER_PATH"):
        firefox_wrapper = dev_launcher_path

    # Allow environment variable customization of Xpra options
    xpra_quality = os.getenv("FIREFOX_LAUNCHER_QUALITY", "100")
    xpra_compress = os.getenv("FIREFOX_LAUNCHER_COMPRESS", "0")
    xpra_dpi = os.getenv("FIREFOX_LAUNCHER_DPI", "96")

    # IMPORTANT: Use only TCP binding with HTML5 client - NO WebSockets for SlurmSpawner compatibility
    return [
        'xpra', 'start',
        '--bind-tcp=0.0.0.0:{port}',
        '--html=on',  # Enable HTML5 client
        '--ssl=off',  # Disable SSL entirely
        '--daemon=no',  # Run in foreground for proper process management
        '--exit-with-children=yes',  # Exit when Firefox closes
        '--start-child=' + firefox_wrapper,  # Use our custom wrapper script
        f'--socket-dirs={socket_dir}',  # User-space socket directory
        f'--socket-dir={socket_dir}',  # Explicit socket directory (different from --socket-dirs)
        '--system-proxy-socket=no',  # Disable system proxy socket
        '--mdns=no',  # Disable mDNS
        '--pulseaudio=no',  # Disable audio for simplicity
        '--notifications=no',  # Disable notifications
        '--clipboard=yes',  # Enable clipboard sharing
        '--clipboard-direction=both',  # Allow bidirectional clipboard
        '--sharing=no',  # Disable screen sharing
        '--speaker=off',  # Disable speaker
        '--microphone=off',  # Disable microphone
        '--webcam=no',  # Disable webcam
        '--desktop-scaling=auto',  # Auto-scale to browser window
        '--resize-display=yes',  # Allow display resizing
        '--cursors=yes',  # Forward custom cursors
        '--bell=no',  # Disable bell forwarding
        '--system-tray=no',  # Disable system tray forwarding
        '--global-menus=no',  # Disable global menu forwarding
        '--xsettings=yes',  # Enable xsettings sync
        '--readonly=no',  # Allow input (default but explicit)
        '--session-name=Firefox',  # Descriptive session name
        '--window-close=auto',  # Handle window close events properly
        f'--dpi={xpra_dpi}',  # Configurable DPI
        f'--compress={xpra_compress}',  # Configurable compression
        f'--quality={xpra_quality}',  # Configurable quality
        '--encoding=auto',  # Auto-select best encoding
        '--min-quality=30',  # Minimum quality threshold
        '--min-speed=30',  # Minimum speed threshold
        '--auto-refresh-delay=0.15',  # Default refresh delay
        # X session configuration
        '--xvfb=/usr/bin/Xvfb +extension GLX +extension Composite -screen 0 1920x1080x24+32 -dpi 96 -nolisten tcp -noreset',
        '--fake-xinerama=auto',  # Enable fake xinerama support
        '--use-display=no',  # Don't use existing display
        '--start-new-commands=yes',  # Allow starting new commands
        # Environment variables
        '--env=PATH=/usr/local/bin:/usr/bin:/bin',  # Ensure PATH includes standard directories
        '--env=DISPLAY=:0',  # Explicit display setting
        f'--env=XDG_RUNTIME_DIR={socket_dir.parent}',  # Set XDG_RUNTIME_DIR to our directory
        f'--env=TMPDIR={socket_dir.parent}',  # Set temp directory
        # Security and cleanup
        '--dbus-launch=',  # Disable D-Bus launch to avoid warnings
        '--dbus-proxy=no',  # Disable D-Bus proxy
        '--remote-logging=no',  # Disable remote logging for security
        '--bandwidth-detection=no',  # Disable auto bandwidth detection
        '--pings=yes',  # Enable keepalive pings (default 5s)
    ]


def launch_firefox():
    """
    Setup function for jupyter-server-proxy to launch Firefox with Xpra HTML5.
    
    This is the entry point function that follows the jupyter-server-proxy pattern.
    It returns configuration dict for jupyter-server-proxy to manage an Xpra
    session with Firefox, providing excellent performance and direct HTML5 support.
    """
    
    return {
        'command': create_xpra_command,  # Use callable that checks dependencies on demand
        'timeout': 60,  # Increased timeout for slower systems
        'new_browser_tab': False,  # Open in JupyterLab tab, not browser tab
        # DISABLED: launcher_entry - we handle launcher through frontend extension
        "launcher_entry": {
            "enabled": False,  # Enable launcher entry via jupyter-server-proxy
        },
        "port": 0,  # Let jupyter-server-proxy assign a random port
        "mappath": {"/": "/index.html"},  # Map root to Xpra HTML5 client
        "request_headers_override": {
            "X-Forwarded-Proto": "http"  # Ensure proper protocol handling
        },
        # Custom health check function
        "ready_check": lambda port: check_xpra_ready(port),
    }