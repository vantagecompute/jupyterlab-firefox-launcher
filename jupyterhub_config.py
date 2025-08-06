"""
JupyterHub configuration for Firefox launcher with configurable-http-proxy integration.
"""

# Get configurable-http-proxy settings from current environment
# Let JupyterHub generate its own auth token instead of hardcoding it
configproxy_auth_token ='a1d186378e6cb9ac36342769de67fc0e7eb3d9ff2e9e5a89f93976a272658dfa'
configproxy_api_url = 'http://127.0.0.1:8001'




# Configure the proxy to use configurable-http-proxy
c.JupyterHub.proxy_class = 'jupyterhub.proxy.ConfigurableHTTPProxy'

# Set JupyterHub to listen on port 8889
c.JupyterHub.port = 8889

# Enable debug logging for proxy operations
c.JupyterHub.log_level = 'DEBUG'
c.ConfigurableHTTPProxy.debug = True
c.ConfigurableHTTPProxy.auth_token = configproxy_auth_token
c.ConfigurableHTTPProxy.api_url = configproxy_api_url
c.Authenticator.allow_all = True


c.Spawner.environment = {
    'CONFIGPROXY_API_URL': configproxy_api_url,
    'CONFIGPROXY_AUTH_TOKEN': configproxy_auth_token,
    # Don't set CONFIGPROXY_AUTH_TOKEN here - let JupyterHub manage it dynamically
}

print(f"🔧 JupyterHub config: Forwarding CONFIGPROXY_API_URL={configproxy_api_url}")
print(f"🔧 JupyterHub config: Forwarding CONFIGPROXY_AUTH_TOKEN={'[SET]' if configproxy_auth_token else '[NOT SET]'}")
