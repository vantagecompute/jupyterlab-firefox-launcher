---
# Copyright (c) 2025 Vantage Compute Corporation.
layout: page
title: Architecture
permalink: /architecture/
---

# Architecture

The JupyterLab Firefox Launcher is built on a multi-tier architecture that seamlessly integrates Firefox browser capabilities into the JupyterLab environment. This document provides a comprehensive overview of the system architecture, component interactions, and data flow.

## System Overview

The extension consists of several interconnected components that work together to provide seamless Firefox integration:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   JupyterLab    │    │   Server-Side    │    │     Firefox     │
│   Frontend      │    │    Extension     │    │    Process      │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │   Widget    │◄┼────┼─│ Launcher API │ │    │ │   Browser   │ │
│ │             │ │    │ │   Handler    │ │    │ │   Instance  │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │  Launcher   │ │    │ │  Xpra Client │◄┼────┼─│    Xpra     │ │
│ │   Button    │ │    │ │   Handler    │ │    │ │   Server    │ │
│ └─────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
└─────────────────┘    │ ┌──────────────┐ │    └─────────────────┘
        │              │ │ Xpra Proxy & │ │            │
        │              │ │ WebSocket    │ │            │
        │              │ │  Handlers    │ │            │
        │              │ └──────────────┘ │            │
        │              │ ┌──────────────┐ │            │
        │              │ │Static & Auth │ │            │
        │              │ │   Bypass     │ │            │
        │              │ └──────────────┘ │            │
        │              └──────────────────┘            │
        │                        │                     │
        └────────── HTTP API ────┼──── TCP/WebSocket ──┘
                                 │
                    ┌──────────────────┐
                    │   Session        │
                    │   Management     │
                    │                  │
                    │ ┌──────────────┐ │
                    │ │   Profile    │ │
                    │ │   Isolation  │ │
                    │ └──────────────┘ │
                    └──────────────────┘
```

## Component Architecture

### Frontend Layer

#### 1. JupyterLab Widget System
The frontend is built using JupyterLab's widget system, providing native integration with the JupyterLab interface.

**Key Components:**
- **Firefox Widget**: Main widget that displays Firefox content
- **Launcher Integration**: Button integration in JupyterLab launcher
- **Lifecycle Management**: Handles widget creation, disposal, and cleanup

**Widget Lifecycle:**
```typescript
Widget Creation → Session Request → Process Tracking → Display → Cleanup
```

#### 2. Communication Layer
The frontend communicates with the backend through RESTful APIs:

**API Endpoints:**
- `POST /firefox-launcher/api/firefox` - Launch new session
- `GET /firefox-launcher/api/firefox?port={port}` - Session status and redirect
- `POST /firefox-launcher/api/cleanup` - Session cleanup
- `GET /firefox-launcher/client` - Xpra HTML5 client interface
- `GET /firefox-launcher/proxy` - Xpra server proxy with CSP bypass
- `WebSocket /firefox-launcher/ws` - WebSocket proxy for Xpra
- `GET /firefox-launcher/{path}` - Static file handler with auth bypass

### Backend Layer

#### 1. Server Extension (`server_extension.py`)
Registers HTTP handlers with the Jupyter server and manages the extension lifecycle.

**Responsibilities:**
- Handler registration and routing
- Extension configuration management
- Integration with Jupyter server lifecycle

#### 2. Firefox Handler (`firefox_handler.py`)
Core backend component that manages Firefox sessions and processes through multiple specialized handlers.

**Handler Classes:**

**FirefoxLauncherHandler**
- Primary session launch and management
- Process lifecycle control
- Session isolation and directory management
- JupyterHub proxy registration support

**XpraClientHandler**
- Serves custom Xpra HTML5 client templates
- Handles client configuration and URL parameters
- Provides browser interface for Firefox sessions

**XpraProxyHandler** 
- Proxies HTTP requests to Xpra servers
- Strips CSP headers for iframe compatibility
- Handles authentication bypass for proxy requests

**XpraWebSocketHandler**
- WebSocket proxy for real-time Xpra communication
- Bi-directional message forwarding
- Connection lifecycle management

**XpraStaticHandler**
- Serves static files from Xpra servers
- Authentication bypass for static assets
- HEAD method support for asset verification

**FirefoxCleanupHandler**
- Session cleanup and resource management
- Process termination and directory cleanup
- Bulk cleanup operations

**Key Features:**
- Multi-handler architecture for separation of concerns
- Process lifecycle control and monitoring
- Session isolation with dedicated directories
- Resource cleanup and management
- Error handling and comprehensive logging
- JupyterHub and standalone JupyterLab support

**Session Management Flow:**
```python
Session Request → Port Allocation → Directory Creation → 
Xpra Process Launch → JupyterHub Proxy Registration → 
Client Template Serving → Session Tracking
```

#### 3. Server Extension (`server_extension.py`)
Registers HTTP handlers with the Jupyter server and manages extension lifecycle.

**Handler Registration Pattern:**
```python
handlers = [
    (firefox_launcher_pattern + r"/?(?:\?.*)?$", FirefoxLauncherHandler),
    (firefox_cleanup_pattern + r"/?(?:\?.*)?$", FirefoxCleanupHandler),
    (xpra_client_pattern + r"/?(?:\?.*)?$", XpraClientHandler),
    (xpra_proxy_pattern + r"/?(?:\?.*)?$", XpraProxyHandler),
    (xpra_ws_pattern + r"/?(?:\?.*)?$", XpraWebSocketHandler),
    (xpra_static_pattern, XpraStaticHandler),  # Must be last (catch-all)
]
```

**Responsibilities:**
- Multi-handler registration and routing
- URL pattern management with query parameter support
- Extension configuration management
- Integration with Jupyter server lifecycle
- jupyter-server-proxy integration when available

### System Layer

#### 1. Xpra Remote Display Server
Xpra provides high-performance remote display capabilities for Firefox sessions.

**Xpra Configuration:**
- TCP binding for web access
- HTML5 client support
- Session-specific display management
- Clipboard integration
- Performance optimization

**Xpra Command Structure:**
```bash
xpra start --bind-tcp=0.0.0.0:PORT --html=on --daemon=no 
     --start-child=firefox-xstartup --session-name=Firefox-Session-PORT
