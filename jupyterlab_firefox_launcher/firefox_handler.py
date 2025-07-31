# Copyright (c) 2025 Vantage Compute Corporation.
"""
Firefox launcher handler for JupyterLab extension.

This module provides the server-side handler for launching Firefox
and managing the process lifecycle.
"""

import asyncio
import json
import logging
import os
import shlex
import socket
import subprocess
import sys
import shutil
import traceback
from pathlib import Path
from shutil import which
from typing import Any, Dict, List

import psutil
from jupyter_server.base.handlers import JupyterHandler
from tornado import web

# Set up a logger for this module
if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

_logger = logging.getLogger(__name__)


def _cleanup_firefox_profile(port: int) -> bool:
    """
    Clean up Firefox profile directory and session-specific directories for a given port.

    Args:
        port: The port number of the Xpra process
    Returns:
        True if cleanup was successful or profile didn't exist, False otherwise
    """

    try:
        home_dir = Path.home()

        # Clean up entire session directory (contains profile, sockets, runtime, temp)
        session_dir = home_dir / ".firefox-launcher" / "sessions" / f"session-{port}"
        if session_dir.exists():
            _logger.info(f"🧹 Cleaning up complete session directory: {session_dir}")
            shutil.rmtree(session_dir)
            _logger.info(f"✅ Successfully removed session directory: {session_dir}")
        else:
            _logger.debug(f"No session directory found for port {port}: {session_dir}")

        return True

    except Exception as e:
        _logger.error(
            f"❌ Error cleaning up Firefox profile for port {port}: {type(e).__name__}: {str(e)}"
        )

        # Log traceback only in debug mode
        if _logger.isEnabledFor(10):  # DEBUG level
            _logger.debug(f"Profile cleanup traceback: {traceback.format_exc()}")

        return False


