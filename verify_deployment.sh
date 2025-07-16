#!/bin/bash

# JupyterLab Firefox Launcher - Post-Deployment Verification Script
# Run this after deploying v0.7.1 to verify the fixes are working

echo "🔍 JupyterLab Firefox Launcher - Verification Script (v0.7.1)"
echo "============================================================"

# Check if extension is installed
echo "1. Checking extension installation..."
if jupyter labextension list 2>/dev/null | grep -q "jupyterlab-firefox-launcher"; then
    echo "✅ Extension is installed"
    jupyter labextension list | grep firefox
else
    echo "❌ Extension not found"
    exit 1
fi

echo ""

# Check if server proxy is available
echo "2. Checking jupyter-server-proxy..."
if jupyter server extension list 2>/dev/null | grep -q "jupyter_server_proxy"; then
    echo "✅ jupyter-server-proxy is available"
else
    echo "❌ jupyter-server-proxy not found"
    exit 1
fi

echo ""

# Check if Xpra is available
echo "3. Checking Xpra installation..."
if command -v xpra >/dev/null 2>&1; then
    echo "✅ Xpra is available"
    xpra --version | head -1
else
    echo "❌ Xpra not found"
    exit 1
fi

echo ""

# Check if Firefox is available
echo "4. Checking Firefox installation..."
if command -v firefox >/dev/null 2>&1; then
    echo "✅ Firefox is available"
    firefox --version
else
    echo "❌ Firefox not found"
    exit 1
fi

echo ""

# Run diagnostic if available
echo "5. Running extension diagnostics..."
if python -c "import jupyterlab_firefox_launcher" 2>/dev/null; then
    echo "✅ Extension module can be imported"
    python -m jupyterlab_firefox_launcher
else
    echo "❌ Extension module import failed"
    exit 1
fi

echo ""
echo "🎉 All checks passed! Extension should be working correctly."
echo ""
echo "📋 Next Steps:"
echo "   1. Start JupyterLab"
echo "   2. Look for Firefox icon in Launcher > Other section"
echo "   3. Click to test - should open in JupyterLab tab, not browser window"
echo "   4. Verify no 404 errors occur"
echo ""
echo "🐛 If issues persist, check JupyterHub logs:"
echo "   sudo journalctl -u jupyterhub -f"