```

#### 2. Firefox Process Management
Each Firefox session runs as an independent process with isolated resources.

**Process Architecture:**
```
Xpra Server (Parent)
└── Firefox Process (Child)
    ├── Session Directory
    ├── Profile Directory  
    ├── Cache Directory
    └── Runtime Directory
```

#### 3. Session Isolation System
Complete isolation between sessions using dedicated directory structures.

**Session Directory Structure:**
```
~/.firefox-launcher/sessions/session-{port}/
├── profile/          # Firefox profile data
├── cache/           # Browser cache
├── temp/            # Temporary files
├── runtime/         # X11 and runtime files
└── sockets/         # IPC sockets
```

## Data Flow

### 1. Session Creation Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant LauncherAPI
    participant XpraClient
    participant XpraServer
    participant Firefox

    User->>Frontend: Click Firefox Launcher
    Frontend->>LauncherAPI: POST /firefox-launcher/api/firefox
    LauncherAPI->>LauncherAPI: Allocate Port
    LauncherAPI->>LauncherAPI: Create Session Directory
    LauncherAPI->>XpraServer: Start Xpra Server Process
    XpraServer->>Firefox: Launch Firefox Process
    LauncherAPI->>LauncherAPI: Register JupyterHub Proxy (if available)
    LauncherAPI->>Frontend: Return Session Info + Client URL
    Frontend->>XpraClient: GET /firefox-launcher/client?port={port}
    XpraClient->>Frontend: Return HTML5 Client Interface
    Frontend->>User: Display Firefox in Tab
```

### 2. User Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant XpraClient
    participant XpraProxy
    participant XpraWS
    participant XpraServer
    participant Firefox

    User->>Browser: Interact with Firefox Widget
    Browser->>XpraClient: Load HTML5 Client Interface
    XpraClient->>XpraWS: WebSocket /firefox-launcher/ws?port={port}
    XpraWS->>XpraServer: Forward WebSocket Messages
    XpraServer->>Firefox: Process User Input
    Firefox->>XpraServer: Return Display Updates
    XpraServer->>XpraWS: Forward Display Data
    XpraWS->>Browser: Stream Display Updates
    
    Note over XpraProxy: HTTP requests for static assets
    Browser->>XpraProxy: GET /firefox-launcher/proxy?port={port}&path={resource}
    XpraProxy->>XpraServer: Forward with CSP bypass
    XpraServer->>XpraProxy: Return Resource
    XpraProxy->>Browser: Serve with Modified Headers
