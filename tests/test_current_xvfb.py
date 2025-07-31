#!/usr/bin/env python3
"""
Test the current Xvfb configuration with multiple concurrent sessions.
"""

import subprocess
import time
import os
from pathlib import Path


def test_current_xvfb_config():
    """Test current Xvfb configuration for conflicts."""

    print("🧪 Testing Current Xvfb Configuration")
    print("=" * 40)

    # Test ports
    test_ports = [47001, 47002]
    processes = []

    for port in test_ports:
        print(f"\n🚀 Starting session on port {port}...")

        # Create session directory
        session_dir = (
            Path.home() / ".firefox-launcher" / "test-xvfb" / f"session-{port}"
        )
        session_dir.mkdir(parents=True, exist_ok=True)

        for subdir in ["sockets", "runtime", "profile", "temp"]:
            (session_dir / subdir).mkdir(exist_ok=True)

        # Set permissions
        (session_dir / "runtime").chmod(0o700)

        firefox_script = (
            "/home/bdx/allcode/github/vantagecompute/jfl/scripts/firefox-xstartup"
        )

        # Use the EXACT current configuration from firefox_handler.py
        cmd = [
            "xpra",
            "start",
            f"--bind-tcp=127.0.0.1:{port}",
            "--bind=none",
            "--html=on",
            "--daemon=no",
            "--exit-with-children=yes",
            "--start-via-proxy=no",
            "--start=",
            f"--start-child={firefox_script}",
            # This is the current Xvfb configuration from firefox_handler.py (fixed format)
            "--xvfb=Xvfb +extension Composite -screen 0 1280x800x24+32 -nolisten tcp -noreset +extension GLX",
            "--use-display=no",
        ]

        # Set environment
        env = os.environ.copy()
        env.update(
            {
                "XDG_RUNTIME_DIR": str(session_dir / "runtime"),
                "TMPDIR": str(session_dir / "temp"),
                "FIREFOX_PROFILE_DIR": str(session_dir / "profile"),
                "PORT": str(port),
            }
        )

        try:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
            )
            processes.append((port, process))

            print(f"   Started process PID: {process.pid}")

            # Wait a bit for startup
            time.sleep(2)

            if process.poll() is None:
                print(f"   ✅ Session {port} running successfully")

                # Check what Xvfb processes were created
                ps_result = subprocess.run(
                    ["ps", "aux"], capture_output=True, text=True
                )
                xvfb_lines = [
                    line
                    for line in ps_result.stdout.split("\n")
                    if f"Xvfb-for-Xpra-S{process.pid}" in line
                ]

                for line in xvfb_lines:
                    print(f"      Xvfb: {line.strip()}")
                    # Check if it includes -displayfd
                    if "-displayfd" in line:
                        print("      ✅ Dynamic display allocation enabled")
                    else:
                        print("      ⚠️ No -displayfd found")

            else:
                stdout, stderr = process.communicate()
                print(f"   ❌ Session {port} failed")
                if stderr:
                    print(f"      Error: {stderr.decode()[:200]}...")

        except Exception as e:
            print(f"   ❌ Exception: {e}")

    # Summary
    running_sessions = [p for port, p in processes if p.poll() is None]
    print("\n📊 Results:")
    print(f"   Sessions started: {len(processes)}")
    print(f"   Sessions running: {len(running_sessions)}")

    if len(running_sessions) == len(test_ports):
        print("   ✅ All sessions running - no Xvfb conflicts!")
    elif len(running_sessions) > 0:
        print("   ⚠️ Some sessions running - partial success")
    else:
        print("   ❌ No sessions running - configuration issue")

    # Cleanup
    print("\n🧹 Cleaning up...")
    for port, process in processes:
        try:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=3)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass

    # Clean up test directories
    test_dir = Path.home() / ".firefox-launcher" / "test-xvfb"
    if test_dir.exists():
        import shutil

        shutil.rmtree(test_dir)
        print("   ✅ Cleaned up test directories")


if __name__ == "__main__":
    test_current_xvfb_config()