def _find_free_port():
    """Find a free port for Xpra server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def _get_xpra_and_firefox_exec_paths():
    """
    Get Firefox command, checking for availability on demand.
    This function is called only when Firefox is actually launched.
    """
    # Check for Xpra (only when actually launching)
    xpra = which("xpra")
    if not xpra:
        raise RuntimeError(
            "xpra executable not found. Please install Xpra:\n"
            "  apt-get install xpra\n"
            "  or\n"
            "  yum install xpra\n"
            "  or\n"
            "  conda install -c conda-forge xpra"
        )

    # Check for Firefox (only when actually launching)
    firefox = which("firefox")
    if not firefox:
        raise RuntimeError(
            "firefox executable not found. Please install Firefox:\n"
            "  apt-get install firefox\n"
            "  or\n"
            "  yum install firefox\n"
            "  or\n"
            "  Download from https://www.mozilla.org/firefox/"
        )
    return xpra, firefox


def _create_xpra_command(port: int) -> List[str]:
    """
    Create the Xpra command dynamically when needed.
    This allows us to avoid hardcoding the command in the handler.

    Args:
        port (int): The port number assigned by jupyter-server-proxy
    """

    _logger.info("🔍 Resolving system dependencies...")
    _logger.debug("   Checking for Xpra executable...")

    # Check dependencies only when actually needed
    xpra, firefox = _get_xpra_and_firefox_exec_paths()

    _logger.info(f"✅ Xpra command resolved: {xpra}")
    _logger.info(f"✅ Firefox command resolved: {firefox}")

    # Create unified session directory structure for complete isolation
    session_dir = Path.home() / ".firefox-launcher" / "sessions" / f"session-{port}"
    _logger.info(f"Creating unified session directory: {session_dir}")
    session_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories within the session directory
    socket_dir = session_dir / "sockets"
    runtime_dir = session_dir / "runtime"
    profile_dir = session_dir / "profile"
    temp_dir = session_dir / "temp"

    # Create all subdirectories with proper permissions
    socket_dir.mkdir(exist_ok=True)
    runtime_dir.mkdir(exist_ok=True)
    profile_dir.mkdir(exist_ok=True)
    temp_dir.mkdir(exist_ok=True)

    # Set strict permissions for runtime directory (required by D-Bus)
    runtime_dir.chmod(0o700)  # Only owner can read/write/execute
    _logger.debug(f"Set runtime directory permissions to 700: {runtime_dir}")

    # Set reasonable permissions for other directories
    socket_dir.chmod(0o755)
    profile_dir.chmod(0o755)
    temp_dir.chmod(0o755)

    _logger.info("✓ Session directory structure ready:")
    _logger.info(f"   Session root: {session_dir}")
    _logger.info(f"   Sockets: {socket_dir}")
    _logger.info(f"   Runtime: {runtime_dir}")
    _logger.info(f"   Profile: {profile_dir}")
    _logger.info(f"   Temp: {temp_dir}")

    # Look for firefox-xstartup script in installed location first, then fallback to development location
    _logger.info("🔍 Locating firefox-xstartup wrapper script...")
    firefox_wrapper = which("firefox-xstartup")
    if not firefox_wrapper:
        _logger.debug(
            "   firefox-xstartup not found in PATH, trying development location..."
        )
        # Fallback to development location
        firefox_wrapper = Path(__file__).parent.parent / "scripts" / "firefox-xstartup"
        _logger.debug(f"   Checking development path: {firefox_wrapper}")
        if not firefox_wrapper.exists():
            error_msg = "firefox-xstartup script not found. Please ensure the package is properly installed."
            _logger.error("❌ CRITICAL: firefox-xstartup script not found!")
            _logger.error(f"   Checked in PATH: {os.environ.get('PATH', 'N/A')}")
            _logger.error(f"   Checked development location: {firefox_wrapper}")
            raise RuntimeError(error_msg)
        _logger.info(
            f"✅ Found firefox-xstartup at development location: {firefox_wrapper}"
        )
    else:
        _logger.info(f"✅ Found firefox-xstartup in PATH: {firefox_wrapper}")

    # Verify script is executable
    if not os.access(firefox_wrapper, os.X_OK):
        _logger.error(
            f"❌ firefox-xstartup script is not executable: {firefox_wrapper}"
        )
        try:
            os.chmod(firefox_wrapper, 0o755)
            _logger.info(f"✅ Made firefox-xstartup executable: {firefox_wrapper}")
        except Exception as chmod_error:
            error_msg = f"Failed to make script executable: {chmod_error}"
            _logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
    else:
        _logger.debug("✓ firefox-xstartup script has executable permissions")

    # Allow development override via environment variable
    if dev_launcher_path := os.getenv("DEV_FIREFOX_LAUNCHER_PATH"):
        _logger.info(
            f"🔧 Development override: Using firefox wrapper from DEV_FIREFOX_LAUNCHER_PATH={dev_launcher_path}"
        )
        firefox_wrapper = dev_launcher_path

    # Allow environment variable customization of Xpra options
    xpra_quality = os.getenv("FIREFOX_LAUNCHER_QUALITY", "100")
    xpra_compress = os.getenv("FIREFOX_LAUNCHER_COMPRESS", "none")
    xpra_dpi = os.getenv("FIREFOX_LAUNCHER_DPI", "96")

    _logger.info(
        "📋 Xpra configuration: quality={xpra_quality}, compress={xpra_compress}, dpi={xpra_dpi}"
    )

    # Check Xpra version to adjust compatibility
    try:
        result = subprocess.run(
            [xpra, "--version"], capture_output=True, text=True, timeout=5
        )
        xpra_version = result.stdout.strip() if result.returncode == 0 else "unknown"
        _logger.info(f"📋 Xpra version detected: {xpra_version}")

        # Inform about older Xpra version limitations
        if "v3.1" in xpra_version or "v3.0" in xpra_version:
            _logger.info(
                "⚠️ Xpra v3.x detected - some session warnings are expected but harmless"
            )
            _logger.info(
                "   You may see 'Xsession: unable to launch true' warnings - these can be ignored"
            )
    except Exception as version_error:
        _logger.debug(f"Could not detect Xpra version: {version_error}")

    # Log key configuration decisions
    _logger.info("🔧 Xpra Configuration Decisions:")
    _logger.info(f"   TCP Binding: 0.0.0.0:{port} (all interfaces)")
    _logger.info(
        "   HTML5 Client: Enabled (no WebSockets for SlurmSpawner compatibility)"
    )
    _logger.info("   Daemon Mode: Disabled (foreground for process management)")
    _logger.info(f"   Child Process: {firefox_wrapper}")
    _logger.info(f"   Session Directory: {session_dir} (unified session structure)")
    _logger.info(f"   Socket Directory: {socket_dir}")
    _logger.info(f"   Runtime Directory: {runtime_dir}")
    _logger.info(f"   Profile Directory: {profile_dir}")
    _logger.info(f"   Temp Directory: {temp_dir}")
    _logger.info(f"   Display Quality: {xpra_quality}% (compression: {xpra_compress})")
    _logger.info(f"   DPI Setting: {xpra_dpi}")
    _logger.info("   Clipboard: Enabled (bidirectional, all content types)")
    _logger.info(
        "   Session Isolation: Complete (unified directory structure per session)"
    )

    # IMPORTANT: Use only TCP binding with HTML5 client - NO WebSockets for SlurmSpawner compatibility

    # Dynamically resolve Xvfb path for portability
    xvfb_path = which("Xvfb")
    if not xvfb_path:
        _logger.error("❌ Xvfb executable not found. Please install Xvfb.")
        raise RuntimeError("Xvfb executable not found. Please install Xvfb.")

    # Let Xpra automatically manage display numbers for session isolation

    xpra_cmd = [
        xpra,
        "start",
        f"--bind-tcp=0.0.0.0:{port}",  # Use the provided port
        "--bind=none",  # Disable Unix socket binding to force TCP only
        "--html=on",  # Enable HTML5 client
        "--daemon=no",  # Run in foreground for proper process management
        "--exit-with-children=yes",  # Exit when Firefox closes
        "--start-via-proxy=no",  # Disable proxy startup to avoid session manager issues
        "--start=",  # Explicitly disable default Xsession startup
        f"--start-child={firefox_wrapper}",  # Use our custom wrapper script
        # Xvfb configuration - let Xpra automatically manage display numbers and screen allocation
        f"--xvfb={xvfb_path} +extension Composite -screen 0 1280x800x24+32 -nolisten tcp -noreset +extension GLX",
        "--mdns=no",  # Disable mDNS
        "--pulseaudio=no",  # Disable audio for simplicity
        "--notifications=no",  # Disable notifications
        "--clipboard=yes",  # Enable clipboard sharing
        "--clipboard-direction=both",  # Allow bidirectional clipboard
        "--sharing=no",  # Disable screen sharing
        "--speaker=off",  # Disable speaker
        "--microphone=off",  # Disable microphone
        "--webcam=no",  # Disable webcam
        "--desktop-scaling=auto",  # Auto-scale to browser window
        "--resize-display=yes",  # Allow display resizing
        "--cursors=yes",  # Forward custom cursors
        "--bell=no",  # Disable bell forwarding
        "--system-tray=no",  # Disable system tray forwarding
        "--xsettings=yes",  # Enable xsettings sync
        "--readonly=no",  # Allow input (default but explicit)
        "--window-close=auto",  # Handle window close events properly
        f"--dpi={xpra_dpi}",  # Configurable DPI
        f"--compressors={xpra_compress}",  # Use modern compression syntax for v5.x
        f"--quality={xpra_quality}",  # Configurable quality
        "--encoding=auto",  # Auto-select best encoding
        "--min-quality=30",  # Minimum quality threshold
        "--min-speed=30",  # Minimum speed threshold
        "--auto-refresh-delay=0.15",  # Default refresh delay
        # X session configuration
        "--fake-xinerama=auto",  # Enable fake xinerama support
        "--use-display=no",  # Don't use existing display
        f"--session-name=Firefox-Session-{port}",  # Session name for identification
        # Environment variables - use session-specific directories for complete isolation
        "--env=PATH=/usr/local/bin:/usr/bin:/bin",  # Ensure PATH includes standard directories
        # NOTE: Don't set DISPLAY manually - let Xpra manage it automatically
        f"--env=SESSION_DIR={session_dir}",  # Pass session directory to firefox-xstartup
        f"--env=XDG_RUNTIME_DIR={runtime_dir}",  # Session-specific runtime directory
        f"--env=XAUTHORITY={runtime_dir}/.Xauth",  # Session-specific X authority file
        "--env=XPRA_CLIPBOARD_WANT_TARGETS=1",  # Enable clipboard target detection
        "--env=XPRA_CLIPBOARD_GREEDY=1",  # Enable greedy clipboard handling
        # Security and cleanup
        "--dbus-launch=",  # Disable D-Bus launch (empty command)
        "--dbus-proxy=no",  # Disable D-Bus proxy
        "--remote-logging=no",  # Disable remote logging for security
        "--bandwidth-detection=no",  # Disable auto bandwidth detection
        "--pings=yes",  # Enable keepalive pings (default 5s)
    ]

    _logger.info("📋 Final Xpra Command Summary:")
    _logger.info(f"   Executable: {xpra_cmd[0]}")
    _logger.info(f"   Action: {xpra_cmd[1]}")
    _logger.info(f"   Port Binding: --bind-tcp=0.0.0.0:{port}")
    _logger.info(f"   Firefox Wrapper: --start-child={firefox_wrapper}")
    _logger.info(f"   Session Directory: {session_dir} (unified structure)")
    _logger.info(f"   Socket Directory: {socket_dir}")
    _logger.info(f"   Runtime Directory: {runtime_dir}")
    _logger.info(f"   Profile Directory: {profile_dir}")
    _logger.info(f"   Temp Directory: {temp_dir}")
    _logger.info(
        f"   Display Settings: DPI={xpra_dpi}, Quality={xpra_quality}%, Compression={xpra_compress}"
    )
    _logger.info(f"   Total Arguments: {len(xpra_cmd)}")

    # Log the complete command for debugging (only in debug mode due to length)
    if _logger.isEnabledFor(10):  # DEBUG level
        xpra_cmd_str = " ".join(shlex.quote(str(arg)) for arg in xpra_cmd)
        _logger.debug("🚀 Complete Xpra Command:")
        _logger.debug(xpra_cmd_str)
    return xpra_cmd


def _check_dependencies():
    """
    Check for required dependencies and return missing ones.
    
    Returns:
        dict: A dictionary with 'missing' (list of missing deps) and 'all_present' (bool)
    """
    missing_deps = []
    
    # Check for Xpra
    if not which("xpra"):
        missing_deps.append({
            "name": "Xpra",
            "description": "Remote display server required for launching Firefox in isolated sessions",
            "install_commands": [
                "# Ubuntu/Debian:",
                "sudo apt update && sudo apt install -y xpra",
                "",
                "# RHEL/CentOS/Fedora:",
                "sudo yum install -y xpra",
                "# or: sudo dnf install -y xpra",
                "",
                "# Conda:",
                "conda install -c conda-forge xpra"
            ]
        })
    
    # Check for Firefox
    if not which("firefox"):
        missing_deps.append({
            "name": "Firefox",
            "description": "Web browser application",
            "install_commands": [
                "# Ubuntu/Debian:",
                "sudo apt update && sudo apt install -y firefox",
                "",
                "# RHEL/CentOS/Fedora:",
                "sudo yum install -y firefox",
                "# or: sudo dnf install -y firefox",
                "",
                "# Manual download:",
                "# Visit https://www.mozilla.org/firefox/"
            ]
        })
    
    # Check for Xvfb (virtual display)
    if not which("Xvfb"):
        missing_deps.append({
            "name": "Xvfb",
            "description": "Virtual framebuffer for headless display",
            "install_commands": [
                "# Ubuntu/Debian:",
                "sudo apt update && sudo apt install -y xvfb",
                "",
                "# RHEL/CentOS/Fedora:",
                "sudo yum install -y xorg-x11-server-Xvfb",
                "# or: sudo dnf install -y xorg-x11-server-Xvfb"
            ]
        })
    
    return {
        "missing": missing_deps,
        "all_present": len(missing_deps) == 0
    }


def _render_dependency_error_html(missing_deps):
    """
    Render HTML error page for missing dependencies using simple string replacement.
    
    Args:
        missing_deps (list): List of missing dependency dictionaries
        
    Returns:
        str: Rendered HTML content
    """
    templates_dir = Path(__file__).parent / "templates"
    template_path = templates_dir / "dependency_error.html"
    
    try:
        # Read the template file
        with open(template_path, 'r') as f:
            html_content = f.read()
        
        # Generate HTML for missing dependencies
        deps_html = ""
        for dep in missing_deps:
            # Format install commands with proper styling
            commands_html = ""
            for cmd in dep["install_commands"]:
                css_class = ' class="comment"' if cmd.startswith('#') else ''
                commands_html += f'<code{css_class}>{cmd}</code>\n'
            
            # Create the dependency item HTML
            deps_html += f"""
            <div class="dep-item">
                <div class="dep-name">{dep['name']}</div>
                <div class="dep-description">{dep['description']}</div>
                <div class="install-commands">
                    {commands_html}
                </div>
            </div>
            """
        
        # Replace the placeholder with our generated HTML
        html_content = html_content.replace("{{DEPENDENCIES_HTML}}", deps_html)
        return html_content
            
    except Exception as e:
        _logger.error(f"Error rendering dependency error template: {e}")
        # Fallback to basic HTML
        deps_list = "\n".join([f"<li><strong>{dep['name']}</strong>: {dep['description']}</li>" 
                              for dep in missing_deps])
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Firefox Launcher - Missing Dependencies</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; text-align: center; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .error {{ color: #e74c3c; }}
                ul {{ text-align: left; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="error">🔧 Firefox Launcher Unavailable</h1>
                <p>The following system dependencies are missing:</p>
                <ul>{deps_list}</ul>
                <p>Please install the missing dependencies and restart JupyterLab.</p>
                <button onclick="window.location.reload()">🔄 Check Again</button>
            </div>
        </body>
        </html>
        """


