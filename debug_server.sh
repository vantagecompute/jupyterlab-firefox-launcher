#!/bin/bash
# Firefox Launcher Extension - Server Debugging Script
# Run this on your JupyterHub server

echo "🔧 Firefox Launcher Extension - Server Debugging"
echo "================================================"

echo ""
echo "🔍 1. Checking if extension is installed..."
python3 -c "import jupyterlab_firefox_launcher; print('✅ Extension package found')" 2>/dev/null || echo "❌ Extension package NOT found"

echo ""
echo "🔍 2. Checking server proxy entry points..."
python3 -c "
try:
    import pkg_resources
    found = False
    for ep in pkg_resources.iter_entry_points('jupyter_serverproxy_servers'):
        if ep.name == 'firefox-desktop':
            print('✅ firefox-desktop entry point found')
            found = True
            break
    if not found:
        print('❌ firefox-desktop entry point NOT found')
except Exception as e:
    print(f'❌ Error checking entry points: {e}')
"

echo ""
echo "🔍 3. Testing server proxy function..."
python3 -c "
try:
    from jupyterlab_firefox_launcher.server_proxy import setup_firefox_desktop
    config = setup_firefox_desktop()
    print('✅ Server proxy function works')
    print(f'📋 Command: {config[\"command\"][0:3]}...')
except Exception as e:
    print(f'❌ Server proxy function failed: {e}')
"

echo ""
echo "🔍 4. Checking Jupyter server extensions..."
jupyter server extension list 2>/dev/null | grep -i firefox || echo "❌ Firefox extension not found in server extensions"

echo ""
echo "🔍 5. Checking JupyterLab extensions..."
jupyter labextension list 2>/dev/null | grep -i firefox || echo "❌ Firefox extension not found in lab extensions"

echo ""
echo "🔍 6. Checking system dependencies..."
xpra --version >/dev/null 2>&1 && echo "✅ Xpra available" || echo "❌ Xpra not available"
firefox --version >/dev/null 2>&1 && echo "✅ Firefox available" || echo "❌ Firefox not available"

echo ""
echo "🔍 7. Testing URL endpoints..."
echo "📋 Environment variables:"
echo "   JUPYTERHUB_SERVICE_PREFIX: ${JUPYTERHUB_SERVICE_PREFIX:-'not set'}"
echo "   JUPYTERHUB_BASE_URL: ${JUPYTERHUB_BASE_URL:-'not set'}"

echo ""
echo "🎯 Expected URL paths:"
if [ -n "$JUPYTERHUB_SERVICE_PREFIX" ]; then
    echo "   Full URL: https://your-domain${JUPYTERHUB_SERVICE_PREFIX}firefox-desktop/"
else
    echo "   Relative URL: /firefox-desktop/"
fi

echo ""
echo "🔧 If everything shows ✅ but you still get 404:"
echo "   1. Restart JupyterHub: sudo systemctl restart jupyterhub"
echo "   2. Try the Firefox icon in JupyterLab launcher"
echo "   3. Check nginx/proxy configuration if using one"
