#!/usr/bin/env python3
"""
Firefox Launcher Installation and Test Script

This script helps install and test the new Xpra-based Firefox launcher.
"""

import subprocess
import sys
import os
from pathlib import Path
from shutil import which

def run_command(cmd, description, check=True):
    """Run a command with description"""
    print(f"\n>>> {description}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"Output: {result.stdout}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def check_dependencies():
    """Check if required system dependencies are available in SlurmSpawner environment"""
    print("=== Checking SlurmSpawner Environment Dependencies ===")
    
    # Check if we're in a SlurmSpawner environment
    is_slurm_env = any([
        os.environ.get('SLURM_JOB_ID'),
        os.environ.get('SLURM_PROCID') is not None,
        os.environ.get('SLURM_NODEID') is not None,
        os.path.exists('/etc/slurm') or os.path.exists('/usr/local/etc/slurm')
    ])
    
    if is_slurm_env:
        print("🔍 Detected SlurmSpawner environment")
        print("📍 Running on compute node - checking available modules and software")
    else:
        print("🔍 Standard environment detected")
    
    deps = {
        'xpra': 'Xpra (remote display server)',
        'firefox': 'Firefox browser',
        'jupyter': 'Jupyter'
    }
    
    missing = []
    module_suggestions = []
    
    for cmd, desc in deps.items():
        cmd_path = which(cmd)
        if cmd_path:
            print(f"✅ {desc}: {cmd_path}")
        else:
            print(f"❌ {desc}: NOT FOUND in PATH")
            missing.append(cmd)
            
            # Try to suggest module loading for SlurmSpawner
            if is_slurm_env:
                if cmd == 'xpra':
                    module_suggestions.extend([
                        "module load xpra",
                        "module load X11/xpra", 
                        "module load gui/xpra"
                    ])
                elif cmd == 'firefox':
                    module_suggestions.extend([
                        "module load firefox",
                        "module load browsers/firefox",
                        "module load Mozilla/Firefox"
                    ])
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        
        if is_slurm_env:
            print("\n🏗️  SlurmSpawner Environment - Try loading modules:")
            print("  Check available modules: module avail")
            for suggestion in set(module_suggestions):  # Remove duplicates
                print(f"  Try: {suggestion}")
            print("\n📝 Add successful module loads to your SlurmSpawner configuration:")
            print("  c.SlurmSpawner.batch_script = '''")
            print("  module load xpra firefox")
            print("  {cmd}")
            print("  '''")
            print("\n🔧 Alternative: Install in user space:")
            print("  conda install -c conda-forge xpra firefox")
            print("  pip install --user firefox-launcher-deps")
        else:
            print("\nInstall with:")
            print("  Ubuntu/Debian: sudo apt-get install xpra xpra-html5 firefox")
            print("  RHEL/CentOS: sudo yum install xpra python3-xpra-html5 firefox")
            print("  Conda: conda install -c conda-forge xpra firefox")
        
        return False
    
    # Additional SlurmSpawner checks
    if is_slurm_env:
        print("\n🔍 SlurmSpawner Environment Checks:")
        
        # Check DISPLAY setting
        display = os.environ.get('DISPLAY')
        if display:
            print(f"📺 DISPLAY: {display}")
        else:
            print("📺 DISPLAY: Not set (Xpra will create virtual display)")
        
        # Check user permissions for socket creation
        home_dir = os.path.expanduser("~")
        socket_test_dir = os.path.join(home_dir, '.firefox-launcher-test')
        try:
            os.makedirs(socket_test_dir, exist_ok=True)
            os.rmdir(socket_test_dir)
            print("✅ User-space socket creation: OK")
        except Exception as e:
            print(f"❌ User-space socket creation: FAILED - {e}")
            return False
        
        # Check if we can bind to ports
        import socket as sock
        try:
            s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
            s.bind(('localhost', 0))
            port = s.getsockname()[1]
            s.close()
            print(f"✅ Port binding test: OK (got port {port})")
        except Exception as e:
            print(f"❌ Port binding test: FAILED - {e}")
            return False
        
        # Check available compute resources
        try:
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            cpu_count = psutil.cpu_count()
            print(f"💾 Compute node resources: {cpu_count} CPUs, {memory_gb:.1f}GB RAM")
            
            if memory_gb < 2:
                print("⚠️  Low memory - Firefox may struggle with <2GB RAM")
            if cpu_count < 2:
                print("⚠️  Single CPU - performance may be limited")
                
        except ImportError:
            print("📊 Resource check: psutil not available")
    
    return True

def install_extension():
    """Install the Firefox launcher extension"""
    print("\n=== Installing Firefox Launcher Extension ===")
    
    # Install in development mode
    success = run_command(
        [sys.executable, '-m', 'pip', 'install', '-e', '.'],
        "Installing extension in development mode"
    )
    
    if not success:
        return False
    
    # Enable the server extension
    success = run_command(
        ['jupyter', 'server', 'extension', 'enable', 'jupyterlab_firefox_launcher'],
        "Enabling server extension"
    )
    
    if not success:
        return False
    
    # Build and install the lab extension
    success = run_command(
        ['jupyter', 'labextension', 'develop', '.', '--overwrite'],
        "Installing lab extension"
    )
    
    return success

def test_installation():
    """Test the installation with SlurmSpawner considerations"""
    print("\n=== Testing Installation ===")
    
    # Check if we're in SlurmSpawner environment
    is_slurm_env = any([
        os.environ.get('SLURM_JOB_ID'),
        os.environ.get('SLURM_PROCID') is not None,
        os.environ.get('SLURM_NODEID') is not None
    ])
    
    if is_slurm_env:
        print("🔍 Testing in SlurmSpawner environment")
        print(f"🖥️  Compute node: {os.environ.get('SLURMD_NODENAME', 'unknown')}")
        print(f"🆔 Job ID: {os.environ.get('SLURM_JOB_ID', 'unknown')}")
    
    # Check server extension
    result = subprocess.run(
        ['jupyter', 'server', 'extension', 'list'],
        capture_output=True, text=True
    )
    
    if 'jupyterlab_firefox_launcher' in result.stdout:
        print("✅ Server extension is installed")
    else:
        print("❌ Server extension not found")
        print("📋 Available extensions:")
        for line in result.stdout.split('\n'):
            if line.strip() and 'enabled' in line.lower():
                print(f"   {line.strip()}")
        return False
    
    # Check lab extension
    result = subprocess.run(
        ['jupyter', 'labextension', 'list'],
        capture_output=True, text=True
    )
    
    if 'jupyterlab-firefox-launcher' in result.stdout:
        print("✅ Lab extension is installed")
    else:
        print("❌ Lab extension not found")
        print("📋 Available lab extensions:")
        for line in result.stdout.split('\n'):
            if line.strip() and ('enabled' in line.lower() or 'disabled' in line.lower()):
                print(f"   {line.strip()}")
        return False
    
    # Check if jupyter-server-proxy entry point works
    try:
        from jupyterlab_firefox_launcher.server_proxy import setup_firefox_desktop
        config = setup_firefox_desktop()
        print("✅ Server proxy configuration loads successfully")
        print(f"   Command: {config['command'][0:2]}...")
        print(f"   Port: {config.get('port', 'dynamic')}")
        print(f"   Launcher title: {config['launcher_entry']['title']}")
        
        # SlurmSpawner specific checks
        if is_slurm_env:
            print("🔍 SlurmSpawner specific configuration:")
            command_str = ' '.join(config['command'])
            
            # Check for user-space socket configuration
            if '--socket-dirs=' in command_str:
                print("✅ User-space socket configuration detected")
            else:
                print("⚠️  No user-space socket configuration found")
            
            # Check for proper Xpra options for compute nodes
            if '--system-proxy-socket=no' in command_str:
                print("✅ System proxy socket disabled (good for compute nodes)")
            else:
                print("⚠️  System proxy socket not explicitly disabled")
                
            if '--daemon=no' in command_str:
                print("✅ Daemon mode disabled (good for process management)")
            else:
                print("⚠️  Daemon mode not disabled")
        
        return True
    except Exception as e:
        print(f"❌ Server proxy configuration failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Try to give helpful hints for SlurmSpawner
        if is_slurm_env and 'xpra' in str(e).lower():
            print("💡 SlurmSpawner hint: Check if Xpra is available on compute nodes")
            print("   Try: srun --pty which xpra")
            print("   Or add to batch script: module load xpra")
        
        return False


def test_slurm_environment():
    """Test SlurmSpawner specific requirements"""
    print("\n=== SlurmSpawner Environment Test ===")
    
    # Check if we're actually in SLURM
    slurm_vars = {
        'SLURM_JOB_ID': os.environ.get('SLURM_JOB_ID'),
        'SLURM_PROCID': os.environ.get('SLURM_PROCID'),
        'SLURM_NODEID': os.environ.get('SLURM_NODEID'),
        'SLURMD_NODENAME': os.environ.get('SLURMD_NODENAME'),
        'SLURM_NTASKS': os.environ.get('SLURM_NTASKS'),
        'SLURM_CPUS_PER_TASK': os.environ.get('SLURM_CPUS_PER_TASK'),
        'SLURM_MEM_PER_NODE': os.environ.get('SLURM_MEM_PER_NODE')
    }
    
    found_slurm = any(v is not None for v in slurm_vars.values())
    
    if not found_slurm:
        print("ℹ️  Not running in SlurmSpawner environment")
        print("   This is normal for testing on login nodes")
        return True
    
    print("🎯 Running in SlurmSpawner environment")
    for key, value in slurm_vars.items():
        if value is not None:
            print(f"   {key}: {value}")
    
    # Test module system availability
    print("\n🔧 Testing module system:")
    try:
        result = subprocess.run(['module', 'avail'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Module system available")
            
            # Check for specific modules we need
            modules_to_check = ['xpra', 'firefox', 'python']
            for module in modules_to_check:
                if module.lower() in result.stdout.lower():
                    print(f"✅ {module} module available")
                else:
                    print(f"⚠️  {module} module not found (may need different name)")
        else:
            print("❌ Module system not available or not configured")
    except FileNotFoundError:
        print("❌ Module command not found")
        print("   Try: source /etc/profile.d/modules.sh")
    
    # Test user-space directory creation
    print("\n📁 Testing user-space directory creation:")
    test_socket_dir = os.path.expanduser("~/.xpra-sockets-test")
    try:
        os.makedirs(test_socket_dir, exist_ok=True)
        print(f"✅ Can create socket directory: {test_socket_dir}")
        
        # Test if we can write to it
        test_file = os.path.join(test_socket_dir, "test")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✅ Socket directory is writable")
        
        # Clean up
        os.rmdir(test_socket_dir)
        
    except Exception as e:
        print(f"❌ Cannot create user-space socket directory: {e}")
        return False
    
    # Test port binding capability
    print("\n🔌 Testing port binding:")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 0))  # Bind to any available port
        port = sock.getsockname()[1]
        sock.close()
        print(f"✅ Can bind to local ports (tested port {port})")
    except Exception as e:
        print(f"❌ Cannot bind to local ports: {e}")
        return False
    
    # Check compute resources
    print("\n💻 Checking compute resources:")
    try:
        import psutil
        
        # Memory
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        print(f"✅ Available memory: {memory_gb:.1f} GB")
        
        if memory_gb < 2:
            print("⚠️  Low memory - Firefox may struggle")
        
        # CPU
        cpu_count = psutil.cpu_count()
        print(f"✅ CPU cores: {cpu_count}")
        
        if cpu_count < 2:
            print("⚠️  Single core - may impact performance")
            
    except ImportError:
        print("ℹ️  psutil not available - cannot check resources")
    except Exception as e:
        print(f"⚠️  Resource check failed: {e}")
    
    print("\n📋 SlurmSpawner recommendations:")
    print("   1. Ensure Firefox and Xpra modules are loaded in job script")
    print("   2. Request adequate memory (≥4GB recommended)")
    print("   3. Consider requesting ≥2 CPU cores for better performance")
    print("   4. Verify network access to compute nodes from hub")
    
    return True


def main():
    """Main installation and test procedure"""
    print("Firefox Launcher Installation Script")
    print("===================================")
    
    # Check we're in the right directory
    if not os.path.exists('pyproject.toml'):
        print("❌ Please run this script from the extension directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing system dependencies. Please install them first.")
        sys.exit(1)
    
    # Install extension
    if not install_extension():
        print("\n❌ Extension installation failed")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("\n❌ Extension testing failed")
        sys.exit(1)
    
    # Test SlurmSpawner environment if applicable
    if not test_slurm_environment():
        print("\n❌ SlurmSpawner environment test failed")
        sys.exit(1)
    
    print("\n🎉 Installation completed successfully!")
    print("\nNext steps:")
    print("1. Start JupyterLab: jupyter lab")
    print("2. Look for 'Firefox Browser' in the Launcher")
    print("3. Click it to start a Firefox session via Xpra")
    
    # SlurmSpawner specific guidance
    slurm_vars = [os.environ.get('SLURM_JOB_ID'), os.environ.get('SLURM_PROCID'), os.environ.get('SLURM_NODEID')]
    if any(v is not None for v in slurm_vars):
        print("\n🎯 SlurmSpawner specific notes:")
        print("   - Firefox will run on the compute node")
        print("   - Session will be accessible via JupyterHub proxy")
        print("   - Make sure required modules are loaded in your job script")
    
    print("\nIf you encounter issues:")
    print("- Check that Xpra HTML5 support is installed")
    print("- Ensure Firefox is in your PATH")
    print("- Check the terminal output for error messages")

if __name__ == "__main__":
    main()
