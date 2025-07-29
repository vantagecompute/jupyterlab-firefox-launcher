#!/usr/bin/env python3
"""
Debug script to capture detailed error output from failed Xpra sessions.
"""

import subprocess
import time
import socket
from pathlib import Path


def start_debug_session(port):
    """Start a single Xpra session and capture detailed output."""
    print(f"🔍 Starting debug session on port {port}")

    # Create session directory
    session_dir = Path.home() / ".firefox-launcher" / "debug-test" / f"session-{port}"
    session_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    socket_dir = session_dir / "sockets"
    runtime_dir = session_dir / "runtime"
    profile_dir = session_dir / "profile"
    temp_dir = session_dir / "temp"

    for subdir in [socket_dir, runtime_dir, profile_dir, temp_dir]:
        subdir.mkdir(exist_ok=True)

    firefox_script = (
        "/home/bdx/allcode/github/vantagecompute/jfl/scripts/firefox-xstartup"
    )

    # Calculate screen number based on port
    screen_number = port % 100
    print(f"   Using screen number: {screen_number}")

    # Xpra command with incremental screen numbers
    cmd = [
        "xpra",
        "start",
        f"--bind-tcp=0.0.0.0:{port}",
        "--bind=none",
        "--html=on",
        "--daemon=no",
        "--exit-with-children=yes",
        "--start=",
        f"--start-child={firefox_script}",
        f"--xvfb=/usr/bin/Xvfb +extension Composite -screen {screen_number} 1280x800x24+32 -nolisten tcp -noreset",
        f"--socket-dir={socket_dir}",
        "--mdns=no",
        "--auth=allow",
        "--tcp-auth=allow",
        "--pulseaudio=no",
        "--notifications=no",
        "--webcam=no",
        # Environment variables
        f"--env=PORT={port}",
        f"--env=XDG_RUNTIME_DIR={runtime_dir}",
        f"--env=TMPDIR={temp_dir}",
        f"--env=FIREFOX_PROFILE_DIR={profile_dir}",
        "--env=MOZ_DBUS_REMOTE=0",
    ]

    print(f"🚀 Command: {' '.join(cmd[:5])}... [truncated]")

    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        print(f"   Process started with PID: {process.pid}")

        # Wait a bit for startup
        time.sleep(3)
        poll_result = process.poll()

        if poll_result is None:
            print("   ✅ Process still running after 3 seconds")
            # Terminate for cleanup
            process.terminate()
            process.wait(timeout=2)
            return True, None, None
        else:
            print(f"   ❌ Process exited with code: {poll_result}")
            # Get output
            stdout, stderr = process.communicate(timeout=5)
            return False, stdout, stderr

    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False, None, str(e)


def find_free_port():
    """Find a free port for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def main():
    print("🔍 Debugging Xpra Session Failures")
    print("=" * 50)

    # Test a few sessions to see what fails
    for i in range(3):
        port = find_free_port()
        print(f"\n🧪 Test {i+1}: Port {port} (screen {port % 100})")

        success, stdout, stderr = start_debug_session(port)

        if not success:
            print("💥 Session failed! Capturing output...")

            if stdout:
                print("\n📤 STDOUT:")
                for line in stdout.strip().split("\n")[-10:]:  # Last 10 lines
                    print(f"   {line}")

            if stderr:
                print("\n📤 STDERR:")
                for line in stderr.strip().split("\n")[-15:]:  # Last 15 lines
                    print(f"   {line}")
        else:
            print("✅ Session succeeded")

        # Small delay between tests
        time.sleep(1)


if __name__ == "__main__":
    main()
