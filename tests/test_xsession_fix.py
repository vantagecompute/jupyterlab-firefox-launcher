#!/usr/bin/env python3
"""
Test script to verify the Xsession startup fix.
"""

import subprocess
import tempfile
import shutil
from pathlib import Path


def test_xsession_fix():
    """Test that the Xsession 'true' error is resolved."""

    print("🔍 Testing Xsession Startup Fix")
    print("=" * 35)

    xpra_path = shutil.which("xpra")
    if not xpra_path:
        print("❌ Xpra not found")
        return False

    with tempfile.TemporaryDirectory() as temp_dir:
        socket_dir = Path(temp_dir) / "sockets"
        socket_dir.mkdir(exist_ok=True)

        # Create firefox-xstartup-like test script
        test_script = Path(temp_dir) / "firefox_test.sh"
        test_script.write_text(
            """#!/bin/sh
echo "Firefox test script starting"
echo "DISPLAY: $DISPLAY"
echo "PORT: $PORT"
sleep 1
echo "Firefox test script complete"
exit 0
"""
        )
        test_script.chmod(0o755)

        # Test with the fixed Xpra command (explicit --start= override)
        test_port = 9998
        cmd = [
            xpra_path,
            "start",
            f"--bind-tcp=127.0.0.1:{test_port}",
            "--html=on",
            "--daemon=no",
            "--exit-with-children=yes",
            "--start-via-proxy=no",
            "--start=",  # Explicitly disable default Xsession startup
            f"--start-child={test_script}",
            "--xvfb=/usr/bin/Xvfb +extension Composite -screen 0 800x600x24+32 -nolisten tcp -noreset",
            f"--socket-dirs={socket_dir}",
            "--mdns=no",
            "--pulseaudio=no",
            "--notifications=no",
            "--system-tray=no",
            f"--env=PORT={test_port}",
            "--env=PATH=/usr/local/bin:/usr/bin:/bin",
        ]

        print("🚀 Testing Xpra with explicit --start= override:")
        print(f"   Command includes: --start= --start-child={test_script}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            print(f"📋 Exit code: {result.returncode}")

            if result.stdout:
                print("📄 STDOUT:")
                for line in result.stdout.split("\n"):
                    if line.strip():
                        print(f"   {line}")

            stderr_lines = []
            xsession_errors = []

            if result.stderr:
                print("📄 STDERR Analysis:")
                for line in result.stderr.split("\n"):
                    if line.strip():
                        stderr_lines.append(line)
                        if "xsession" in line.lower() and "true" in line.lower():
                            xsession_errors.append(line)
                        print(f"   {line}")

            # Check if the Xsession error is gone
            if xsession_errors:
                print("\n❌ Still seeing Xsession 'true' errors:")
                for error in xsession_errors:
                    print(f"   {error}")
                print(
                    "\n💡 This suggests Xpra is still running default session startup"
                )
            else:
                print("\n✅ No Xsession 'true' errors detected!")
                print("   The --start= override is working correctly")

            # Check if our test script ran
            if "Firefox test script starting" in result.stdout:
                print("✅ Test script executed successfully")
            else:
                print("❌ Test script may not have executed")

            if result.returncode == 0:
                print("✅ Xpra session completed successfully")
                return len(xsession_errors) == 0
            else:
                print("❌ Xpra session failed")
                return False

        except subprocess.TimeoutExpired:
            print("⏱️ Test timed out")
            return False
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False


if __name__ == "__main__":
    success = test_xsession_fix()
    if success:
        print("\n🎉 Xsession fix appears to be working!")
    else:
        print("\n⚠️ Xsession issue may still be present")
