---
layout: page
title: Troubleshooting
permalink: /troubleshooting/
---

# Troubleshooting Guide

Common issues and solutions for the JupyterLab Firefox Launcher extension.

## Quick Diagnostics

### Check Installation Status

First, verify the extension is properly installed:

```bash
# Check if the extension is installed
jupyter labextension list | grep firefox

# Check server extension status
jupyter server extension list | grep firefox

# Verify Python package
pip show jupyterlab-firefox-launcher
```

### Test System Dependencies

```bash
# Test X server functionality
xvfb-run -a firefox --version

# Test VNC server
which x11vnc

# Test noVNC availability  
which novnc_proxy || echo "noVNC not found in PATH"

# Check display availability
echo $DISPLAY
```

### Check Logs

Enable debug logging to see detailed information:

```bash
# Start JupyterLab with debug logging
FIREFOX_LAUNCHER_DEBUG=1 jupyter lab --debug

# Check JupyterLab logs
journalctl --user -u jupyter-lab -f

# Check system logs for X server issues
tail -f /var/log/Xorg.0.log
```

## Common Issues

### 1. Extension Not Loading

**Symptoms:**
- Firefox launcher icon not visible in JupyterLab
- No Firefox launcher in Launcher tab
- Extension not listed in installed extensions

**Possible Causes:**
- Extension not properly installed
- JupyterLab cache issues
- Version compatibility problems

**Solutions:**

```bash
# Reinstall the extension
pip uninstall jupyterlab-firefox-launcher
pip install jupyterlab-firefox-launcher

# Clear JupyterLab cache
jupyter lab clean
jupyter lab build

# Force rebuild
jupyter labextension develop . --overwrite

# Check JupyterLab version compatibility
jupyter --version
```

### 2. Session Launch Failures

**Symptoms:**
- "Failed to launch Firefox session" error
- Timeout during session creation
- Session starts but immediately stops

**Common Error Messages:**

#### "No available ports"
```bash
# Check port availability
netstat -tulpn | grep :6080

# Kill processes using Firefox launcher ports
sudo lsof -ti:6080-6090 | xargs sudo kill -9

# Configure custom port range (in jupyter config)
c.FirefoxLauncherApp.port_range = (7000, 7100)
```

#### "X server failed to start"
```bash
# Install X server dependencies
sudo apt install -y xvfb xauth

# Check X server permissions
ls -la /tmp/.X11-unix/

# Start X server manually to test
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
firefox --version
```

#### "Firefox process died immediately"
```bash
# Check Firefox installation
firefox --version

# Test Firefox in headless mode
xvfb-run -a firefox --version

# Check for missing libraries
ldd $(which firefox) | grep "not found"

# Install missing dependencies
sudo apt install -y libgtk-3-0 libx11-xcb1 libxtst6 libxrandr2 libasound2 libpangocairo-1.0-0
```

### 3. VNC Connection Issues

**Symptoms:**
- Session launches but VNC viewer shows blank screen
- VNC connection refused
- Performance issues in VNC viewer

**Solutions:**

#### VNC Server Not Starting
```bash
# Check if x11vnc is installed
which x11vnc || sudo apt install -y x11vnc

# Test VNC server manually
export DISPLAY=:99
Xvfb $DISPLAY -screen 0 1024x768x24 &
x11vnc -display $DISPLAY -forever -shared -rfbport 5900
```

#### Connection Refused
```bash
# Check if port is accessible
netstat -tulpn | grep :6080

# Check firewall settings
sudo ufw status
sudo ufw allow 6080

# Test local connection
curl http://localhost:6080/
```

#### Poor Performance
```bash
# Reduce quality settings
{
  "quality": 50,
  "dpi": 72
}

# Use lower resolution
export FIREFOX_LAUNCHER_RESOLUTION="800x600"

# Check system resources
htop
free -h
```

### 4. Permission Issues

**Symptoms:**
- "Permission denied" errors
- Cannot write to session directories
- X server authentication failures

