#!/bin/bash
# Deploy Firefox Launcher Extension to Ubuntu Server
# Usage: ./deploy_to_server.sh [user@server]

set -e

SERVER=${1:-"ubuntu@your-server"}
EXTENSION_NAME="jupyterhub-firefox-launcher-extension"
LOCAL_DIR="$(pwd)"

echo "🚀 Deploying Firefox Launcher Extension to Ubuntu Server"
echo "========================================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Please run this script from the extension directory"
    exit 1
fi

echo "📦 Creating deployment package..."

# Create a temporary deployment package
TEMP_DIR=$(mktemp -d)
DEPLOY_DIR="$TEMP_DIR/$EXTENSION_NAME"
mkdir -p "$DEPLOY_DIR"

# Copy essential files (excluding development artifacts)
echo "📁 Copying extension files..."
cp -r jupyterlab_firefox_launcher/ "$DEPLOY_DIR/"
cp -r frontend/ "$DEPLOY_DIR/"
cp pyproject.toml "$DEPLOY_DIR/"
cp package.json "$DEPLOY_DIR/"
cp tsconfig.json "$DEPLOY_DIR/"
cp install_and_test.py "$DEPLOY_DIR/"
cp README.md "$DEPLOY_DIR/"
cp SLURM_DEPLOYMENT.md "$DEPLOY_DIR/"

# Copy shell scripts with executable permissions
cp firefox-* "$DEPLOY_DIR/" 2>/dev/null || true
chmod +x "$DEPLOY_DIR"/firefox-* 2>/dev/null || true

echo "📤 Uploading to server: $SERVER"

# Upload the package
scp -r "$DEPLOY_DIR" "$SERVER:~/"

echo "🔧 Running remote installation..."

# Run installation on the server
ssh "$SERVER" << 'EOF'
set -e

cd ~/jupyterhub-firefox-launcher-extension

echo "🔍 Checking Ubuntu server environment..."

# Check OS
echo "📋 OS Information:"
lsb_release -a 2>/dev/null || cat /etc/os-release

# Check if we have Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# Check if we have Node.js for building extensions
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js for extension building..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Install system dependencies for Ubuntu
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    xpra \
    xpra-html5 \
    firefox \
    python3-pip \
    python3-venv \
    build-essential \
    python3-dev

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install
echo "📦 Installing Python dependencies..."
source venv/bin/activate

# Upgrade pip and install base packages
pip install --upgrade pip setuptools wheel

# Install JupyterLab and required packages
pip install jupyterlab jupyter-server-proxy

# Run the installation script
echo "🚀 Running extension installation..."
python3 install_and_test.py

echo "✅ Installation completed on Ubuntu server!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source ~/jupyterhub-firefox-launcher-extension/venv/bin/activate"
echo "2. Start JupyterLab: jupyter lab --ip=0.0.0.0 --port=8888 --no-browser"
echo "3. Access via browser and look for 'Firefox Browser' in the launcher"
EOF

# Clean up
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "To connect to the server and test:"
echo "  ssh $SERVER"
echo "  cd ~/jupyterhub-firefox-launcher-extension"
echo "  source venv/bin/activate"
echo "  jupyter lab --ip=0.0.0.0 --port=8888 --no-browser"
echo ""
echo "Then access JupyterLab via: http://your-server-ip:8888"
