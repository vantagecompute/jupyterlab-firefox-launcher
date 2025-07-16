#!/usr/bin/env python3
"""
Firefox Desktop Server Proxy Configuration

This module provides Firefox launcher functionality using jupyter-server-proxy
with Xpra HTML5 for superior performance and seamless application integration.
"""

import os
import stat
import time
import socket
from shutil import which
from pathlib import Path

HERE = Path(__file__).parent


def check_xpra_ready(port, max_attempts=30):
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


def setup_firefox_desktop():
    """
    Setup function for jupyter-server-proxy to launch Firefox with Xpra HTML5.
    
    Returns configuration dict for jupyter-server-proxy to manage an Xpra
    session with Firefox, providing excellent performance and direct HTML5 support.
    """
    
    # Check for Xpra
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

    # Check for Firefox
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

    # Create user-space socket directory for security
    socket_dir = Path.home() / '.firefox-launcher' / 'sockets'
    socket_dir.mkdir(parents=True, exist_ok=True)

    # Path to our Firefox wrapper script
    firefox_wrapper = os.getenv("FIREFOX_LAUNCHER_WRAPPER", str(HERE / 'share' / 'firefox-xstartup'))
    
    # Alternative advanced wrapper with more options
    firefox_wrapper_advanced = str(HERE / 'share' / 'firefox-wrapper-advanced')
    
    # Use advanced wrapper if requested via environment variable
    if os.getenv("FIREFOX_LAUNCHER_ADVANCED", "").lower() in ("1", "true", "yes"):
        firefox_wrapper = firefox_wrapper_advanced
    
    # Fallback: if wrapper scripts don't exist or aren't accessible, use direct firefox command
    wrapper_available = False
    if os.path.exists(firefox_wrapper):
        wrapper_available = True
    elif os.path.exists(firefox_wrapper_advanced):
        firefox_wrapper = firefox_wrapper_advanced
        wrapper_available = True
    
    if not wrapper_available:
        # Create a minimal inline wrapper
        firefox_wrapper = os.path.expanduser("~/.firefox-launcher-wrapper.sh")
        wrapper_content = f'''#!/bin/bash
# Auto-generated Firefox wrapper for JupyterLab extension
export MOZ_DISABLE_CONTENT_SANDBOX=1
export MOZ_DISABLE_GMP_SANDBOX=1
exec {firefox} --new-instance --no-first-run --profile ~/.firefox-launcher-profile "$@"
'''
        with open(firefox_wrapper, 'w') as f:
            f.write(wrapper_content)
        os.chmod(firefox_wrapper, 0o755)
    else:
        # Make sure the wrapper script is executable
        # Handle NFS/shared installation where we can't modify permissions
        import stat
        if os.path.exists(firefox_wrapper):
            try:
                st = os.stat(firefox_wrapper)
                # Only try to set executable if we don't already have execute permission
                if not (st.st_mode & stat.S_IEXEC):
                    os.chmod(firefox_wrapper, st.st_mode | stat.S_IEXEC)
            except PermissionError:
                # In shared/NFS environments, the file should already be executable
                # or we need to copy it to user space
                st = os.stat(firefox_wrapper)
                if not (st.st_mode & stat.S_IEXEC):
                    # Copy to user space and make executable
                    user_wrapper = os.path.expanduser(f"~/.firefox-launcher-{os.path.basename(firefox_wrapper)}")
                    import shutil
                    shutil.copy2(firefox_wrapper, user_wrapper)
                    os.chmod(user_wrapper, st.st_mode | stat.S_IEXEC)
                    firefox_wrapper = user_wrapper

    # Allow environment variable customization of Xpra options
    xpra_quality = os.getenv("FIREFOX_LAUNCHER_QUALITY", "100")
    xpra_compress = os.getenv("FIREFOX_LAUNCHER_COMPRESS", "0")
    xpra_dpi = os.getenv("FIREFOX_LAUNCHER_DPI", "96")
    
    # Build Xpra command using --start-child with our wrapper script
    # This gives us full control over Firefox options while using Xpra's process management
    # IMPORTANT: Use only TCP binding with HTML5 client - NO WebSockets for SlurmSpawner compatibility
    xpra_command = [
        'xpra', 'start',
        '--bind-tcp=0.0.0.0:{port}',  # {port} expanded by jupyter-server-proxy
        '--html=on',  # Enable HTML5 client
        # NOTE: NOT using --bind-ws or --bind-wss to avoid WebSocket connections
        '--ssl=off',  # Disable SSL entirely  
        '--daemon=no',  # Run in foreground for proper process management
        '--exit-with-children=yes',  # Exit when Firefox closes
        '--start-child=' + firefox_wrapper,  # Use our custom wrapper script
        f'--socket-dirs={socket_dir}',  # User-space socket directory
        '--system-proxy-socket=no',  # Disable system proxy socket
        '--mdns=no',  # Disable mDNS
        '--pulseaudio=no',  # Disable audio for simplicity
        '--notifications=no',  # Disable notifications
        '--clipboard=yes',  # Enable clipboard sharing
        '--sharing=no',  # Disable screen sharing
        '--speaker=no',  # Disable speaker
        '--microphone=no',  # Disable microphone
        '--webcam=no',  # Disable webcam
        '--desktop-scaling=auto',  # Auto-scale to browser window
        f'--dpi={xpra_dpi}',  # Configurable DPI
        f'--compress={xpra_compress}',  # Configurable compression
        f'--quality={xpra_quality}',  # Configurable quality
        '--window-close=auto',  # Handle window close events properly
        # X session fixes for "true" command issue
        '--xvfb=/usr/bin/Xvfb +extension Composite -screen 0 1920x1080x24+32 -nolisten tcp -noreset',
        '--start-new-commands=yes',  # Allow starting new commands
        '--env=PATH=/usr/local/bin:/usr/bin:/bin',  # Ensure PATH includes standard directories
        # Reduce warning messages and fix XDG runtime directory issues
        '--dbus-launch=',  # Disable D-Bus launch to avoid warnings
        f'--socket-dir={socket_dir}',  # Explicit socket directory (different from --socket-dirs)
    ]

    return {
        'command': xpra_command,
        'timeout': 60,  # Increased timeout for slower systems
        'new_browser_window': False,  # Open in JupyterLab tab, not new browser window
        # Note: launcher_entry removed - let frontend extension handle launcher icon
        # This prevents conflicts between server proxy and frontend launcher
        "port": 0,  # Let jupyter-server-proxy assign a random port
        "mappath": {"/": "/index.html"},  # Map root to Xpra HTML5 client
        "request_headers_override": {
            "X-Forwarded-Proto": "http"  # Ensure proper protocol handling
        },
        # Custom health check function
        "ready_check": lambda port: check_xpra_ready(port),
    }
