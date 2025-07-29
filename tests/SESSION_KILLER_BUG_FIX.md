# Firefox Session Killer Bug - Debug Analysis & Fix

## 🐛 Problem Description

When starting a new Firefox/Xpra process, older processes were being killed unexpectedly. Users reported that launching a second Firefox session would terminate the first session.

## 🔍 Root Cause Analysis

### The Issue

The problem was in the **global signal handler system** implemented in `session_cleanup.py`:

1. **Global Singleton**: `session_cleanup.py` creates a global singleton `FirefoxSessionRegistry`
2. **Global Signal Handlers**: This singleton registers global SIGTERM and SIGINT signal handlers
3. **Cross-Session Killing**: When ANY process receives a signal (including normal restarts), the signal handlers call `cleanup_all_sessions()`
4. **Mass Termination**: `cleanup_all_sessions()` kills ALL registered sessions across ALL launcher instances

### Code Evidence

```python
# In session_cleanup.py
class FirefoxSessionRegistry:
    _instance = None  # Global singleton
    
    def _register_cleanup_handlers(self):
        # Global signal handlers - THIS IS THE PROBLEM!
        signal.signal(signal.SIGTERM, self._signal_cleanup)
        signal.signal(signal.SIGINT, self._signal_cleanup)
    
    def _signal_cleanup(self, signum, frame):
        # Kills ALL sessions when ANY signal is received
        self.cleanup_all_sessions(force=True)
```

### Verification Tests

Created test scripts that confirmed:
- `session_registry` is a global singleton shared across all instances
- Global signal handlers are registered that point to the singleton
- Any signal to any process triggers cleanup of ALL sessions
- This explains why new sessions kill older ones

## ✅ Solution Implemented

### Changes Made

**File: `firefox_handler.py`**

1. **Disabled Global Registry Import**:
   ```python
   # OLD:
   from .session_cleanup import session_registry
   
   # NEW:
   # Import session cleanup system (but avoid global signal handlers)
   # from .session_cleanup import session_registry  # DISABLED: causes cross-session killing
   ```

2. **Removed Session Registration**:
   ```python
   # OLD:
   session_registry.register_session(port, process.pid, session_dir)
   
   # NEW:
   # BUGFIX: Don't register with global session_registry to avoid cross-session killing
   # session_registry.register_session(port, process.pid, session_dir)
   # Instead, we'll handle cleanup locally in this handler instance
   ```

3. **Removed Session Unregistration**:
   ```python
   # OLD:
   session_registry.unregister_session(port)
   
   # NEW:
   # Note: No longer using global session_registry to avoid cross-session killing
   # session_registry.unregister_session(port)  # DISABLED
   ```

### How It Works Now

1. **Local Session Tracking**: Sessions are tracked only in `FirefoxLauncherHandler._active_sessions`
2. **No Global Signal Handlers**: No global signal handlers that kill all sessions
3. **Instance-Level Cleanup**: Each handler instance manages its own sessions
4. **Isolated Sessions**: Sessions don't interfere with each other

## 🧪 Testing & Verification

### Tests Created

1. **`test_session_killer.py`**: Demonstrates the original problem
2. **`test_bug_verification.py`**: Confirms the bug exists in original code
3. **`test_bug_fix_verification.py`**: Verifies the fix works
4. **`test_final_verification.py`**: Complete scenario testing

### Test Results

```
✅ Session 1 alive: True (after launching Session 2)
✅ Sessions running: 2
✅ Bug status: FIXED
✅ Multi-session support: WORKING
✅ Cross-session killing: PREVENTED
```

## 📊 Impact Assessment

### ✅ Benefits

- **Fixed**: New sessions no longer kill existing sessions
- **Maintained**: Multi-session support still works perfectly
- **Maintained**: Proper cleanup when sessions end normally
- **Improved**: Better session isolation

### ⚠️ Trade-offs

- **Less Aggressive Cleanup**: No global cleanup on abnormal termination
- **Manual Cleanup**: May need manual cleanup for orphaned processes
- **Signal Handling**: Less comprehensive signal-based cleanup

### 🔄 Mitigation

The trade-offs are acceptable because:
1. Normal session cleanup still works (when users close sessions)
2. Process cleanup happens through the handler's `_stop_firefox()` method
3. OS-level process cleanup handles truly orphaned processes
4. The original cross-session killing was a much worse problem

## 🚀 Results

The Firefox launcher now supports multiple concurrent sessions without interference:

- ✅ Users can launch multiple Firefox sessions
- ✅ Each session runs independently
- ✅ Sessions don't kill each other
- ✅ Normal cleanup still works
- ✅ Multi-session architecture preserved

## 🔧 Files Modified

- **`firefox_handler.py`**: Disabled global session registry usage
  - Commented out session_registry imports and calls
  - Sessions now tracked locally in `_active_sessions`
  - No global signal handlers registered

## 🎯 Conclusion

The session killer bug was caused by global signal handlers that were too aggressive in cleaning up sessions. By moving to local session tracking without global signal handlers, we've eliminated the cross-session killing while maintaining all the benefits of multi-session support.

**Result**: The Firefox launcher now works correctly with multiple concurrent sessions! 🎉
