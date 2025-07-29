---
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

**POST** `/jupyterlab-firefox-launcher/launch`

Launch a new Firefox session.

**Request Body:**
```json
{
  "url": "https://example.com",
  "quality": 80,
  "dpi": 96
}
```

**Parameters:**
- `url` (string, optional): URL to open in Firefox. Defaults to `about:blank`
- `quality` (integer, optional): Video quality 1-100. Defaults to `80`
- `dpi` (integer, optional): Display DPI 50-200. Defaults to `96`

**Response:**
```json
{
  "success": true,
  "port": 6080,
  "session_id": "session_abc123",
  "url": "http://localhost:6080/vnc.html",
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

#### Delete Session

**DELETE** `/jupyterlab-firefox-launcher/sessions/{session_id}`

Delete a specific Firefox session.

**Parameters:**
- `session_id` (string): ID of the session to delete

**Response:**
```json
{
  "success": true,
  "message": "Session deleted successfully"
}
```

#### List Sessions

**GET** `/jupyterlab-firefox-launcher/sessions`

Get information about all active sessions.

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "session_abc123",
      "port": 6080,
      "pid": 12345,
      "created_at": "2024-12-19T10:30:00Z",
      "status": "running"
    }
  ],
  "count": 1
}
```

#### Session Status

**GET** `/jupyterlab-firefox-launcher/sessions/{session_id}/status`

Get status of a specific session.

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

### Python API

#### FirefoxLauncherHandler

Main request handler for the server extension.

```python
from jupyterlab_firefox_launcher.firefox_handler import FirefoxLauncherHandler

class FirefoxLauncherHandler(tornado.web.RequestHandler):
    """Main handler for Firefox launcher requests."""
```

##### Methods

**async post(self)**
Handle POST requests to launch new Firefox sessions.

**async delete(self, session_id: str)**
Handle DELETE requests to terminate sessions.

**async get(self, session_id: str = None)**
Handle GET requests for session information.

#### FirefoxCleanupHandler

Automatic cleanup handler for terminated sessions.

```python
from jupyterlab_firefox_launcher.firefox_handler import FirefoxCleanupHandler

class FirefoxCleanupHandler:
    """Handles automatic cleanup of terminated Firefox sessions."""
```

##### Methods

**cleanup_sessions()**
Scan for and clean up terminated sessions.

**is_process_running(pid: int) -> bool**
Check if a process is still running.

**cleanup_session_directory(session_dir: Path)**
Remove session directory and files.

#### Utility Functions

**get_available_port() -> int**
Find an available port for VNC server.

```python
from jupyterlab_firefox_launcher.firefox_handler import get_available_port

port = get_available_port()
print(f"Available port: {port}")
```

**create_session_directory(port: int) -> Path**
Create isolated session directory.

```python
from jupyterlab_firefox_launcher.firefox_handler import create_session_directory

session_dir = create_session_directory(6080)
print(f"Session directory: {session_dir}")
```

**launch_firefox_session(port: int, url: str, quality: int, dpi: int) -> dict**
Launch Firefox with VNC server.

```python
from jupyterlab_firefox_launcher.firefox_handler import launch_firefox_session

result = launch_firefox_session(
    port=6080,
    url="https://example.com",
    quality=80,
    dpi=96
)
```

## Frontend API

### TypeScript Interfaces

#### ISessionInfo

Interface for session information.

```typescript
interface ISessionInfo {
  session_id: string;
  port: number;
  pid: number;
  created_at: string;
  status: 'running' | 'stopped' | 'error';
  uptime?: number;
}
```

#### ILaunchRequest

Interface for launch request parameters.

```typescript
interface ILaunchRequest {
  url?: string;
  quality?: number;
  dpi?: number;
}
```

#### ILaunchResponse

Interface for launch response.

```typescript
interface ILaunchResponse {
  success: boolean;
  port?: number;
  session_id?: string;
  url?: string;
  message?: string;
  error?: string;
  details?: string;
}
```

### Classes

#### FirefoxLauncherWidget

Main widget for the Firefox launcher interface.

```typescript
import { FirefoxLauncherWidget } from 'jupyterlab-firefox-launcher';

class FirefoxLauncherWidget extends Widget {
  constructor(options: FirefoxLauncherWidget.IOptions) {
    // Implementation
  }
}
```

