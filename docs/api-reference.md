---
# Copyright (c) 2025 Vantage Compute Corporation.
layout: page
title: API Reference
permalink: /api-reference/
---

# API Reference

Complete API documentation for the JupyterLab Firefox Launcher extension.

## Server Extension API

### HTTP Endpoints

The server extension provides REST API endpoints for managing Firefox sessions.

#### Launch Session

**POST** `/firefox-launcher/api/firefox`

Launch a new Firefox session.

**Request Body:**
```json
{
  "url": "https://example.com"
}
```

**Parameters:**
- `url` (string, optional): URL to open in Firefox. Defaults to `about:blank`

**Response:**
```json
{
  "success": true,
  "port": 43051,
  "session_id": "Firefox-Session-43051",
  "url": "/firefox-launcher/client?port=43051",
  "message": "Firefox session launched successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message",
  "details": "Detailed error information"
}
```

#### Get Session Status / Redirect

**GET** `/firefox-launcher/api/firefox?port={port}`

Get session status or redirect to the Firefox client.

**Parameters:**
- `port` (integer): Port number of the Firefox session

**Response:**
- **302 Redirect**: Redirects to the Firefox client interface
- **404 Not Found**: If session doesn't exist

#### Cleanup Session

**POST** `/firefox-launcher/api/cleanup`

Clean up Firefox sessions.

**Request Body:**
```json
{
  "process_id": 12345
}
```

**Parameters:**
- `process_id` (integer, optional): Specific process ID to clean up. If not provided, cleans all sessions.

**Response:**
```json
{
  "success": true,
  "message": "Cleanup completed successfully",
  "processes_terminated": 3
}
```

#### Get Xpra Client

**GET** `/firefox-launcher/client?port={port}&httpUrl={url}&websocketUrl={ws_url}`

Get the custom Xpra HTML5 client interface.

**Parameters:**
- `port` (integer): Port number of the Xpra server
- `httpUrl` (string, optional): HTTP URL for the Xpra server
- `websocketUrl` (string, optional): WebSocket URL for the Xpra server

**Response:**
- **200 OK**: Returns HTML5 Xpra client interface
- **404 Not Found**: If client template is not available

#### Proxy Xpra Content

**GET** `/firefox-launcher/proxy?port={port}&path={path}`

Proxy requests to the Xpra server with CSP header modifications.

**Parameters:**
- `port` (integer): Port number of the Xpra server  
- `path` (string, optional): Path to proxy to the Xpra server

**WebSocket Proxy**

**WebSocket** `/firefox-launcher/ws?port={port}`

WebSocket proxy for Xpra connections.

**Parameters:**
- `port` (integer): Port number of the Xpra server

#### Static File Handler

**GET** `/firefox-launcher/{path}`

Serve static files from the Xpra server with authentication bypass.

**Parameters:**
- `path` (string): Path to the static file on the Xpra server

**Response:**
```json
{
  "session_id": "session_abc123",
  "status": "running",
  "port": 6080,
  "pid": 12345,
  "created_at": "2024-12-19T10:30:00Z",
  "uptime": 3600
}
```

## Python API

The extension provides handler classes that can be extended or integrated:

### Handler Classes

#### FirefoxLauncherHandler
Main request handler for session launch and management.

```python
from jupyterlab_firefox_launcher.firefox_handler import FirefoxLauncherHandler
```

**Methods:**
- `async post(self)`: Handle session launch requests
- `async get(self)`: Handle session status/redirect requests

#### XpraClientHandler
Serves the custom Xpra HTML5 client interface.

```python
from jupyterlab_firefox_launcher.firefox_handler import XpraClientHandler
```

#### XpraProxyHandler
Proxies HTTP requests to Xpra servers with CSP modifications.

```python
from jupyterlab_firefox_launcher.firefox_handler import XpraProxyHandler
```

#### XpraWebSocketHandler
WebSocket proxy for real-time Xpra communication.

```python
from jupyterlab_firefox_launcher.firefox_handler import XpraWebSocketHandler
```

#### XpraStaticHandler
Serves static files with authentication bypass.

```python
from jupyterlab_firefox_launcher.firefox_handler import XpraStaticHandler
```

#### FirefoxCleanupHandler
Handles session cleanup and resource management.

```python
from jupyterlab_firefox_launcher.firefox_handler import FirefoxCleanupHandler
```

**Methods:**
- `async post(self)`: Handle cleanup requests

### Environment Detection
```python
from jupyterlab_firefox_launcher.firefox_handler import _detect_environment

env = _detect_environment()  # Returns 'jupyterhub', 'jupyterlab', or 'unknown'
```

## Frontend Integration

The frontend integrates with JupyterLab's plugin system and communicates with the backend via HTTP APIs.

### JupyterLab Plugin Integration

The extension is registered as a JupyterLab plugin that:
- Adds a Firefox launcher button to the JupyterLab launcher
- Handles session creation and management through HTTP APIs
- Manages widget lifecycle and cleanup
- Provides user feedback and error handling

### API Communication

