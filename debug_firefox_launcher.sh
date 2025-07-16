#!/bin/bash
# Debug script to test Firefox launcher components manually

echo "🔍 Firefox Launcher Debug Script"
echo "================================="

# Test Xpra
echo "📋 Testing Xpra availability..."
if command -v xpra >/dev/null 2>&1; then
    echo "✅ Xpra found: $(which xpra)"
    xpra --version
else
    echo "❌ Xpra not found"
    exit 1
fi

# Test Firefox
echo -e "\n📋 Testing Firefox availability..."
if command -v firefox >/dev/null 2>&1; then
    echo "✅ Firefox found: $(which firefox)"
    firefox --version
else
    echo "❌ Firefox not found"
    exit 1
fi

# Test wrapper scripts
echo -e "\n📋 Testing wrapper scripts..."
WRAPPER_DIR="$HOME/.firefox-launcher-wrapper.sh"
if [ -f "$WRAPPER_DIR" ]; then
    echo "✅ User wrapper found: $WRAPPER_DIR"
    ls -la "$WRAPPER_DIR"
else
    echo "ℹ️  User wrapper not found, creating one..."
    cat > "$WRAPPER_DIR" << 'EOF'
#!/bin/bash
export MOZ_DISABLE_CONTENT_SANDBOX=1
export MOZ_DISABLE_GMP_SANDBOX=1
exec firefox --new-instance --no-first-run --profile ~/.firefox-launcher-profile "$@"
EOF
    chmod +x "$WRAPPER_DIR"
    echo "✅ Created user wrapper: $WRAPPER_DIR"
fi

# Test wrapper execution
echo -e "\n📋 Testing wrapper execution..."
if "$WRAPPER_DIR" --version >/dev/null 2>&1; then
    echo "✅ Wrapper executes successfully"
else
    echo "❌ Wrapper execution failed"
fi

# Test Xpra HTML5 support
echo -e "\n📋 Testing Xpra HTML5 support..."
HTML5_PATHS=(
    "/usr/share/xpra/www"
    "/usr/local/share/xpra/www"
    "/opt/xpra/share/xpra/www"
)

for path in "${HTML5_PATHS[@]}"; do
    if [ -d "$path" ]; then
        echo "✅ HTML5 support found: $path"
        break
    fi
done

# Test socket directory creation
echo -e "\n📋 Testing socket directory creation..."
SOCKET_DIR="$HOME/.firefox-launcher/sockets"
mkdir -p "$SOCKET_DIR"
if [ -d "$SOCKET_DIR" ]; then
    echo "✅ Socket directory created: $SOCKET_DIR"
else
    echo "❌ Cannot create socket directory"
fi

# Test a minimal Xpra command
echo -e "\n📋 Testing minimal Xpra start (5 seconds)..."
TEST_PORT=19876
XPRA_CMD="xpra start --bind-tcp=127.0.0.1:$TEST_PORT --html=on --daemon=no --exit-with-children=yes"

echo "Command: $XPRA_CMD"
timeout 5s $XPRA_CMD &
XPRA_PID=$!

sleep 2
if kill -0 $XPRA_PID 2>/dev/null; then
    echo "✅ Xpra started successfully"
    kill $XPRA_PID 2>/dev/null
else
    echo "❌ Xpra failed to start"
fi

# Test full command
echo -e "\n📋 Testing full Xpra+Firefox command (10 seconds)..."
FULL_CMD="xpra start --bind-tcp=127.0.0.1:$TEST_PORT --html=on --daemon=no --exit-with-children=yes --start='$WRAPPER_DIR'"

echo "Command: $FULL_CMD"
timeout 10s $FULL_CMD &
FULL_PID=$!

sleep 3
if kill -0 $FULL_PID 2>/dev/null; then
    echo "✅ Full command started successfully"
    echo "🌐 Test in browser: http://localhost:$TEST_PORT"
    sleep 5
    kill $FULL_PID 2>/dev/null
else
    echo "❌ Full command failed to start"
fi

echo -e "\n✅ Debug script completed"