class FirefoxLauncherHandler(JupyterHandler):
    """Handler for Firefox launcher requests."""

    # Shared lock for session management
    _xpra_startup_lock = None

    # Track multiple active sessions instead of just one
    _active_sessions: Dict[
        Any, Any
    ] = {}  # Dictionary to track {port: process} for multiple sessions

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize the lock if it doesn't exist
        if FirefoxLauncherHandler._xpra_startup_lock is None:
            FirefoxLauncherHandler._xpra_startup_lock = asyncio.Lock()

        # Initialize active sessions tracking if it doesn't exist
        if not hasattr(FirefoxLauncherHandler, "_active_sessions"):
            FirefoxLauncherHandler._active_sessions = {}

    @web.authenticated
    async def get(self):
        """Check dependencies first, then handle session status or redirect to proxy."""
        self.log.info("GET request received for Firefox launcher")
        
        # Always check dependencies first
        dep_check = _check_dependencies()
        
        if not dep_check["all_present"]:
            # Dependencies are missing, render error page
            self.log.warning(f"Missing dependencies: {[dep['name'] for dep in dep_check['missing']]}")
            
            try:
                html_content = _render_dependency_error_html(dep_check["missing"])
                self.set_header("Content-Type", "text/html")
                self.set_status(503)  # Service Unavailable
                self.write(html_content)
                return
            except Exception as e:
                self.log.error(f"Error rendering dependency error page: {e}")
                # Fallback to JSON response
                self.set_status(503)
                self.write({
                    "status": "error",
                    "message": "Firefox launcher dependencies missing",
                    "missing_dependencies": dep_check["missing"]
                })
                return
        
        # Dependencies are present, continue with normal logic
        try:
            # If there are query parameters, handle as status check
            if self.request.arguments:
                # Check if we have any active sessions
                active_sessions = len(FirefoxLauncherHandler._active_sessions)
                running = active_sessions > 0

                self.set_status(200)
                self.write(
                    {
                        "status": "running" if running else "stopped",
                        "message": f"Firefox is {'running' if running else 'not running'}",
                        "active_sessions": active_sessions,
                        "dependencies": "all present"
                    }
                )
                return

            # Otherwise, redirect to first available proxy (legacy proxy handler behavior)
            if not FirefoxLauncherHandler._active_sessions:
                self.set_status(503)
                self.write(
                    {
                        "error": "No Firefox sessions are currently running",
                        "status": "no_sessions",
                    }
                )
                return

            # Get the first available active port (simple approach)
            port = next(iter(FirefoxLauncherHandler._active_sessions.keys()))

            # Redirect to the Xpra HTML5 interface using the server proxy path
            proxy_path = f"/proxy/{port}/"
            self.log.info(
                f"GET request: Redirecting to Xpra HTML5 interface at {proxy_path}"
            )
            self.redirect(proxy_path)

        except Exception as e:
            self.log.error(f"Error in GET handler: {type(e).__name__}: {str(e)}")

            # Log traceback only in debug mode
            if self.log.isEnabledFor(10):  # DEBUG level
                self.log.debug(f"GET handler traceback: {traceback.format_exc()}")

            self.set_status(500)
            self.write({"status": "error", "message": str(e)})

    @web.authenticated
    async def post(self):
        """Launch Firefox via server proxy."""
        self.log.info("POST request received to launch Firefox via server proxy")
        try:
            # Use the shared lock to prevent multiple simultaneous launches
            async with FirefoxLauncherHandler._xpra_startup_lock:
                # Always start a new Firefox session with a unique profile
                self.log.info(
                    "🚀 Starting new Firefox session (existing sessions will continue running)"
                )
                active_count = len(FirefoxLauncherHandler._active_sessions)
                self.log.info(f"📊 Currently active sessions: {active_count}")
                success, port, process_id = await self._start_server_proxy()

                if success and port and process_id:
                    # Store this session in our active sessions
                    FirefoxLauncherHandler._active_sessions[port] = {
                        "process_id": process_id,
                        "port": port,
                    }

                    self.log.info(
                        f"Firefox launched successfully on port {port} with process ID {process_id}"
                    )
                    self.set_status(200)
                    self.write(
                        {
                            "status": "success",
                            "message": "Firefox launched successfully",
                            "port": port,
                            "process_id": process_id,
                            "proxy_path": f"/proxy/{port}/",
                        }
                    )
                else:
                    error_msg = "Failed to launch Firefox via server proxy"
                    if not success:
                        error_msg += " - Xpra startup failed"
                    elif not port:
                        error_msg += " - No port allocated"
                    elif not process_id:
                        error_msg += " - No process ID returned"

                    self.log.error(error_msg)
                    self.set_status(500)
                    self.write(
                        {
                            "status": "error",
                            "message": error_msg,
                            "details": {
                                "success": success,
                                "port": port,
                                "process_id": process_id,
                            },
                        }
                    )

        except Exception as e:
            self.log.error(f"Error launching Firefox: {type(e).__name__}: {str(e)}")

            # Log traceback only in debug mode
            if self.log.isEnabledFor(10):  # DEBUG level
                self.log.debug(f"POST handler traceback: {traceback.format_exc()}")

            # Check if this is a dependency issue
            if isinstance(e, RuntimeError) and ("executable not found" in str(e)):
                # This is likely a missing dependency issue
                dep_check = _check_dependencies()
                if not dep_check["all_present"]:
                    # Render HTML error page for missing dependencies
                    try:
                        html_content = _render_dependency_error_html(dep_check["missing"])
                        self.set_header("Content-Type", "text/html")
                        self.set_status(503)  # Service Unavailable
                        self.write(html_content)
                        return
                    except Exception as render_error:
                        self.log.error(f"Error rendering dependency error page: {render_error}")
                        # Fall through to regular JSON error response

            # Regular JSON error response
            self.set_status(500)
            self.write(
                {
                    "status": "error",
                    "message": f"Exception during Firefox launch: {str(e)}",
                    "error_type": type(e).__name__,
                }
            )

    async def _start_server_proxy(self):
        """Start Firefox/Xpra process with random port for server proxy routing."""
        self.log.info("=== 🚀 STARTING XPRA SERVER PROXY PROCESS ===")

        # Log system information for debugging
        self.log.info("🖥️ System Information:")
        self.log.info(f"   Current working directory: {os.getcwd()}")
        self.log.info(f"   User home directory: {Path.home()}")
        self.log.info(f"   Process PID: {os.getpid()}")
        self.log.info(f"   Python executable: {sys.executable}")

        # Log current active sessions
        active_count = len(FirefoxLauncherHandler._active_sessions)
        self.log.info(f"📊 Active Sessions: {active_count}")
        if active_count > 0:
            for (
                session_port,
                session_info,
            ) in FirefoxLauncherHandler._active_sessions.items():
                self.log.debug(
                    f"   Port {session_port}: PID {session_info['process_id']}"
                )

        try:
            # Find a free port for Xpra
            self.log.debug("Searching for free port for Xpra...")
            port = _find_free_port()
            if not port:
                self.log.error("CRITICAL: Could not find a free port for Xpra")
                return False, None, None
            self.log.info(f"✓ Allocated port {port} for Xpra server")

            # NOTE: Not updating global _xpra_port to support multi-session
            xpra_cmd = _create_xpra_command(port)  # Create the Xpra command

            process = subprocess.Popen(
                xpra_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                # Use the current environment variables, but ensure we have the right PATH
                env={
                    **os.environ,
                    "PATH": os.environ.get("PATH", ""),
                    "XPRA_CRASH_DEBUG": "1",
                },
                # Use setsid for process group management if available
                preexec_fn=os.setsid if hasattr(os, "setsid") else None,
            )

            self.log.info("✅ Xpra subprocess created successfully!")
            self.log.info(f"   Process ID: {process.pid}")
            self.log.info(f"   Port: {port}")
            self.log.info(f"   Command: {xpra_cmd[0]} {xpra_cmd[1]}")
            self.log.info(f"   Proxy URL will be: /proxy/{port}/")
            self.log.info("   Process will run in foreground (daemon mode disabled)")

            # Wait and monitor process startup
            self.log.info("⏱️ Monitoring Xpra process startup...")
            startup_checks = [0.1, 0.2, 0.2]  # Check at 0.1s, 0.3s, 0.5s

            for i, wait_time in enumerate(startup_checks):
                await asyncio.sleep(
                    wait_time
                )  # Use async sleep instead of blocking sleep

                try:
                    poll_result = process.poll()
                    if poll_result is None:
                        self.log.debug(
                            f"✓ Startup check {i+1}/{len(startup_checks)}: Process running"
                        )
                    else:
                        self.log.error(
                            f"❌ Startup check {i+1}/{len(startup_checks)}: Process exited with code {poll_result}"
                        )
                        break
                except Exception as poll_error:
                    self.log.error(f"❌ Error during startup check {i+1}: {poll_error}")
                    break

            # Final process status check
            try:
                final_poll = process.poll()
            except Exception as final_poll_error:
                self.log.error(
                    f"❌ Error checking final process status: {final_poll_error}"
                )
                return False, None, None

            if final_poll is None:
                self.log.info("🎉 Xpra process startup completed successfully!")
                self.log.info(f"   Final process status: Running (PID: {process.pid})")
                self.log.info(f"   Port binding: {port}")
                self.log.info(f"   Session will be available at: /proxy/{port}/")
                # Store this session in the active sessions dictionary
                FirefoxLauncherHandler._active_sessions[port] = {
                    "process_id": process.pid,
                    "port": port,
                }
                self.log.info(
                    "✅ Session will be tracked independently (multi-session support)"
                )

                # Try to verify port is bound (non-blocking check)
                try:
                    test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_sock.settimeout(0.1)
                    result = test_sock.connect_ex(("localhost", port))
                    test_sock.close()

                    if result == 0:
                        self.log.info(f"🌐 Port {port} is accepting connections")
                    else:
                        self.log.debug(
                            f"🔍 Port {port} not yet accepting connections (expected during startup)"
                        )
                except Exception as port_check_error:
                    self.log.debug(
                        f"🔍 Port check failed (expected during startup): {port_check_error}"
                    )

                return True, port, process.pid
            else:
                # Process exited immediately - comprehensive error logging
                self.log.error("❌ Xpra process startup FAILED!")
                self.log.error(f"   Process exited with return code: {final_poll}")
                self.log.error(f"   Process ID was: {process.pid}")
                self.log.error(f"   Port attempted: {port}")
                self.log.error(f"   Command executed: {' '.join(xpra_cmd)}")
                self.log.error("   Please check the Xpra logs for more details.")
                # Capture and log output
                try:
                    stdout, stderr = process.communicate(timeout=5)
                    if stdout:
                        stdout_str = stdout.decode("utf-8", errors="ignore").strip()
                        self.log.error(f"📤 STDOUT ({len(stdout_str)} chars):")
                        for line in stdout_str.split("\n"):
                            if line.strip():
                                self.log.error(f"     {line}")

                    if stderr:
                        stderr_str = stderr.decode("utf-8", errors="ignore").strip()
                        self.log.error(f"📤 STDERR ({len(stderr_str)} chars):")
                        for line in stderr_str.split("\n"):
                            if line.strip():
                                self.log.error(f"     {line}")

                    if not stdout and not stderr:
                        self.log.error("📤 No output captured from failed process")

                except subprocess.TimeoutExpired:
                    self.log.error("⏰ Timeout waiting for process output")
                    process.kill()
                except Exception as output_error:
                    self.log.error(f"❌ Error capturing process output: {output_error}")

                return False, None, None

        except Exception as e:
            self.log.error(
                f"💥 CRITICAL ERROR in _start_server_proxy: {type(e).__name__}: {str(e)}"
            )

            # Log traceback only in debug mode
            if self.log.isEnabledFor(10):  # DEBUG level
                self.log.debug("Full traceback for debugging:")
                for line in traceback.format_exc().splitlines():
                    self.log.debug(f"  {line}")

            # Clean up any partial state
            self.log.error("❌ Xpra server proxy startup failed")
            return False, None, None

    def _cleanup_inactive_sessions(self):
        """Clean up sessions that are no longer running."""
        if not FirefoxLauncherHandler._active_sessions:
            return

        self.log.debug("🧹 Checking for inactive sessions to cleanup")
        sessions_to_remove = []

        for port, session_info in FirefoxLauncherHandler._active_sessions.items():
            process_id = session_info.get("process_id")
            if not process_id:
                sessions_to_remove.append(port)
                continue

            try:
                # Check if process still exists
                process = psutil.Process(process_id)
                if not process.is_running():
                    self.log.info(
                        f"🗑️ Found inactive session on port {port} (process {process_id} not running)"
                    )
                    sessions_to_remove.append(port)
                else:
                    # Double-check by verifying it's actually an Xpra process
                    proc_name = process.name().lower()
                    if "xpra" not in proc_name:
                        self.log.warning(
                            f"🗑️ Process {process_id} on port {port} is not Xpra ({proc_name})"
                        )
                        sessions_to_remove.append(port)

            except psutil.NoSuchProcess:
                self.log.info(
                    f"🗑️ Found inactive session on port {port} (process {process_id} no longer exists)"
                )
                sessions_to_remove.append(port)
            except Exception as check_error:
                self.log.warning(
                    f"⚠️ Error checking session on port {port}: {check_error}"
                )
                # Don't remove on error, might be temporary

        # Remove inactive sessions
        for port in sessions_to_remove:
            try:
                del FirefoxLauncherHandler._active_sessions[port]
                self.log.info(
                    f"✅ Cleaned up inactive session tracking for port {port}"
                )
            except KeyError:
                pass  # Already removed

        if sessions_to_remove:
            self.log.info(f"🧹 Cleaned up {len(sessions_to_remove)} inactive sessions")

    @web.authenticated
    async def delete(self):
        """Stop Firefox and Xpra processes."""
        try:
            async with FirefoxLauncherHandler._xpra_startup_lock:
                stopped = self._stop_firefox()

                if stopped:
                    self.set_status(200)
                    self.write(
                        {"status": "success", "message": "Firefox stopped successfully"}
                    )
                else:
                    self.set_status(200)
                    self.write(
                        {"status": "not_running", "message": "Firefox was not running"}
                    )

        except Exception as e:
            self.log.error(f"Error stopping Firefox: {type(e).__name__}: {str(e)}")

            # Log traceback only in debug mode
            if self.log.isEnabledFor(10):  # DEBUG level
                self.log.debug(f"DELETE handler traceback: {traceback.format_exc()}")

            self.set_status(500)
            self.write({"status": "error", "message": str(e)})

    @web.authenticated
    async def head(self):
        """Handle HEAD requests to check if any Firefox sessions are available."""
        self.log.debug("HEAD request received to check session availability")
        try:
            # Check if we have any active sessions
            if not FirefoxLauncherHandler._active_sessions:
                self.log.debug("HEAD request: No active sessions, returning 503")
                self.set_status(503)  # Service Unavailable
                self.set_header("Content-Length", "0")
                return

            # Return 200 if we have active sessions
            self.log.debug(
                f"HEAD request: Found {len(FirefoxLauncherHandler._active_sessions)} active sessions, returning 200"
            )
            self.set_status(200)
            self.set_header("Content-Length", "0")

        except Exception as e:
            self.log.error(
                f"HEAD request failed with unexpected error: {type(e).__name__}: {str(e)}"
            )

            # Log traceback only in debug mode
            if self.log.isEnabledFor(10):  # DEBUG level
                self.log.debug(f"HEAD request traceback: {traceback.format_exc()}")

            self.set_status(503)  # Service Unavailable
            self.set_header("Content-Length", "0")

    def _stop_firefox(self) -> bool:
        """Stop only the managed Firefox/Xpra sessions, not all processes on the system."""
        stopped = False

        self.log.info("🛑 Stopping managed Firefox/Xpra sessions...")

        # Only stop processes that we're actually managing
        sessions_to_stop = list(FirefoxLauncherHandler._active_sessions.items())

        for port, session_info in sessions_to_stop:
            process_id = session_info.get("process_id")
            if not process_id:
                continue

            try:
                process = psutil.Process(process_id)
                process_name = process.name()

                self.log.info(
                    f"🔥 Terminating managed session: PID {process_id} ({process_name}) on port {port}"
                )

                # Terminate the process and its children
                children = process.children(recursive=True)
                for child in children:
                    try:
                        child.terminate()
                        self.log.debug(f"   Terminated child process: {child.pid}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                # Terminate the main process
                process.terminate()

                # Wait for graceful termination
                try:
                    process.wait(timeout=3)
                    self.log.info(
                        f"✅ Successfully terminated managed session PID {process_id}"
                    )
                except psutil.TimeoutExpired:
                    # Force kill if needed
                    self.log.warning(
                        f"⏰ Force killing unresponsive process {process_id}"
                    )
                    process.kill()

                stopped = True

                # Remove from active sessions
                del FirefoxLauncherHandler._active_sessions[port]

                # Note: No longer using global session_registry to avoid cross-session killing
                # session_registry.unregister_session(port)  # DISABLED

                # Clean up Firefox profile
                _cleanup_firefox_profile(port)

            except psutil.NoSuchProcess:
                self.log.info(f"⚠️ Process {process_id} already terminated")
                # Remove from tracking anyway
                del FirefoxLauncherHandler._active_sessions[port]
                stopped = True

            except Exception as stop_error:
                self.log.error(f"❌ Error stopping process {process_id}: {stop_error}")

        # Session tracking provides all the state we need
        if stopped:
            remaining_sessions = len(FirefoxLauncherHandler._active_sessions)
            if remaining_sessions == 0:
                self.log.info("🧹 All sessions have been stopped")
            else:
                self.log.info(f"📊 {remaining_sessions} active sessions remain")

        return stopped


class FirefoxCleanupHandler(JupyterHandler):
    """Handler for cleaning up Firefox processes when tabs are closed."""

    def check_xsrf_cookie(self):
        """Override XSRF check for cleanup requests since sendBeacon can't send custom headers."""
        # For cleanup requests, we'll allow them without XSRF tokens since:
        # 1. They only terminate processes (no sensitive data exposure)
        # 2. sendBeacon can't send custom headers with XSRF tokens
        # 3. The worst case is terminating a process that's already supposed to be cleaned up
        pass

    async def post(self):
        """Clean up Xpra process by process ID."""
        try:
            # Handle different content types (JSON or plain text from sendBeacon)
            try:
                data = self.get_json()
            except Exception:
                # Fallback for sendBeacon or other non-JSON requests
                body = self.request.body
                if isinstance(body, bytes):
                    body = body.decode("utf-8")

                # Try to parse as JSON
                try:
                    data = json.loads(body)
                except json.JSONDecodeError:
                    self.log.error(f"❌ Could not parse request body as JSON: {body}")
                    self.set_status(400)
                    self.write(
                        {"status": "error", "message": "Invalid JSON in request body"}
                    )
                    return

            process_id = data.get("process_id")
            port = data.get("port")

            self.log.info("🧹 Cleanup request received")
            self.log.info(f"   Process ID: {process_id}")
            self.log.info(f"   Port: {port}")
            self.log.info(f"   Request method: {self.request.method}")
            self.log.info(
                f"   Content-Type: {self.request.headers.get('Content-Type', 'Not set')}"
            )

            if not process_id:
                self.log.error("❌ No process_id provided in cleanup request")
                self.set_status(400)
                self.write({"status": "error", "message": "No process_id provided"})
                return

            # Handle special "all" cleanup - ONLY affects our managed sessions by default
            if process_id == "all":
                self.log.info(
                    "🧹 CLEANUP: Terminating managed Firefox launcher sessions only"
                )
                self.log.info(
                    "   (Other Firefox/Xpra processes on the system will NOT be affected)"
                )
                killed_processes = []

                # Only clean up our explicitly managed sessions
                sessions_to_clean = list(
                    FirefoxLauncherHandler._active_sessions.items()
                )
                self.log.info(
                    f"   Found {len(sessions_to_clean)} managed sessions to clean up"
                )

                for session_port, session_info in sessions_to_clean:
                    session_pid = session_info.get("process_id")
                    if session_pid:
                        try:
                            process = psutil.Process(session_pid)
                            process_name = process.name()

                            self.log.info(
                                f"🔥 Terminating managed session: PID {session_pid} ({process_name}) on port {session_port}"
                            )

                            # Only kill direct child processes of this specific managed session
                            children = process.children(recursive=True)
                            for child in children:
                                try:
                                    child_name = child.name().lower()
                                    # Only terminate processes that are clearly related to Firefox/Xpra
                                    if any(
                                        name in child_name
                                        for name in ["firefox", "xpra", "xvfb"]
                                    ):
                                        child.terminate()
                                        killed_processes.append(
                                            f"{child.name()}:{child.pid}"
                                        )
                                    else:
                                        self.log.debug(
                                            f"🤷 Skipping unrelated child process {child.pid}: {child.name()}"
                                        )
                                except (psutil.NoSuchProcess, psutil.AccessDenied):
                                    pass

                            process.terminate()
                            killed_processes.append(f"{process_name}:{session_pid}")

                            # Clean up profile for this specific session
                            _cleanup_firefox_profile(session_port)

                        except psutil.NoSuchProcess:
                            self.log.info(
                                f"⚠️ Managed session PID {session_pid} already terminated"
                            )
                        except Exception as session_error:
                            self.log.error(
                                f"❌ Error terminating managed session {session_pid}: {session_error}"
                            )

                # Nuclear cleanup is OPTIONAL and requires explicit confirmation
                # This is dangerous in multi-session environments!
                nuclear_cleanup = (
                    self.get_argument("nuclear", "false").lower() == "true"
                    and self.get_argument("confirm_nuclear", "false").lower() == "true"
                )

                if (
                    self.get_argument("nuclear", "false").lower() == "true"
                    and not nuclear_cleanup
                ):
                    self.log.warning("💥 Nuclear cleanup requested but not confirmed.")
                    self.log.warning(
                        "   Nuclear cleanup will kill ALL Firefox/Xpra processes system-wide!"
                    )
                    self.log.warning(
                        "   This may interfere with other users or applications!"
                    )
                    self.log.warning(
                        "   Use ?nuclear=true&confirm_nuclear=true to proceed."
                    )

                if nuclear_cleanup:
                    self.log.warning(
                        "💥 NUCLEAR CLEANUP: Killing ALL Xpra and Firefox processes on system"
                    )
                    self.log.warning(
                        "   ⚠️  WARNING: This may affect processes outside this launcher!"
                    )

                    # Kill ALL Xpra and Firefox processes (not just managed ones)
                    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                        try:
                            proc_name = proc.info["name"].lower()
                            if "xpra" in proc_name or "firefox" in proc_name:
                                # Skip if this is one of our managed processes (already handled)
                                if any(
                                    session_info.get("process_id") == proc.info["pid"]
                                    for session_info in FirefoxLauncherHandler._active_sessions.values()
                                ):
                                    continue

                                self.log.warning(
                                    f"💀 Nuclear cleanup: Killing {proc_name} process {proc.info['pid']}"
                                )
                                proc.terminate()
                                killed_processes.append(
                                    f"NUCLEAR-{proc_name}:{proc.info['pid']}"
                                )
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                else:
                    self.log.info(
                        "🔒 Multi-session safe: Nuclear cleanup not requested, other processes protected"
                    )

                # Clean up session directories only if requested and only for terminated sessions
                cleanup_directories = (
                    self.get_argument("cleanup_dirs", "false").lower() == "true"
                )

                if cleanup_directories:
                    self.log.info(
                        "🧹 Directory cleanup requested - cleaning up directories for terminated sessions only"
                    )
                    try:
                        home_dir = Path.home()
                        sessions_dir = home_dir / ".firefox-launcher" / "sessions"

                        if sessions_dir.exists():
                            # Only clean up directories for sessions we just terminated
                            for session_port, session_info in sessions_to_clean:
                                session_dir = sessions_dir / f"session-{session_port}"
                                if session_dir.exists() and session_dir.is_dir():
                                    try:
                                        self.log.info(
                                            f"🗑️ Removing session directory: {session_dir}"
                                        )
                                        shutil.rmtree(session_dir)
                                        self.log.info(
                                            f"✅ Successfully removed session directory for port {session_port}"
                                        )
                                    except Exception as dir_error:
                                        self.log.warning(
                                            f"⚠️ Failed to remove session directory {session_dir}: {dir_error}"
                                        )
                        else:
                            self.log.debug(
                                "📁 Sessions directory does not exist, nothing to clean up"
                            )

                    except Exception as cleanup_error:
                        self.log.error(
                            f"❌ Error during directory cleanup: {cleanup_error}"
                        )
                else:
                    self.log.debug(
                        "📁 Directory cleanup not requested (use ?cleanup_dirs=true to enable)"
                    )

                # Clear only the sessions we terminated from active tracking
                for session_port, _ in sessions_to_clean:
                    if session_port in FirefoxLauncherHandler._active_sessions:
                        del FirefoxLauncherHandler._active_sessions[session_port]
                    # Note: No longer using global session_registry to avoid cross-session killing
                    # session_registry.unregister_session(session_port)  # DISABLED

                remaining_sessions = len(FirefoxLauncherHandler._active_sessions)
                self.log.info(
                    f"🗑️ Cleared {len(sessions_to_clean)} terminated sessions from tracking"
                )
                self.log.info(
                    f"🔒 Multi-session safe: {remaining_sessions} other sessions remain active"
                )

                cleanup_type = "nuclear" if nuclear_cleanup else "managed-only"
                cleanup_features = []
                if nuclear_cleanup:
                    cleanup_features.append("nuclear")
                if cleanup_directories:
                    cleanup_features.append("directories")

                features_text = (
                    f" ({', '.join(cleanup_features)})" if cleanup_features else ""
                )
                message = f"{cleanup_type.title()} cleanup completed{features_text}, affected {len(killed_processes)} processes, {remaining_sessions} sessions remain active"

                self.set_status(200)
                self.write(
                    {
                        "status": "success",
                        "message": message,
                        "processes_affected": killed_processes,
                        "cleanup_type": cleanup_type,
                    }
                )
                return

            # Try to terminate the specific process
            try:
                process = psutil.Process(process_id)
                process_name = process.name()
                self.log.info(f"🔍 Found process {process_id}: {process_name}")

                # Check if it's actually an Xpra process
                cmdline = " ".join(process.cmdline())
                self.log.info(f"🔍 Process command line: {cmdline}")

                # Terminate only the direct child processes of this specific process
                # This ensures we don't interfere with other active sessions
                children = process.children(recursive=True)
                self.log.info(
                    f"🔍 Found {len(children)} child processes under PID {process_id}"
                )

                for child in children:
                    try:
                        child_name = child.name().lower()
                        # Only terminate processes that are clearly related to Firefox/Xpra
                        if any(
                            name in child_name for name in ["firefox", "xpra", "xvfb"]
                        ):
                            self.log.info(
                                f"🔥 Terminating child process {child.pid}: {child.name()}"
                            )
                            child.terminate()
                        else:
                            self.log.debug(
                                f"🤷 Skipping unrelated child process {child.pid}: {child.name()}"
                            )
                    except psutil.NoSuchProcess:
                        self.log.debug(
                            f"⚠️ Child process {child.pid} already terminated"
                        )
                    except Exception as child_error:
                        self.log.warning(
                            f"❌ Error terminating child {child.pid}: {child_error}"
                        )

                # Terminate the main process
                self.log.info(
                    f"🔥 Terminating main process {process_id}: {process_name}"
                )
                process.terminate()

                # Wait for process to terminate
                try:
                    process.wait(timeout=5)
                    self.log.info(f"✅ Successfully terminated process {process_id}")
                except psutil.TimeoutExpired:
                    # Force kill if it doesn't terminate gracefully
                    self.log.warning(
                        f"⏰ Process {process_id} didn't terminate gracefully, force killing..."
                    )
                    process.kill()
                    try:
                        process.wait(timeout=2)
                        self.log.info(f"💀 Force killed process {process_id}")
                    except psutil.TimeoutExpired:
                        self.log.error(
                            f"❌ Failed to kill process {process_id} even with force"
                        )

                # Clean up Firefox profile for this process
                self.log.info(
                    f"🧹 Cleaning up Firefox profile for process {process_id}"
                )
                profile_cleanup_success = _cleanup_firefox_profile(process_id)
                if profile_cleanup_success:
                    self.log.info(
                        f"✅ Successfully cleaned up Firefox profile for process {process_id}"
                    )
                else:
                    self.log.warning(
                        f"⚠️ Failed to clean up Firefox profile for process {process_id}"
                    )

                # Remove from active sessions tracking
                port_to_remove = None
                for (
                    session_port,
                    session_info,
                ) in FirefoxLauncherHandler._active_sessions.items():
                    if session_info["process_id"] == process_id:
                        port_to_remove = session_port
                        break

                if port_to_remove:
                    del FirefoxLauncherHandler._active_sessions[port_to_remove]
                    # Note: No longer using global session_registry to avoid cross-session killing
                    # session_registry.unregister_session(port_to_remove)  # DISABLED
                    self.log.info(
                        f"🗑️ Removed session from active tracking (port {port_to_remove})"
                    )

                self.set_status(200)
                self.write(
                    {
                        "status": "success",
                        "message": f"Process {process_id} terminated successfully",
                    }
                )

            except psutil.NoSuchProcess:
                self.log.info(f"⚠️ Process {process_id} already terminated")

                # Clean up Firefox profile even if process is already dead
                self.log.info(
                    f"🧹 Cleaning up Firefox profile for terminated process {process_id}"
                )
                profile_cleanup_success = _cleanup_firefox_profile(process_id)
                if profile_cleanup_success:
                    self.log.info(
                        f"✅ Successfully cleaned up Firefox profile for process {process_id}"
                    )
                else:
                    self.log.warning(
                        f"⚠️ Failed to clean up Firefox profile for process {process_id}"
                    )

                # Remove from active sessions tracking
                port_to_remove = None
                for (
                    session_port,
                    session_info,
                ) in FirefoxLauncherHandler._active_sessions.items():
                    if session_info["process_id"] == process_id:
                        port_to_remove = session_port
                        break

                if port_to_remove:
                    del FirefoxLauncherHandler._active_sessions[port_to_remove]
                    # Note: No longer using global session_registry to avoid cross-session killing
                    # session_registry.unregister_session(port_to_remove)  # DISABLED
                    self.log.info(
                        f"🗑️ Removed session from active tracking (port {port_to_remove})"
                    )

                # For multi-session support, we DON'T search for stray processes
                # since other sessions might be using similar processes
                self.log.debug(
                    "🔒 Multi-session mode: Skipping stray process cleanup to protect other active sessions"
                )
                killed_processes = []

                self.set_status(200)
                self.write(
                    {
                        "status": "success",
                        "message": f"Process {process_id} was already terminated, cleaned up {len(killed_processes)} stray processes",
                    }
                )

            except psutil.AccessDenied:
                self.log.error(f"❌ Access denied to terminate process {process_id}")
                self.set_status(403)
                self.write(
                    {
                        "status": "error",
                        "message": f"Access denied to terminate process {process_id}",
                    }
                )

        except Exception as e:
            self.log.error(f"💥 Error in cleanup handler: {type(e).__name__}: {str(e)}")

            # Log traceback only in debug mode
            if self.log.isEnabledFor(10):  # DEBUG level
                self.log.debug(f"Cleanup handler traceback: {traceback.format_exc()}")

            self.set_status(500)
            self.write({"status": "error", "message": str(e)})