```

### 3. Cleanup Flow

```mermaid
sequenceDiagram
    participant Frontend
    participant CleanupAPI
    participant LauncherAPI
    participant XpraServer
    participant Firefox
    participant Filesystem

    Frontend->>CleanupAPI: POST /firefox-launcher/api/cleanup
    CleanupAPI->>CleanupAPI: Identify Target Processes
    CleanupAPI->>XpraServer: Terminate Xpra Process
    XpraServer->>Firefox: Terminate Firefox Process
    CleanupAPI->>Filesystem: Clean Session Directory
    CleanupAPI->>LauncherAPI: Update Session Tracking
    CleanupAPI->>Frontend: Confirm Cleanup Complete
    
    Note over CleanupAPI: Supports bulk cleanup
    Frontend->>CleanupAPI: POST /cleanup (no process_id)
    CleanupAPI->>CleanupAPI: Clean All Sessions
```
    participant Filesystem

    Frontend->>Backend: POST /cleanup (process_id)
    Backend->>Firefox: Terminate Process
    Backend->>Xpra: Terminate Xpra Server
    Backend->>Filesystem: Clean Session Directory
    Backend->>Backend: Update Session Tracking
    Backend->>Frontend: Confirm Cleanup
```

## Security Architecture

### 1. Session Isolation
Each Firefox session is completely isolated from others:

**Process Isolation:**
- Separate system processes
- Independent memory spaces
- Isolated file systems
- Dedicated network namespaces

**Data Isolation:**
- Session-specific directories
- Independent Firefox profiles
- Separate cache and temporary files
- Isolated runtime environments

### 2. Access Control
Multiple layers of access control ensure security:

**Authentication:**
- JupyterLab authentication required
- XSRF protection for user actions
- Session-specific access tokens

**Authorization:**
- User can only access their own sessions
- Process ownership validation
- Directory permission controls

### 3. Resource Management
Proper resource management prevents abuse:

**Resource Limits:**
- Memory usage monitoring
- Process count limitations
- Session timeout controls
- Automatic cleanup mechanisms

## Performance Architecture

### 1. Display Optimization
Xpra provides optimized remote display performance:

**Compression:**
- Configurable compression algorithms
- Adaptive quality adjustment
- Bandwidth optimization
- Frame rate control

**Caching:**
- Client-side display caching
- Partial screen updates
- Mouse cursor optimization
- Clipboard synchronization

### 2. Resource Efficiency
Efficient resource usage across all components:

**Memory Management:**
- Session-specific memory allocation
- Garbage collection optimization
- Resource pooling where applicable
- Automatic cleanup mechanisms

**Process Management:**
- Minimal process overhead
- Efficient process communication
- Resource sharing optimization
- Graceful process termination

## Scalability Considerations

### 1. Multi-User Support
The architecture supports multiple concurrent users:

**User Isolation:**
- Per-user session directories
- Independent process trees
- Isolated resource allocation
- User-specific cleanup

### 2. Resource Scaling
The system can scale based on resource availability:

**Horizontal Scaling:**
- Multiple JupyterLab instances
- Load balancing support
- Distributed session management
- Cross-instance cleanup

**Vertical Scaling:**
- Memory usage optimization
- CPU usage monitoring
- Storage management
- Network bandwidth control

## Error Handling Architecture

### 1. Fault Tolerance
Robust error handling at all levels:

**Process Failures:**
- Automatic process restart
- Graceful degradation
- Error logging and monitoring
- User notification systems

**Network Failures:**
- Connection retry mechanisms
- Timeout handling
- Fallback strategies
- State recovery

### 2. Monitoring and Logging
Comprehensive monitoring and logging:

**System Monitoring:**
- Process health checks
- Resource usage monitoring
- Performance metrics
- Error rate tracking

**Logging Strategy:**
- Structured logging format
- Multiple log levels
- Debug mode support
- Log rotation and cleanup

## Next Steps

- **[Installation Guide]({{ site.baseurl }}/installation)**: Learn how to install and configure the extension
- **[Development Guide]({{ site.baseurl }}/development)**: Set up a development environment
- **[API Reference]({{ site.baseurl }}/api-reference)**: Detailed API documentation
- **[Troubleshooting]({{ site.baseurl }}/troubleshooting)**: Common issues and solutions