**Solutions:**

#### File Permissions
```bash
# Check session directory permissions
ls -la ~/.local/share/jupyterlab-firefox-launcher/

# Fix permissions
chmod -R 755 ~/.local/share/jupyterlab-firefox-launcher/

# Check tmp directory permissions
ls -la /tmp/ | grep firefox-launcher
```

#### X Server Permissions
```bash
# Add user to necessary groups
sudo usermod -a -G video $USER
sudo usermod -a -G audio $USER

# Reset X server authentication
xauth remove $DISPLAY
xauth generate $DISPLAY . trusted
```

#### SELinux Issues (RHEL/CentOS)
```bash
# Check SELinux status
getenforce

# Check for denials
sudo ausearch -m avc -ts recent | grep firefox

# Create custom policy if needed
sudo setsebool -P httpd_can_network_connect 1
```

### 5. Session Management Issues

**Symptoms:**
- Sessions not appearing in list
- Cannot delete sessions
- Cleanup not working properly

**Solutions:**

#### Orphaned Sessions
```bash
# List all Firefox processes
ps aux | grep firefox

# Kill orphaned processes
pkill -f "firefox.*--new-instance"

# Clean up session directories
rm -rf ~/.local/share/jupyterlab-firefox-launcher/sessions/*

# Restart cleanup service
# This is handled automatically, but you can force it:
python -c "
from jupyterlab_firefox_launcher.firefox_handler import FirefoxCleanupHandler
handler = FirefoxCleanupHandler()
handler.cleanup_sessions()
"
```

#### Session Not Found Errors
```bash
# Refresh session list
curl http://localhost:8888/jupyterlab-firefox-launcher/sessions

# Check session storage
ls ~/.local/share/jupyterlab-firefox-launcher/sessions/

# Verify session IDs match
cat ~/.local/share/jupyterlab-firefox-launcher/sessions/*/session_info.json
```

### 6. Docker/Container Issues

**Symptoms:**
- Extension works locally but not in containers
- X server fails in containerized environment
- Permission denied in Docker

**Solutions:**

#### Docker Configuration
```dockerfile
# Dockerfile additions for GUI support
RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    firefox \
    dbus-x11 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV DISPLAY=:99
ENV FIREFOX_LAUNCHER_DOCKER=1

# Create display
RUN Xvfb :99 -screen 0 1024x768x24 &
```

#### Docker Compose
```yaml
# docker-compose.yml
services:
  jupyterlab:
    build: .
    ports:
      - "8888:8888"
      - "6080-6090:6080-6090"
    environment:
      - DISPLAY=:99
      - FIREFOX_LAUNCHER_DEBUG=1
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
    privileged: true  # If needed for X server
```

#### Kubernetes
```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jupyterlab-firefox
spec:
  template:
    spec:
      containers:
      - name: jupyterlab
        image: jupyterlab-firefox:latest
        env:
        - name: DISPLAY
          value: ":99"
        - name: FIREFOX_LAUNCHER_DEBUG
          value: "1"
        securityContext:
          runAsUser: 1000
          runAsGroup: 1000
        volumeMounts:
        - name: x11
          mountPath: /tmp/.X11-unix
      volumes:
      - name: x11
        emptyDir: {}
```

### 7. Performance Issues

**Symptoms:**
- Slow session launch times
- High CPU/memory usage
- Browser responsiveness issues

**Diagnostic Commands:**
```bash
# Monitor resource usage
htop
iotop
nethogs

# Check disk space
df -h
du -sh ~/.local/share/jupyterlab-firefox-launcher/

# Monitor network traffic
ss -tulpn | grep :6080
```

**Optimization Solutions:**
```bash
# Reduce quality for better performance
export FIREFOX_LAUNCHER_DEFAULT_QUALITY=30

# Limit concurrent sessions
export FIREFOX_LAUNCHER_MAX_SESSIONS=3

# Increase cleanup frequency
export FIREFOX_LAUNCHER_CLEANUP_INTERVAL=60

# Use lower resolution
export FIREFOX_LAUNCHER_RESOLUTION="800x600"
```