The frontend communicates with the backend handlers via:
- **Session Launch**: `POST /firefox-launcher/api/firefox`
- **Session Cleanup**: `POST /firefox-launcher/api/cleanup`
- **Client Interface**: Direct navigation to `/firefox-launcher/client?port={port}`

### Widget Lifecycle

1. User clicks Firefox launcher button
2. Frontend makes API call to launch session
3. Backend returns session information and client URL
4. Frontend navigates to Xpra HTML5 client
5. Session runs until user closes or cleanup occurs

## Configuration

### Environment Variables

Configure behavior via environment variables:

```bash
# Enable debug logging
export FIREFOX_LAUNCHER_DEBUG=1

# Development override for firefox-xstartup script
export DEV_FIREFOX_LAUNCHER_PATH=/path/to/custom/script

# JupyterHub integration settings (set automatically by JupyterHub)
export JUPYTERHUB_SERVICE_PREFIX=/user/username/
export CONFIGPROXY_API_URL=http://localhost:8001/api/routes
export CONFIGPROXY_AUTH_TOKEN=secret-token
```

### JupyterLab Configuration

The extension integrates automatically with JupyterLab. Server extension settings can be configured in `jupyter_server_config.py`:

```python
# jupyter_server_config.py
c.ServerApp.jpserver_extensions = {
    'jupyterlab_firefox_launcher': True
}
```

### Xpra Configuration

The extension uses optimized Xpra settings for performance:

```bash
# Automatically configured by the extension:
--compressors=none 
--quality=100 
--encoding=auto
--min-quality=30 
--min-speed=30
--auto-refresh-delay=0.15
--html=on
--bind-tcp=0.0.0.0:{port}
```

## Error Handling

### Error Response Format

All API endpoints return structured error responses:

```json
{
  "success": false,
  "error": "Error type description",
  "details": "Detailed error message for debugging"
}
```

### Common Error Types

#### Session Launch Failures
- **Port allocation errors**: No available ports
- **Process launch failures**: Xpra or Firefox startup issues  
- **Directory creation errors**: Filesystem permission issues
- **System resource limits**: Insufficient memory or processes

#### Session Access Errors
- **Session not found**: Invalid or expired session
- **Connection failures**: Network or proxy issues
- **Authentication errors**: JupyterLab security validation

#### Cleanup Errors
- **Process termination issues**: Stuck or unresponsive processes
- **Directory cleanup failures**: Filesystem permission issues

### Error Logging

Enable debug logging for detailed error information:

```bash
export FIREFOX_LAUNCHER_DEBUG=1
jupyter lab --log-level=DEBUG
```

## Debugging

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Via environment variable
export FIREFOX_LAUNCHER_DEBUG=1
jupyter lab --log-level=DEBUG
```

### Process Monitoring

Monitor active Firefox sessions:

```bash
# Check for running Xpra processes
ps aux | grep xpra

# Check session directories
ls -la ~/.firefox-launcher/sessions/

# Monitor resource usage
htop | grep firefox
```

### Network Debugging

```bash
# Check active ports
netstat -tulpn | grep -E "(43051|8000)"

# Test Xpra server directly
curl http://localhost:43051/

# Check WebSocket connections
ss -tulpn | grep :43051
```

Returns:
```python
{
  'version': '0.9.10',
  'sessions': {...},
  'system_info': {...},
  'configuration': {...}
}
```

## Performance

### Session Limits

- **Maximum concurrent sessions**: 10 (configurable)
- **Session timeout**: 1 hour (configurable)  
- **Cleanup interval**: 5 minutes (configurable)

### Resource Usage

Each Firefox session consumes:
- **Memory**: ~200-500MB per session
- **CPU**: Varies based on web content
- **Disk**: ~10-50MB per session directory

### Optimization Tips

1. **Limit concurrent sessions** to available system resources
2. **Use appropriate Xpra settings** (already optimized in extension)
3. **Set reasonable timeouts** to prevent resource leaks
4. **Monitor session usage** via the cleanup API
5. **Clean up unused sessions** regularly

## Security

### Access Control

Sessions are isolated by:
- **Process separation**: Each session runs in separate process
- **Directory isolation**: Separate profile directories per session
- **Port isolation**: Unique ports per session
- **Authentication integration**: JupyterLab's security model

### Network Security

- Xpra servers bind to localhost only
- No external network access by default
- HTTPS support via JupyterLab configuration
- CSP header management for iframe compatibility

### Data Protection

- Session directories are temporary and isolated
- Automatic cleanup on session termination
- No persistent storage of browsing data
- Authentication bypass only for approved static resources

For more security considerations, see the [Security Documentation]({{ site.baseurl }}/security).

## Changelog

### Version 0.9.10

- Multi-handler architecture implementation
- Xpra-based remote display (replaces VNC)
- JupyterHub proxy integration
- Authentication bypass for static files
- WebSocket proxy support
- Comprehensive session isolation
- JupyterLab 4.4.5+ support

### Roadmap

- **0.9.11**: Performance optimizations and bug fixes
- **0.10.0**: Enhanced session persistence and recovery
- **1.0.0**: Production-ready stable release

For complete version history, see [CHANGELOG.md](https://github.com/vantagecompute/jupyterlab-firefox-launcher/blob/main/CHANGELOG.md).
