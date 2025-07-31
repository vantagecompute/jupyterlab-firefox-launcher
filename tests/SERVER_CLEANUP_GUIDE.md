# Firefox Session Cleanup on Server Shutdown/Culling

## Overview

When a notebook server is culled (terminated by JupyterHub, SlurmSpawner, or other spawners), it's critical to ensure all Firefox/Xpra sessions are properly cleaned up to prevent:

- **Orphaned processes** consuming system resources
- **Port conflicts** when new sessions start
- **Session directory bloat** filling up disk space
- **Resource leaks** in multi-user environments

## Current Implementation

As of the latest version, the cleanup system has been simplified for reliability and to prevent cross-session interference.

### 1. Local Session Tracking

The `firefox_handler.py` maintains local session tracking without global registries:

```python
# Track sessions locally in the handler
_active_sessions = {}  # port -> session_info

# Register sessions when created
_active_sessions[port] = {
    "process_id": process.pid,
    "port": port,
    "session_dir": session_dir,
    "created_at": time.time()
}

# Clean up when stopped
if port in _active_sessions:
    del _active_sessions[port]
```

### 2. Individual Session Cleanup

Each session handles its own cleanup without global signal handlers:

```python
# Import cleanup utilities
from .session_cleanup import cleanup_firefox_profile

# Clean up individual sessions
def _stop_firefox(self):
    # ... stop processes ...
    cleanup_firefox_profile(port)
```

### 3. Why Global Session Registry Was Removed

The previous global session registry caused problems:

- **Cross-session killing**: Global signal handlers would terminate ALL sessions when any single session stopped
- **Process interference**: Starting a new session could inadvertently kill existing sessions
- **Threading issues**: Global singleton patterns created race conditions in multi-user environments

## Current Session Cleanup Approach

### Per-Session Cleanup

Each Firefox session is responsible for cleaning up its own resources:

1. **Process termination**: Gracefully stop Xpra and Firefox processes
2. **Directory cleanup**: Remove session-specific directories and temporary files
3. **Port cleanup**: Free up the allocated port for reuse
4. **Local tracking**: Update the handler's internal session tracking

### Session Directory Structure

```
~/.firefox-launcher/
├── sessions/
│   ├── session-8001/
│   ├── session-8002/
│   └── ...
└── temp/
    ├── session-8001/
    └── ...
```

### Cleanup Functions

The `session_cleanup.py` module provides utility functions:

```python
def cleanup_firefox_profile(port: int) -> bool:
    """Clean up session directory for a specific port."""
    # Removes session directory and temporary files
    # Returns True if successful
```
3. **All Firefox/Xpra processes terminated** with their child processes
4. **Session directories cleaned up** to free disk space
5. **Tracking cleared** from both registries

### Scenario 2: Force Kill (SIGKILL)

1. **Server killed immediately** without cleanup opportunity
2. **External cleanup script** can use PID file to detect orphaned sessions
3. **Next server start** can clean up stale session directories

### Scenario 3: SlurmSpawner Timeout

1. **SlurmSpawner sends SIGTERM** before timeout
2. **Cleanup handlers execute** as in normal culling
3. **If processes don't terminate**, SIGKILL follows
4. **Session directories marked for cleanup** on next start

## Benefits

### ✅ **Resource Protection**
- No orphaned Xpra/Firefox processes
- No lingering session directories
- Proper port cleanup for reuse

### ✅ **Multi-User Safety**
- Only cleans up managed sessions
- Protects other users' processes
- Thread-safe session tracking

### ✅ **Robustness**
- Multiple cleanup triggers ensure reliability
- Graceful termination with force fallback
- Handles various shutdown scenarios

### ✅ **Observability**
- Comprehensive logging of cleanup operations
- PID file for external monitoring
- Session tracking for debugging

## Server Shutdown Scenarios

### JupyterHub Culling

When JupyterHub terminates a notebook server:

1. **Server process termination**: The main Jupyter server process is terminated
2. **Child process cleanup**: Operating system handles cleanup of child processes
3. **Session directories**: May remain and need periodic cleanup via external scripts
4. **Port availability**: Ports become available for reuse automatically

### Manual Session Management

Users can manually start and stop sessions:

```python
# Start a new Firefox session
handler.start_firefox()

# Stop a specific session
handler.stop_firefox(port=8001)
```

## Cleanup Best Practices

### 1. Regular Directory Cleanup

Set up periodic cleanup of old session directories:

```bash
#!/bin/bash
# cleanup_old_sessions.sh

# Remove session directories older than 7 days
find "$HOME/.firefox-launcher/sessions" -type d -mtime +7 -exec rm -rf {} +

# Remove temporary files older than 1 day  
find "$HOME/.firefox-launcher/temp" -type f -mtime +1 -delete
```

### 2. Process Monitoring

Monitor for orphaned processes:

```bash
# Check for orphaned Xpra processes
ps aux | grep "xpra.*$USER" | grep -v grep

# Check for orphaned Firefox processes
ps aux | grep "firefox.*$USER" | grep -v grep
```

### 3. Port Usage Tracking

Check which ports are in use:

```bash
# Check for listening ports in the Firefox range
netstat -tlnp | grep ":80[0-9][0-9]"
```

## Configuration

No special configuration is needed. Cleanup happens automatically when sessions are stopped properly.

### Environment Variables (Optional)

- `FIREFOX_LAUNCHER_CLEANUP_TIMEOUT`: Cleanup timeout in seconds (default: 3)
- `FIREFOX_LAUNCHER_DEBUG`: Enable debug logging for cleanup operations

## Testing

Test the cleanup system:

```python
# Test session cleanup
from jupyterlab_firefox_launcher.session_cleanup import cleanup_firefox_profile

# Clean up a specific session
result = cleanup_firefox_profile(8001)
print(f"Cleanup successful: {result}")
```

## External Cleanup Script Example

For additional safety in production environments, you can create monitoring scripts:

```bash
#!/bin/bash
# monitor_firefox_sessions.sh

# Clean up any orphaned processes for the current user
cleanup_orphaned() {
    echo "Cleaning up orphaned Firefox/Xpra processes..."
    
    # Find and kill orphaned Xpra processes
    pkill -u $(whoami) -f "xpra.*--bind-tcp"
    
    # Find and kill orphaned Firefox processes in headless mode
    pkill -u $(whoami) -f "firefox.*--headless"
    
    # Clean up old session directories (older than 24 hours)
    find "$HOME/.firefox-launcher/sessions" -type d -mtime +1 -exec rm -rf {} + 2>/dev/null
    
    echo "Cleanup completed"
}

# Check if any sessions are running
if pgrep -u $(whoami) -f "xpra.*--bind-tcp" > /dev/null; then
    echo "Active Firefox sessions detected"
else
    echo "No active sessions found"
    cleanup_orphaned
fi
```

## Summary

The current cleanup system provides:

1. **Isolated session management** - each session handles its own cleanup
2. **No cross-session interference** - starting/stopping one session doesn't affect others
3. **Simple and reliable** - fewer moving parts means fewer potential failure points
4. **Resource efficiency** - no global signal handlers or background threads

### Key Improvements Over Previous Version

- **Removed global session registry** that caused cross-session killing
- **Eliminated global signal handlers** that interfered with process management
- **Simplified architecture** for better maintainability and debugging
- **Improved reliability** in multi-user environments

This approach ensures that Firefox sessions are properly managed without the complexity and reliability issues of the previous global registry system.
