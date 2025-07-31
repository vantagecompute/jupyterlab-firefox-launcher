# Copyright (c) 2025 Vantage Compute Corporation.
"""
Session cleanup utilities for Firefox launcher extension.

This module provides utility functions for cleaning up Firefox sessions and profiles.
"""

import logging
import shutil
from pathlib import Path

# Set up logger for cleanup operations
_logger = logging.getLogger(__name__)


def cleanup_firefox_profile(port: int) -> bool:
    """
    Clean up Firefox profile directory and session-specific directories for a given port.

    Args:
        port: The port number of the Xpra process
    Returns:
        True if cleanup was successful or profile didn't exist, False otherwise
    """
    # Import the existing cleanup function
    try:
        from . import firefox_handler

        return firefox_handler._cleanup_firefox_profile(port)
    except ImportError:
        # Fallback implementation
        try:
            home_dir = Path.home()
            session_dir = (
                home_dir / ".firefox-launcher" / "sessions" / f"session-{port}"
            )
            if session_dir.exists():
                _logger.info(f"🧹 Cleaning up session directory: {session_dir}")
                shutil.rmtree(session_dir)
                _logger.info(
                    f"✅ Successfully removed session directory: {session_dir}"
                )
            return True
        except Exception as e:
            _logger.error(f"❌ Error cleaning up profile for port {port}: {e}")
            return False