### 8. Network Connectivity Issues

**Symptoms:**
- Cannot access external websites in Firefox
- DNS resolution failures
- Proxy configuration issues

**Solutions:**

#### DNS Issues
```bash
# Test DNS resolution
nslookup google.com

# Configure DNS in session
echo "nameserver 8.8.8.8" > /tmp/resolv.conf
export FIREFOX_DNS_SERVERS="8.8.8.8,8.8.4.4"
```

#### Proxy Configuration
```bash
# Set proxy environment variables
export http_proxy=http://proxy:8080
export https_proxy=http://proxy:8080
export no_proxy=localhost,127.0.0.1

# Configure Firefox proxy
# This is handled automatically by the extension
```

#### Firewall Issues
```bash
# Check iptables rules
sudo iptables -L

# Allow outbound connections
sudo iptables -A OUTPUT -j ACCEPT

# Check UFW status
sudo ufw status verbose
```

## Linux Distribution-Specific Issues

### Ubuntu/Debian

#### Missing Packages
```bash
# Install all required packages
sudo apt update
sudo apt install -y \
    firefox \
    xvfb \
    x11vnc \
    dbus-x11 \
    xauth \
    xfonts-base \
    xfonts-75dpi \
    xfonts-100dpi
```

#### Snap Firefox Issues
```bash
# If using snap Firefox, it may have additional restrictions
snap list | grep firefox

# Consider using apt version instead
sudo snap remove firefox
sudo apt install firefox
```

### CentOS/RHEL

#### EPEL Repository
```bash
# Enable EPEL for additional packages
sudo yum install -y epel-release

# Install packages
sudo yum install -y firefox xorg-x11-server-Xvfb x11vnc
```

#### SELinux Issues
```bash
# Check SELinux context
ls -Z ~/.local/share/jupyterlab-firefox-launcher/

# If needed, adjust SELinux policies
sudo setsebool -P use_nfs_home_dirs 1
```

## Advanced Debugging

### Debug Mode

Enable comprehensive debugging:

```python
# In Python code
import logging
logging.basicConfig(level=logging.DEBUG)

# Set environment variables
export FIREFOX_LAUNCHER_DEBUG=1
export FIREFOX_LAUNCHER_TRACE=1
export XVFB_DEBUG=1
```

### Memory Debugging

```bash
# Monitor memory usage
while true; do
    echo "$(date): $(ps aux | grep firefox | grep -v grep | awk '{sum += $6} END {print sum/1024 " MB"}')"
    sleep 10
done

# Check for memory leaks
valgrind --tool=memcheck firefox --version
```

### Network Debugging

```bash
# Monitor network connections
netstat -tulpn | grep firefox

# Trace network activity
tcpdump -i lo port 6080

# Debug VNC protocol
x11vnc -display :99 -verbose -debug 2
```

### Process Debugging

```bash
# Monitor process creation
ps -ef | grep firefox | watch -n 1

# Debug process signals
strace -p $(pgrep firefox) 2>&1 | grep -i signal

# Check process limits
ulimit -a
```

## Recovery Procedures

### Complete Reset

If all else fails, perform a complete reset:

```bash
# Stop JupyterLab
jupyter lab stop

# Kill all Firefox processes
pkill -f firefox

# Clear all session data
rm -rf ~/.local/share/jupyterlab-firefox-launcher/

# Clear JupyterLab cache
jupyter lab clean

# Reinstall extension
pip uninstall jupyterlab-firefox-launcher
pip install jupyterlab-firefox-launcher

# Rebuild JupyterLab
jupyter lab build

# Restart JupyterLab
jupyter lab
```

### Backup and Restore

