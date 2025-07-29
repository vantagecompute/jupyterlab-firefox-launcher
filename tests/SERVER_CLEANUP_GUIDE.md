# Firefox Session Cleanup on Server Shutdown/Culling

## Overview

When a notebook server is culled (terminated by JupyterHub, SlurmSpawner, or other spawners), it's critical to ensure all Firefox/Xpra sessions are properly cleaned up to prevent:

- **Orphaned processes** consuming system resources
- **Port conflicts** when new sessions start
- **Session directory bloat** filling up disk space
- **Resource leaks** in multi-user environments

## Solution Implementation

We've implemented a comprehensive cleanup system that handles server shutdown through multiple mechanisms:

### 1. Session Registry (`session_cleanup.py`)

A centralized tracking system that maintains a registry of all active Firefox/Xpra sessions:

```python
# Register new sessions when they start
session_registry.register_session(port, process_id, session_dir)

# Unregister when manually stopped
session_registry.unregister_session(port)

# Cleanup all sessions on shutdown
session_registry.cleanup_all_sessions(force=True)
```

### 2. Multiple Cleanup Triggers

The system registers cleanup handlers for various shutdown scenarios:

#### a) **atexit Handlers**
- Triggered on normal Python exit
- Ensures cleanup even if other methods fail

#### b) **Signal Handlers** 
- SIGTERM: Standard termination signal from process managers
- SIGINT: Interrupt signal (Ctrl+C)
- Handles forceful shutdown scenarios

#### c) **Jupyter Server Hooks**
- Integrates with Jupyter server shutdown process
- Triggered when JupyterHub culls the server

#### d) **PID File for External Cleanup**
- Creates `/home/user/.firefox-launcher/jupyter_server.pid`
- Allows external scripts to clean up orphaned sessions

### 3. Integration with Firefox Handler

The `firefox_handler.py` has been modified to:

```python
# Import cleanup system
from .session_cleanup import session_registry

# Register sessions when created
def _start_server_proxy(self):
    # ... create Xpra process ...
    if final_poll is None:
        # Register for cleanup
        session_dir = Path.home() / '.firefox-launcher' / 'sessions' / f'session-{port}'
        session_registry.register_session(port, process.pid, session_dir)
        # ... continue with session setup ...

# Unregister when manually stopped
def _stop_firefox(self):
    # ... stop processes ...
    session_registry.unregister_session(port)
```

## How Cleanup Works During Server Culling

### Scenario 1: Normal JupyterHub Culling

1. **JupyterHub sends SIGTERM** to the notebook server process
2. **Signal handler activates** and calls `cleanup_all_sessions(force=True)`
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

## Configuration

The cleanup system is automatically activated when the first Firefox session is created. No additional configuration is needed.

### Environment Variables (Optional)

- `FIREFOX_LAUNCHER_CLEANUP_TIMEOUT`: Cleanup timeout in seconds (default: 3)
- `FIREFOX_LAUNCHER_FORCE_CLEANUP`: Always use force cleanup (default: False)

## Testing

The system can be tested using the provided notebook:

```bash
# Run the cleanup test notebook
jupyter notebook server_shutdown_cleanup.ipynb
```

## External Cleanup Script Example

For additional safety, you can create an external cleanup script:

```bash
#!/bin/bash
# cleanup_orphaned_firefox.sh

PID_FILE="$HOME/.firefox-launcher/jupyter_server.pid"

if [ -f "$PID_FILE" ]; then
    JUPYTER_PID=$(cat "$PID_FILE")
    if ! kill -0 "$JUPYTER_PID" 2>/dev/null; then
        echo "Jupyter server $JUPYTER_PID not running, cleaning up orphaned sessions..."
        
        # Clean up any remaining Xpra processes for this user
        pkill -u $(whoami) xpra
        
        # Clean up session directories
        rm -rf "$HOME/.firefox-launcher/sessions/"
        
        # Remove stale PID file
        rm -f "$PID_FILE"
        
        echo "Cleanup completed"
    fi
fi
```

## Summary

This cleanup system ensures that when a notebook server is culled:

1. **All Firefox/Xpra sessions are terminated** properly
2. **Session directories are cleaned up** to prevent disk bloat
3. **Resources are freed** for other users
4. **No orphaned processes remain** consuming system resources

The multi-layered approach (signal handlers, atexit, Jupyter hooks, PID files) provides robust protection against resource leaks in various shutdown scenarios.
