# JupyterLab Firefox Launcher - Deployment Guide (v0.7.1)

## Fixed Issues in v0.7.1
- ✅ Fixed URL routing to properly handle JupyterHub service prefix
- ✅ Fixed tab behavior to open Firefox in JupyterLab tab instead of new browser window
- ✅ Added proper @jupyterlab/coreutils dependency for URLExt.join()
- ✅ Implemented proper JupyterLab Widget API for tab management

## Quick Deployment Steps

### 1. Upload the wheel file to your JupyterHub server
```bash
scp dist/jupyterlab_firefox_launcher-0.7.1-py3-none-any.whl user@your-server:/tmp/
```

### 2. Install on JupyterHub server
```bash
# SSH to your server
ssh user@your-server

# Install the fixed extension
sudo pip install /tmp/jupyterlab_firefox_launcher-0.7.1-py3-none-any.whl --force-reinstall

# Restart JupyterHub
sudo systemctl restart jupyterhub  # or your restart method
```

### 3. Test the Fixed Extension

1. **Access JupyterLab**: Navigate to your JupyterHub and start a server
2. **Find Firefox Launcher**: Look for Firefox icon in the Launcher under "Other" section
3. **Test Launch**: Click the Firefox icon
4. **Verify Behavior**: 
   - Firefox should open in a new JupyterLab tab (not browser window)
   - URL should be properly routed through service prefix
   - No 404 errors should occur

## Key Fixes Applied

### Frontend URL Routing
- **Before**: `window.location.origin + '/firefox-desktop'`
- **After**: `URLExt.join(app.serviceManager.serverSettings.baseUrl, 'firefox-desktop')`

### Tab Behavior
- **Before**: `window.open(url, '_blank')`
- **After**: `app.shell.add(widget, 'main')` with proper Widget integration

### Dependencies
- **Added**: `@jupyterlab/coreutils` for proper URL handling

## Troubleshooting

If you still encounter issues:

1. **Check Extension Installation**:
   ```bash
   jupyter labextension list | grep firefox
   ```

2. **Verify Server Proxy**:
   ```bash
   jupyter server extension list | grep server-proxy
   ```

3. **Run Diagnostics**:
   ```bash
   python -m jupyterlab_firefox_launcher
   ```

4. **Check Logs**:
   ```bash
   sudo journalctl -u jupyterhub -f
   ```

## Expected Behavior After Fix

✅ Firefox launcher icon appears in JupyterLab launcher  
✅ Clicking icon opens Firefox in new JupyterLab tab  
✅ URL routing works correctly with service prefix  
✅ No 404 errors when accessing firefox-desktop endpoint  
✅ Firefox session runs properly through Xpra HTML5  

## Version History

- **v0.7.1**: Fixed URL routing and tab behavior issues
- **v0.7.0**: Initial working server-proxy implementation
- **v0.6.x**: Development versions with UI integration work