##### Properties

- `sessions: Map<string, ISessionInfo>` - Active sessions
- `isLaunching: boolean` - Launch state indicator

##### Methods

**async launchSession(request: ILaunchRequest): Promise<ILaunchResponse>**
Launch a new Firefox session.

**async deleteSession(sessionId: string): Promise<void>**
Delete a specific session.

**async refreshSessions(): Promise<void>**
Refresh the list of active sessions.

**openSessionInNewTab(sessionId: string): void**
Open session VNC viewer in new browser tab.

#### FirefoxAPI

API client for communicating with the server extension.

```typescript
import { FirefoxAPI } from 'jupyterlab-firefox-launcher';

const api = new FirefoxAPI();
```

##### Methods

**async launch(request: ILaunchRequest): Promise<ILaunchResponse>**
Launch new session via API.

```typescript
const response = await api.launch({
  url: 'https://example.com',
  quality: 80,
  dpi: 96
});
```

**async deleteSessions(sessionId: string): Promise<void>**
Delete session via API.

```typescript
await api.deleteSession('session_abc123');
```

**async getSessions(): Promise<ISessionInfo[]>**
Get all active sessions.

```typescript
const sessions = await api.getSessions();
```

**async getSessionStatus(sessionId: string): Promise<ISessionInfo>**
Get specific session status.

```typescript
const status = await api.getSessionStatus('session_abc123');
```

### React Components

#### LaunchForm

Form component for launching new sessions.

```typescript
interface LaunchFormProps {
  onLaunch: (request: ILaunchRequest) => Promise<void>;
  isLaunching: boolean;
}

export const LaunchForm: React.FC<LaunchFormProps> = (props) => {
  // Implementation
};
```

#### SessionList

Component for displaying active sessions.

```typescript
interface SessionListProps {
  sessions: ISessionInfo[];
  onDelete: (sessionId: string) => Promise<void>;
  onOpen: (sessionId: string) => void;
  onRefresh: () => Promise<void>;
}

export const SessionList: React.FC<SessionListProps> = (props) => {
  // Implementation
};
```

#### SessionCard

Component for individual session display.

```typescript
interface SessionCardProps {
  session: ISessionInfo;
  onDelete: () => Promise<void>;
  onOpen: () => void;
}

export const SessionCard: React.FC<SessionCardProps> = (props) => {
  // Implementation
};
```

## Configuration API

### Server Configuration

Server extension can be configured via `jupyter_server_config.py`:

```python
# jupyter_server_config.py
c.ServerApp.jpserver_extensions = {
    'jupyterlab_firefox_launcher': True
}

# Custom configuration
c.FirefoxLauncherApp.cleanup_interval = 300  # seconds
c.FirefoxLauncherApp.max_sessions = 10
c.FirefoxLauncherApp.session_timeout = 3600  # seconds
c.FirefoxLauncherApp.default_quality = 80
c.FirefoxLauncherApp.default_dpi = 96
```

### Environment Variables

Configure behavior via environment variables:

```bash
# Enable debug logging
export FIREFOX_LAUNCHER_DEBUG=1

# Set session timeout (seconds)
export FIREFOX_LAUNCHER_TIMEOUT=3600

# Set maximum concurrent sessions
export FIREFOX_LAUNCHER_MAX_SESSIONS=5

# Set cleanup interval (seconds)
export FIREFOX_LAUNCHER_CLEANUP_INTERVAL=300

# Set default video quality (1-100)
export FIREFOX_LAUNCHER_DEFAULT_QUALITY=80

# Set default DPI (50-200)
export FIREFOX_LAUNCHER_DEFAULT_DPI=96
```

## Error Handling

### Error Types

#### LaunchError

Raised when Firefox session launch fails.

```python
from jupyterlab_firefox_launcher.exceptions import LaunchError

try:
    launch_firefox_session(port, url, quality, dpi)
except LaunchError as e:
    print(f"Launch failed: {e}")
```

#### SessionNotFoundError

Raised when requested session doesn't exist.

```python
from jupyterlab_firefox_launcher.exceptions import SessionNotFoundError

try:
    delete_session(session_id)
except SessionNotFoundError as e:
    print(f"Session not found: {e}")
```

