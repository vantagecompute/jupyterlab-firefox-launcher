// Copyright (c) 2025 Vantage Compute Corporation.

/**
 * Xpra Client Integration for JupyterLab Firefox Launcher
 * 
 * This module provides a TypeScript wrapper around the xpra-html5-client
 * library for seamless integration with our JupyterLab extension.
 */

import { XpraClient, XpraConnectionOptions } from 'xpra-html5-client';

export interface FirefoxXpraClientOptions {
  container: HTMLElement;
  wsUrl: string;
  httpUrl?: string;
  autoConnect?: boolean;
  debug?: boolean;
}

export class FirefoxXpraClient {
  private client: XpraClient;
  private container: HTMLElement;
  private wsUrl: string;
  private httpUrl?: string;
  private debug: boolean;
  private isConnected: boolean = false;

  constructor(options: FirefoxXpraClientOptions) {
    this.container = options.container;
    this.wsUrl = options.wsUrl;
    this.httpUrl = options.httpUrl;
    this.debug = options.debug || false;

    // Initialize the Xpra client with better configuration
    this.client = new XpraClient({
      // Configure workers for better performance
      worker: undefined, // Let the library handle worker creation
      decoder: undefined // Let the library handle decoder creation
    });

    this.setupEventHandlers();

    if (options.autoConnect !== false) {
      this.connect();
    }
  }

  private setupEventHandlers(): void {
    // Connection events
    this.client.on('connect', (status) => {
      console.log(`🔗 Xpra connected: ${status}`);
      this.isConnected = status === 'connected';
    });

    this.client.on('disconnect', (status) => {
      console.log(`🔌 Xpra disconnected: ${status}`);
      this.isConnected = false;
    });

    // Additional event handlers can be added here when we know the correct event names
    // For now, we'll handle basic connection events
  }

  private createWindowElement(win: any): void {
    // Create DOM element for the Xpra window
    const windowDiv = document.createElement('div');
    windowDiv.id = `xpra-window-${win.wid}`;
    windowDiv.className = 'xpra-window';
    windowDiv.style.cssText = `
      position: absolute;
      left: ${win.x}px;
      top: ${win.y}px;
      width: ${win.w}px;
      height: ${win.h}px;
      border: 1px solid #ccc;
      background: #fff;
    `;

    // Create canvas for window content
    const canvas = document.createElement('canvas');
    canvas.width = win.w;
    canvas.height = win.h;
    canvas.style.cssText = `
      width: 100%;
      height: 100%;
      display: block;
    `;

    windowDiv.appendChild(canvas);
    this.container.appendChild(windowDiv);
  }

  private removeWindowElement(wid: number): void {
    const windowElement = document.getElementById(`xpra-window-${wid}`);
    if (windowElement) {
      windowElement.remove();
    }
  }

  private handleDraw(draw: any): void {
    // Handle drawing operations on the canvas
    const windowElement = document.getElementById(`xpra-window-${draw.wid}`);
    if (!windowElement) return;

    const canvas = windowElement.querySelector('canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Apply the drawing data to the canvas
    // This is a simplified implementation - the actual drawing logic
    // would depend on the specific draw data format
    if (draw.buffer) {
      ctx.drawImage(draw.buffer, draw.x, draw.y);
    }
  }

  async connect(): Promise<void> {
    try {
      // Initialize the client
      await this.client.init();

      // Parse the original Xpra WebSocket URL
      const originalUrl = new URL(this.wsUrl);
      console.log(`🔧 Original WebSocket URL: ${this.wsUrl}`);
      console.log(`🔧 Parsed - protocol: ${originalUrl.protocol}, hostname: ${originalUrl.hostname}, port: ${originalUrl.port}`);
      
      // Get the clean host and port for the target Xpra server
      let xpraHost = originalUrl.hostname;
      let xpraPort = originalUrl.port ? parseInt(originalUrl.port) : (originalUrl.protocol === 'wss:' ? 443 : 80);
      
      // Convert localhost to 127.0.0.1 for better compatibility
      if (xpraHost === 'localhost') {
        xpraHost = '127.0.0.1';
        console.log(`🔧 Converting localhost to 127.0.0.1 for WebSocket compatibility`);
      }

      // Construct the proxy WebSocket URL that goes through JupyterHub
      // Instead of connecting directly to ws://127.0.0.1:44613/
      // We connect to ws://raton00:8889/user/bdx/firefox-launcher/ws?host=127.0.0.1&port=44613
      const currentLocation = window.location;
      const proxyProtocol = currentLocation.protocol === 'https:' ? 'wss:' : 'ws:';
      const proxyUrl = `${proxyProtocol}//${currentLocation.host}${currentLocation.pathname.replace('/lab', '')}/firefox-launcher/ws?host=${xpraHost}&port=${xpraPort}`;
      
      console.log(`🔧 Using WebSocket proxy URL: ${proxyUrl}`);
      console.log(`🔧 Target Xpra server: ${xpraHost}:${xpraPort}`);

      // Connection options
      const options: Partial<XpraConnectionOptions> = {
        ssl: proxyProtocol === 'wss:',
        reconnect: true,
        reconnectAttempts: 3,
        reconnectInterval: 5000,
        connectionTimeout: 30000,
      };

      console.log(`🔗 Connecting through proxy to Xpra server at: ${xpraHost}:${xpraPort}`);
      console.log(`🔗 SSL enabled: ${options.ssl}`);
      console.log(`🔗 Binary subprotocol will be handled by WebSocket proxy`);
      
      // SOLUTION: Override WebSocket creation to use our proxy URL
      // but make it appear as a simple connection to xpra-html5-client
      
      // Save the original WebSocket constructor
      const OriginalWebSocket = window.WebSocket;
      
      // Create a custom WebSocket class that redirects to our proxy
      class ProxyWebSocket extends OriginalWebSocket {
        constructor(url: string | URL, protocols?: string | string[]) {
          const urlString = url.toString();
          
          // If this is an Xpra connection (contains our target host/port), redirect to proxy
          if (urlString.includes(xpraHost) && urlString.includes(xpraPort.toString())) {
            console.log(`🔀 Intercepting Xpra WebSocket connection to: ${urlString}`);
            console.log(`🔀 Redirecting to JupyterHub proxy: ${proxyUrl}`);
            
            // Use our proxy URL but keep the binary protocol
            super(proxyUrl, protocols || ['binary']);
          } else {
            // For other WebSockets, use original behavior
            super(url, protocols);
          }
        }
      }
      
      // Temporarily replace WebSocket with our proxy version
      (window as any).WebSocket = ProxyWebSocket;
      
      // Now connect using the original WebSocket URL - our ProxyWebSocket will intercept and redirect
      this.client.connect(this.wsUrl, options);
      
      // Restore original WebSocket after connection attempt (give it time to establish)
      setTimeout(() => {
        (window as any).WebSocket = OriginalWebSocket;
        console.log(`🔄 Restored original WebSocket constructor`);
      }, 5000);

    } catch (error) {
      console.error('Failed to connect to Xpra server:', error);
      throw error;
    }
  }

  disconnect(): void {
    if (this.isConnected) {
      this.client.disconnect();
    }
  }

  isClientConnected(): boolean {
    return this.isConnected;
  }

  getClient(): XpraClient {
    return this.client;
  }

  // Cleanup method
  destroy(): void {
    this.disconnect();
    
    // Remove all window elements
    const windows = this.container.querySelectorAll('.xpra-window');
    windows.forEach(window => window.remove());
  }
}

export default FirefoxXpraClient;
