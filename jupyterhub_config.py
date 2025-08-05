"""
JupyterHub configuration for Firefox launcher with configurable-http-proxy integration.
"""


# Use environment variable expansion for the spawner
import os

# Get configurable-http-proxy settings from current environment
configproxy_api_url = os.environ.get('CONFIGPROXY_API_URL', 'http://127.0.0.1:8001')
configproxy_auth_token = os.environ.get('CONFIGPROXY_AUTH_TOKEN', 'a1d186378e6cb9ac36342769de67fc0e7eb3d9ff2e9e5a89f93976a272658dfa')

# Set up environment for spawned servers
c.Spawner.environment = {
    'CONFIGPROXY_API_URL': configproxy_api_url,
    'CONFIGPROXY_AUTH_TOKEN': configproxy_auth_token,
}

# Configure the proxy to use configurable-http-proxy
c.JupyterHub.proxy_class = 'jupyterhub.proxy.ConfigurableHTTPProxy'

# Set JupyterHub to listen on port 8889
c.JupyterHub.port = 8889

# Enable debug logging for proxy operations
c.JupyterHub.log_level = 'DEBUG'
c.ConfigurableHTTPProxy.debug = True

print(f"🔧 JupyterHub config: Forwarding CONFIGPROXY_API_URL={configproxy_api_url}")
print(f"🔧 JupyterHub config: Forwarding CONFIGPROXY_AUTH_TOKEN={'[SET]' if configproxy_auth_token else '[NOT SET]'}")