```bash
# Backup configuration
cp -r ~/.local/share/jupyterlab-firefox-launcher/ ~/firefox-launcher-backup/

# Restore from backup
rm -rf ~/.local/share/jupyterlab-firefox-launcher/
cp -r ~/firefox-launcher-backup/ ~/.local/share/jupyterlab-firefox-launcher/
```

## Getting Help

### Log Collection

When reporting issues, collect these logs:

```bash
# Create debug bundle
mkdir firefox-launcher-debug
cd firefox-launcher-debug

# System information
uname -a > system_info.txt
lsb_release -a >> system_info.txt 2>/dev/null
python --version >> system_info.txt
jupyter --version >> system_info.txt

# Package information
pip show jupyterlab-firefox-launcher > package_info.txt
jupyter labextension list > extensions.txt

# JupyterLab logs
FIREFOX_LAUNCHER_DEBUG=1 jupyter lab --debug > jupyterlab.log 2>&1 &
sleep 30
pkill jupyter

# System logs
dmesg | tail -100 > dmesg.log
journalctl --user -u jupyter-lab --no-pager > journal.log

# Process information
ps aux | grep -E "(firefox|jupyter|xvfb|x11vnc)" > processes.txt

# Network information
netstat -tulpn | grep -E "(6080|8888)" > network.txt

# Tar the bundle
cd ..
tar -czf firefox-launcher-debug.tar.gz firefox-launcher-debug/
```

### Support Channels

1. **GitHub Issues**: [Report bugs and feature requests](https://github.com/vantagecompute/jupyterlab-firefox-launcher/issues)
2. **GitHub Discussions**: [Ask questions and get help](https://github.com/vantagecompute/jupyterlab-firefox-launcher/discussions)
3. **Email Support**: [james@vantagecompute.ai](mailto:james@vantagecompute.ai)

### Before Reporting

Please check:
- [ ] Issue doesn't already exist in GitHub Issues
- [ ] You've tried the troubleshooting steps above
- [ ] You have the latest version installed
- [ ] You've collected relevant logs and information

### Issue Template

When reporting issues, include:

```markdown
## Environment
- OS: Ubuntu 22.04
- Python: 3.11.0
- JupyterLab: 4.4.5
- Extension version: 0.1.0

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Logs
[Attach debug bundle or paste relevant logs]

## Additional Context
Any other relevant information
```

## Prevention

### Best Practices

- **Monitor resources** regularly
- **Keep dependencies updated**
- **Use appropriate session limits**
- **Enable cleanup automation**
- **Regular health checks**

### Health Check Script

```bash
#!/bin/bash
# firefox-launcher-health.sh

echo "=== Firefox Launcher Health Check ==="

# Check if JupyterLab is running
if pgrep -f "jupyter-lab" > /dev/null; then
    echo "✓ JupyterLab is running"
else
    echo "✗ JupyterLab is not running"
fi

# Check extension installation
if jupyter labextension list 2>/dev/null | grep -q firefox; then
    echo "✓ Extension is installed"
else
    echo "✗ Extension is not installed"
fi

# Check for orphaned processes
orphaned=$(ps aux | grep firefox | grep -c new-instance)
if [ $orphaned -eq 0 ]; then
    echo "✓ No orphaned Firefox processes"
else
    echo "⚠ Found $orphaned orphaned Firefox processes"
fi

# Check disk usage
usage=$(du -sh ~/.local/share/jupyterlab-firefox-launcher/ 2>/dev/null | cut -f1)
echo "📊 Session data usage: ${usage:-0B}"

# Check active sessions
sessions=$(curl -s http://localhost:8888/jupyterlab-firefox-launcher/sessions 2>/dev/null | jq -r '.count' 2>/dev/null)
echo "📊 Active sessions: ${sessions:-0}"

echo "=== Health Check Complete ==="
```

Make it executable and run regularly:
```bash
chmod +x firefox-launcher-health.sh
./firefox-launcher-health.sh

# Add to crontab for regular checks
echo "0 */6 * * * /path/to/firefox-launcher-health.sh" | crontab -
```
