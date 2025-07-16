# Firefox Launcher Configuration Options

This document describes how to customize the Firefox launcher behavior using environment variables and wrapper scripts.

## Basic Configuration

The Firefox launcher uses Xpra with `--start=<wrapper-script>` to give you full control over Firefox startup options.

### Default Wrapper Script

The default wrapper script is located at:
```
jupyterlab_firefox_launcher/share/firefox-xstartup
```

This script provides basic Firefox configuration optimized for Xpra.

### Advanced Wrapper Script

For more customization options, use the advanced wrapper:
```bash
export FIREFOX_LAUNCHER_ADVANCED=1
```

This enables the advanced wrapper located at:
```
jupyterlab_firefox_launcher/share/firefox-wrapper-advanced
```

## Environment Variables

### Xpra Configuration

- `FIREFOX_LAUNCHER_QUALITY` (default: "100")
  - Image quality (0-100)
  - Higher values = better quality, more bandwidth

- `FIREFOX_LAUNCHER_COMPRESS` (default: "0") 
  - Compression level (0-9)
  - Higher values = more compression, less bandwidth

- `FIREFOX_LAUNCHER_DPI` (default: "96")
  - Screen DPI setting

- `FIREFOX_LAUNCHER_WRAPPER` (default: auto)
  - Path to custom wrapper script

### Firefox Configuration (Advanced Wrapper Only)

- `FIREFOX_PROFILE_DIR` (default: `$HOME/.firefox-launcher-profile`)
  - Custom Firefox profile directory

- `FIREFOX_WINDOW_SIZE` (default: "1280,800")
  - Initial Firefox window size

- `FIREFOX_START_URL` (default: "about:blank")
  - URL to open on Firefox startup

- `FIREFOX_CLASS_NAME` (default: "Firefox-Launcher")
  - X11 window class name

- `FIREFOX_EXTRA_ARGS` (default: "")
  - Additional Firefox command line arguments

## Usage Examples

### High Quality Mode
```bash
export FIREFOX_LAUNCHER_QUALITY=100
export FIREFOX_LAUNCHER_COMPRESS=0
jupyter lab
```

### Low Bandwidth Mode
```bash
export FIREFOX_LAUNCHER_QUALITY=50
export FIREFOX_LAUNCHER_COMPRESS=5
jupyter lab
```

### Custom Firefox Configuration
```bash
export FIREFOX_LAUNCHER_ADVANCED=1
export FIREFOX_START_URL="https://www.google.com"
export FIREFOX_WINDOW_SIZE="1920,1080"
export FIREFOX_EXTRA_ARGS="--kiosk"
jupyter lab
```

### Custom Wrapper Script
```bash
# Create your own wrapper
cat > /tmp/my-firefox-wrapper << 'EOF'
#!/bin/sh
exec firefox --safe-mode --new-instance about:blank
EOF
chmod +x /tmp/my-firefox-wrapper

export FIREFOX_LAUNCHER_WRAPPER=/tmp/my-firefox-wrapper
jupyter lab
```

## Wrapper Script Development

### Template for Custom Wrapper

```bash
#!/bin/sh
# Custom Firefox wrapper for Xpra

cd "$HOME"

# Set environment variables
export MOZ_USE_XINPUT2=1
export MOZ_ENABLE_WAYLAND=0

# Your custom Firefox options here
exec firefox \
    --new-instance \
    --class=MyFirefox \
    --profile /path/to/custom/profile \
    --your-custom-options \
    about:blank
```

### Key Points

1. **Use `exec`**: Always use `exec` to replace the shell process
2. **Set MOZ_* variables**: Required for proper Xpra integration
3. **Use `--new-instance`**: Prevents conflicts with existing Firefox
4. **Set `--class`**: Helps Xpra track the window properly

## Troubleshooting

### Check Xpra Command
The actual Xpra command being used is logged when the session starts. Look for:
```
xpra start --bind-tcp=0.0.0.0:PORT --start=/path/to/wrapper ...
```

### Test Wrapper Script Manually
```bash
# Test your wrapper script
/path/to/wrapper/script

# Test with Xpra
xpra start --bind-tcp=0.0.0.0:9999 --html=on --start=/path/to/wrapper
```

### Debug Firefox Issues
Add debugging to your wrapper script:
```bash
#!/bin/sh
set -x  # Enable debug output
exec firefox --verbose your-options 2>&1 | tee /tmp/firefox-debug.log
```

## Integration with JupyterHub/SlurmSpawner

The wrapper script approach works well with distributed computing environments:

1. **Process Isolation**: Xpra manages the Firefox process separately
2. **No Terminal Blocking**: jupyter-server-proxy handles process management
3. **User-Space Operation**: No root privileges required
4. **Resource Cleanup**: Processes exit cleanly when session ends

This architecture eliminates the terminal freezing issues you experienced with the previous implementation.
