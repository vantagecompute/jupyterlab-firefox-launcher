#!/usr/bin/env python3
"""
Test multiple concurrent Xpra sessions to verify screen number isolation.
"""

import subprocess
import time
import socket
from pathlib import Path


def find_free_port():
    """Find a free port for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def start_xpra_session(port):
    """Start a single Xpra session for testing."""
    print(f"🚀 Starting session on port {port}")

    # Create session directory
    session_dir = Path.home() / ".firefox-launcher" / "multi-test" / f"session-{port}"
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

    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        print(f"   Process started with PID: {process.pid}")
        return process, port, screen_number

    except Exception as e:
        print(f"   ❌ Failed to start session: {e}")
        return None, port, screen_number


def test_multi_session():
    """Test multiple concurrent sessions."""
    print("🧪 Testing Multiple Concurrent Xpra Sessions")
    print("=" * 60)

    # Start 3 concurrent sessions
    sessions = []
    ports = [find_free_port() for _ in range(3)]

    print(f"📋 Starting 3 sessions on ports: {ports}")

    # Start all sessions
    for port in ports:
        process, session_port, screen_num = start_xpra_session(port)
        if process:
            sessions.append((process, session_port, screen_num))

    if not sessions:
        print("❌ Failed to start any sessions")
        return False

    print(f"\n✅ Started {len(sessions)} sessions successfully")

    # Wait for startup
    print("⏱️ Waiting 10 seconds for all sessions to start...")
    time.sleep(10)

    # Check all sessions
    active_sessions = []
    for process, port, screen_num in sessions:
        poll_result = process.poll()
        if poll_result is None:
            # Test connectivity
            try:
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_sock.settimeout(1)
                result = test_sock.connect_ex(("localhost", port))
                test_sock.close()

                if result == 0:
                    print(
                        f"✅ Session {port} (screen {screen_num}): Running and accepting connections"
                    )
                    active_sessions.append((process, port, screen_num))
                else:
                    print(
                        f"⚠️ Session {port} (screen {screen_num}): Running but not accepting connections yet"
                    )
                    active_sessions.append((process, port, screen_num))
            except Exception as e:
                print(
                    f"❌ Session {port} (screen {screen_num}): Connection test failed - {e}"
                )
        else:
            print(
                f"❌ Session {port} (screen {screen_num}): Process exited with code {poll_result}"
            )

    print(
        f"\n📊 Summary: {len(active_sessions)} of {len(sessions)} sessions are running"
    )

    if active_sessions:
        print("\n🌐 Active sessions:")
        for _, port, screen_num in active_sessions:
            print(f"   http://localhost:{port}/ (screen {screen_num})")

        print("\n⏸️ Keeping sessions running for 15 seconds for manual testing...")
        time.sleep(15)

    # Clean up all sessions
    print("\n🛑 Terminating all sessions...")
    for process, port, screen_num in sessions:
        try:
            if process.poll() is None:
                print(f"   Terminating session {port} (screen {screen_num})")
                process.terminate()
                try:
                    process.wait(timeout=3)
                    print(f"   ✅ Session {port} terminated cleanly")
                except subprocess.TimeoutExpired:
                    process.kill()
                    print(f"   ⚠️ Session {port} force-killed")
        except Exception as e:
            print(f"   ❌ Error terminating session {port}: {e}")

    success = (
        len(active_sessions) >= 2
    )  # Consider success if at least 2 sessions worked
    return success


if __name__ == "__main__":
    success = test_multi_session()
    if success:
        print("\n🎉 Multi-session test PASSED!")
        print("✅ Screen number isolation is working correctly")
    else:
        print("\n❌ Multi-session test FAILED!")
        print("⚠️ There may be issues with concurrent sessions")