#### PortUnavailableError

Raised when no ports are available.

```python
from jupyterlab_firefox_launcher.exceptions import PortUnavailableError

try:
    port = get_available_port()
except PortUnavailableError as e:
    print(f"No ports available: {e}")
```

### Error Responses

All API endpoints return structured error responses:

```json
{
  "success": false,
  "error": "Error type",
  "details": "Detailed error message",
  "code": "ERROR_CODE"
}
```

#### Error Codes

- `LAUNCH_FAILED`: Firefox session launch failed
- `SESSION_NOT_FOUND`: Requested session doesn't exist
- `PORT_UNAVAILABLE`: No available ports
- `INVALID_PARAMETERS`: Invalid request parameters
- `PERMISSION_DENIED`: Insufficient permissions
- `SYSTEM_ERROR`: System-level error

## Events

### Frontend Events

The frontend emits custom events for session management:

#### session-launched

Emitted when a new session is launched.

```typescript
document.addEventListener('session-launched', (event: CustomEvent) => {
  const session = event.detail.session;
  console.log('Session launched:', session);
});
```

#### session-deleted

Emitted when a session is deleted.

```typescript
document.addEventListener('session-deleted', (event: CustomEvent) => {
  const sessionId = event.detail.sessionId;
  console.log('Session deleted:', sessionId);
});
```

#### sessions-refreshed

Emitted when session list is refreshed.

```typescript
document.addEventListener('sessions-refreshed', (event: CustomEvent) => {
  const sessions = event.detail.sessions;
  console.log('Sessions refreshed:', sessions);
});
```

## Plugin System

### JupyterLab Plugin

The extension is implemented as a JupyterLab plugin:

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-firefox-launcher',
  autoStart: true,
  requires: [],
  optional: [],
  activate: (app: JupyterFrontEnd) => {
    // Plugin activation logic
  }
};

export default plugin;
```

### Extension Points

The plugin provides extension points for customization:

#### Custom Launch Handlers

```typescript
interface ILaunchHandler {
  canHandle(request: ILaunchRequest): boolean;
  handle(request: ILaunchRequest): Promise<ILaunchResponse>;
}

// Register custom handler
app.registerLaunchHandler(myCustomHandler);
```

#### Custom Session Renderers

```typescript
interface ISessionRenderer {
  canRender(session: ISessionInfo): boolean;
  render(session: ISessionInfo): Widget;
}

// Register custom renderer
app.registerSessionRenderer(myCustomRenderer);
```

## Debugging

### Debug Mode

Enable debug mode for detailed logging:

```python
# In Python
import logging
logging.getLogger('jupyterlab_firefox_launcher').setLevel(logging.DEBUG)
```

```bash
# Via environment variable
export FIREFOX_LAUNCHER_DEBUG=1
jupyter lab
```

### Debug Information

Access debug information via the API:

```python
from jupyterlab_firefox_launcher.debug import get_debug_info

debug_info = get_debug_info()
print(debug_info)
```

Returns:
```python
{
  'version': '0.1.0',
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
2. **Use appropriate quality settings** (lower quality = less bandwidth)
3. **Set reasonable timeouts** to prevent resource leaks
4. **Monitor session usage** via the sessions API
5. **Clean up unused sessions** regularly

## Security

### Access Control

Sessions are isolated by:
- **Process separation**: Each session runs in separate process
- **Directory isolation**: Separate profile directories
- **Port isolation**: Unique ports per session

### Network Security

- VNC servers bind to localhost only
- No external network access by default
- HTTPS support via JupyterLab configuration

### Data Protection

- Session directories are temporary
- Automatic cleanup on session termination
- No persistent storage of browsing data

For more security considerations, see the [Security Documentation]({{ site.baseurl }}/security).

## Changelog

### Version 0.1.0

- Initial release
- Basic Firefox session management
- VNC integration
- JupyterLab 4.0+ support

### Roadmap

- **0.2.0**: Session persistence and recovery
- **0.3.0**: Advanced configuration options
- **0.4.0**: Multi-browser support
- **1.0.0**: Production-ready stable release

For complete version history, see [CHANGELOG.md](https://github.com/vantagecompute/jupyterlab-firefox-launcher/blob/main/CHANGELOG.md).
